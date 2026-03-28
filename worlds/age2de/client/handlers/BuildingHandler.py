from dataclasses import dataclass

from .FolderHandler import FolderHandler
from ...campaign import XsdatFile
from ...items.Items import Age2ItemData
from ...locations.Buildings import Age2BuildingData

@dataclass
class ManagedBuilding:
    data: Age2BuildingData
    item: Age2ItemData
    unlocked = False

class BuildingHandler(FolderHandler):
    _buildings: dict[Age2BuildingData, ManagedBuilding] = dict()
    
    def __init__(self, data: list[Age2BuildingData]):
        for building in data:
            managedBuilding = ManagedBuilding(building, building.item)
    
    def unlock_building(self, building: Age2BuildingData):
        if building not in self._buildings:
            print(f"Building data not found in this AP World's Building Handler. Could not unlock building {building.name}.")
            return
        ManagedBuilding[building].unlocked = True
    
    def try_sync_buildings(self):
        try:
            with open(self._user_folder + "buildings.xsdat", "wb") as fp:
                for building in self._buildings.values():
                    if building.unlocked:
                        XsdatFile.write_int(fp, building.item.id)
        except Exception as ex:
            print(ex)