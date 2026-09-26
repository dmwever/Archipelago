from dataclasses import dataclass

from .FolderHandler import FolderHandler
from ...campaign import XsdatFile
from ...items.Items import Age2ItemData, UnitBuilding, UnitLine, UnitUpgrade


UNIT_ITEM_TYPES = (UnitLine, UnitUpgrade, UnitBuilding)


@dataclass
class ManagedUnitItem:
    item: Age2ItemData
    unlocked: bool = False


class UnitHandler(FolderHandler):
    _items: dict[Age2ItemData, ManagedUnitItem]

    def __init__(self, items: list[Age2ItemData] = None):
        if items is None:
            items = [item for item in Age2ItemData if item.type_data in UNIT_ITEM_TYPES]
        self._items = {item: ManagedUnitItem(item) for item in items}
        super().__init__()

    def unlock_item(self, item: Age2ItemData):
        if item not in self._items:
            print(f"Item {item.name} is not a unit item; the Unit Handler will not record it.")
            return
        self._items[item].unlocked = True

    def try_sync_units(self, unlocked_items: list[Age2ItemData]):
        try:
            for managed in self._items.values():
                if managed.item in unlocked_items:
                    self.unlock_item(managed.item)

            with open(self._user_folder + "units.xsdat", "wb") as fp:
                for managed in self._items.values():
                    if managed.unlocked:
                        XsdatFile.write_int(fp, managed.item.id)
        except Exception as ex:
            print(ex)
