from .FolderHandler import FolderHandler
from ...campaign import XsdatFile
from ...items.Items import Age2ItemData, UnitBuilding, UnitLine, UnitUpgrade


UNIT_ITEM_TYPES = (UnitLine, UnitUpgrade, UnitBuilding)


class UnitHandler(FolderHandler):
    _items: dict[Age2ItemData, bool]

    def __init__(self, items: list[Age2ItemData] = None):
        if items is None:
            items = [item for item in Age2ItemData if item.type_data in UNIT_ITEM_TYPES]
        self._items = {item: False for item in items}
        super().__init__()

    def unlock_item(self, item: Age2ItemData):
        if item not in self._items:
            print(f"Item {item.name} is not a unit item; the Unit Handler will not record it.")
            return
        self._items[item] = True

    def try_sync_units(self, unlocked_items: list[Age2ItemData]):
        try:
            for item in self._items:
                if item in unlocked_items:
                    self._items[item] = True

            with open(self._user_folder + "units.xsdat", "wb") as fp:
                for item, unlocked in self._items.items():
                    if unlocked:
                        XsdatFile.write_int(fp, item.id)
        except Exception as ex:
            print(ex)
