import json
import logging
from pathlib import Path

from .FolderHandler import FolderHandler

from ...generation import Identity
from ...items.Items import Age2ItemData

logger = logging.getLogger("Client")

APDATA_SUBPATH = "APData"
MERCENARY_STEM = "mercenaries"


def reconcile_spent(local: set[int] | None, server: set[int]) -> tuple[set[int], bool]:
    if local is None:
        return set(server), False
    return set(local), local != server

class StorageHandler(FolderHandler):
    _tag: str = ''
    _player_name: str = ''

    def __init__(self, mercenaries: list[Age2ItemData]):
        self._mercenaries = list(mercenaries)
        super().__init__()

    def set_tag(self, tag: str) -> None:
        self._tag = tag

    def set_player_name(self, player_name: str) -> None:
        self._player_name = player_name

    def apdata_dir(self) -> Path:
        return Path(self._user_folder, APDATA_SUBPATH)

    def mercenary_path(self) -> Path:
        return self.apdata_dir() / Identity.storage_file_name(
            MERCENARY_STEM, self._tag, self._player_name)

    def try_load(self) -> set[int] | None:
        try:
            return self._read()
        except FileNotFoundError:
            return None
        except Exception:
            logger.exception("Could not read %s; treating it as a fresh playthrough.",
                             self.mercenary_path())
            return None

    def try_save(self, used: set[int]) -> None:
        try:
            self._write(used)
        except Exception:
            logger.exception("Could not write %s.", self.mercenary_path())

    def _read(self) -> set[int]:
        records = json.loads(self.mercenary_path().read_text(encoding="utf-8"))
        return {record["id"] for record in records if record["used"]}

    def _write(self, used: set[int]) -> None:
        records = [{"id": mercenary.id, "used": mercenary.id in used}
                   for mercenary in sorted(self._mercenaries, key=lambda item: item.id)]
        self.apdata_dir().mkdir(parents=True, exist_ok=True)
        self.mercenary_path().write_text(json.dumps(records, indent=4), encoding="utf-8")
