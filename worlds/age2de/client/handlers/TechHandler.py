from dataclasses import dataclass

from .FolderHandler import FolderHandler
from ...campaign import XsdatFile
from ...items.Items import Age2ItemData
from ...locations.Techs import Age2TechData


@dataclass
class ManagedTech:
    data: Age2TechData
    item: Age2ItemData
    unlocked: bool = False


class TechHandler(FolderHandler):
    _techs: dict[Age2TechData, ManagedTech]

    def __init__(self, data: list[Age2TechData]):
        self._techs = {}
        for tech in data:
            self._techs[tech] = ManagedTech(tech, tech.item)
        super().__init__()

    def unlock_tech(self, tech: Age2TechData):
        if tech not in self._techs:
            print(f"Tech data not found in this AP World's Tech Handler. Could not unlock tech {tech.name}.")
            return
        self._techs[tech].unlocked = True

    def try_sync_techs(self, unlocked_items: list[Age2ItemData]):
        try:
            for tech in self._techs.values():
                if tech.item in unlocked_items:
                    self.unlock_tech(tech.data)

            with open(self._user_folder + "techs.xsdat", "wb") as fp:
                for tech in self._techs.values():
                    if tech.unlocked:
                        XsdatFile.write_int(fp, tech.item.id)
        except Exception as ex:
            print(ex)
