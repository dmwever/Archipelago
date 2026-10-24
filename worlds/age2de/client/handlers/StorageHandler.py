import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .FolderHandler import FolderHandler

from ...generation import Identity

logger = logging.getLogger("Client")

APDATA_SUBPATH = "APData"
STATE_STEM = "state"


@dataclass(frozen=True)
class SpentPush:
    operation: Literal["or", "replace"]
    value: int


class StorageHandler(FolderHandler):
    _tag: str
    _player_name: str

    def __init__(self):
        self._tag = ''
        self._player_name = ''
        self._spent: int | None = None
        self._loaded: bool = False
        self._up_to_date: bool = False
        self._dirty: bool = False
        self._warned: bool = False
        super().__init__()

    def set_tag(self, tag: str) -> None:
        if tag != self._tag:
            self._tag = tag
            self._loaded = False

    def set_player_name(self, player_name: str) -> None:
        if player_name != self._player_name:
            self._player_name = player_name
            self._loaded = False

    def apdata_dir(self) -> Path:
        return Path(self._user_folder, APDATA_SUBPATH)

    def state_path(self) -> Path:
        return self.apdata_dir() / Identity.storage_file_name(
            STATE_STEM, self._tag, self._player_name)

    def is_up_to_date(self) -> bool:
        return self._up_to_date

    def try_load(self) -> int | None:
        self._ensure_loaded()
        return self._spent

    def spent_mask(self) -> int:
        return self.try_load() or 0

    def spent_indices(self, received: int) -> set[int]:
        spent = self.spent_mask()
        return {index for index in range(received) if (spent >> index) & 1}

    def try_save(self, spent: int) -> bool:
        self._ensure_loaded()
        self._spent = spent
        return self._flush()

    def mark_spent(self, indices: Iterable[int]) -> bool:
        before = self.spent_mask()
        spent = before
        for index in indices:
            spent |= 1 << index
        if spent == before:
            return False
        self._spent = spent
        self._flush()
        return True

    def reconcile(self, server: int, received: int) -> SpentPush | None:
        spent = self.spent_mask() | server
        spent &= (1 << received) - 1
        self.try_save(spent)
        self._up_to_date = True
        if spent == server:
            return None
        if server & ~spent:
            return SpentPush("replace", spent)
        return SpentPush("or", spent)

    def try_clear(self) -> bool:
        self._ensure_loaded()
        if self._spent is None:
            return False
        self._spent = None
        self._flush()
        return True

    def try_flush(self) -> None:
        if self._dirty:
            self._flush()

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            self._spent = self._read()
        except FileNotFoundError:
            self._spent = None
        except Exception:
            logger.exception("Could not read %s; treating it as a fresh playthrough.",
                             self.state_path())
            self._spent = None

    def _read(self) -> int | None:
        state = json.loads(self.state_path().read_text(encoding="utf-8"))
        spent = state["spent"]
        return None if spent is None else int(spent)

    def _flush(self) -> bool:
        try:
            self.apdata_dir().mkdir(parents=True, exist_ok=True)
            self.state_path().write_text(
                json.dumps({"spent": self._spent}, indent=4), encoding="utf-8")
        except Exception as ex:
            self._dirty = True
            if not self._warned:
                self._warned = True
                logger.warning("Could not write %s (%s). Spends are kept in memory and on the "
                               "server; retrying every tick.", self.state_path(), ex)
            return False
        self._dirty = False
        if self._warned:
            self._warned = False
            logger.info("Wrote %s; the spent record is back on disk.", self.state_path())
        return True
