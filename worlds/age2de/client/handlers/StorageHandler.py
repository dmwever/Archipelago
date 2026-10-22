import json
import logging
from pathlib import Path

from .FolderHandler import FolderHandler

from ...generation import Identity

logger = logging.getLogger("Client")

APDATA_SUBPATH = "APData"
STATE_STEM = "state"

class StorageHandler(FolderHandler):
    _tag: str
    _player_name: str

    def __init__(self):
        self._tag = ''
        self._player_name = ''
        self._spent: int | None = None
        self._loaded: bool = False
        super().__init__()

    def set_tag(self, tag: str) -> None:
        self._tag = tag
        self._loaded = False

    def set_player_name(self, player_name: str) -> None:
        self._player_name = player_name
        self._loaded = False

    def apdata_dir(self) -> Path:
        return Path(self._user_folder, APDATA_SUBPATH)

    def state_path(self) -> Path:
        return self.apdata_dir() / Identity.storage_file_name(
            STATE_STEM, self._tag, self._player_name)

    def try_load(self) -> int | None:
        self._ensure_loaded()
        return self._spent

    def spent_mask(self) -> int:
        return self.try_load() or 0

    def try_save(self, spent: int) -> bool:
        self._ensure_loaded()
        self._spent = spent
        return self._flush()

    def try_clear(self) -> bool:
        self._ensure_loaded()
        if self._spent is None:
            return False
        self._spent = None
        self._flush()
        return True

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
        except Exception:
            logger.exception("Could not write %s.", self.state_path())
            return False
        return True
