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
    _buildings: dict[Age2BuildingData, ManagedBuilding] = {}
    
    def __init__(self, data: list[Age2BuildingData]):
        for building in data:
            managedBuilding = ManagedBuilding(building, building.item)
            self._buildings[building] = managedBuilding
    
    def unlock_building(self, building: Age2BuildingData):
        if building not in self._buildings:
            print(f"Building data not found in this AP World's Building Handler. Could not unlock building {building.name}.")
            return
        self._buildings[building].unlocked = True
    
    def try_sync_buildings(self, unlocked_items: list[Age2ItemData]):
        try:
            for building in self._buildings.values():
                if building.item in unlocked_items:
                    self.unlock_building(building.data)
                
            with open(self._user_folder + "buildings.xsdat", "wb") as fp:
                for building in self._buildings.values():
                    if building.unlocked:
                        XsdatFile.write_int(fp, building.item.id)
        except Exception as ex:
            print(ex)