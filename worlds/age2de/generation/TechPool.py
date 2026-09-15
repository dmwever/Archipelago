from typing import Iterable

from ..Options import Age2Options, ExistingTechs, ShuffleUniqueTechs, Techsanity
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Civilizations import Age2CivData
from ..locations.Techs import Age2TechData, TechOption, BUILDING_TO_TECHS
from ..locations.connections.CivilizationTechs import CIV_TO_TECHS

MODE_TO_OPTION = {
    Techsanity.option_none: None,
    Techsanity.option_units: TechOption.units,
    Techsanity.option_generic: TechOption.generic,
    Techsanity.option_all: None
}

class TechPool:

    def __init__(self, options: Age2Options, earliest_age: Age2AgeData):
        self._techsanity = options.techsanity
        self._shuffle_uniques = options.shuffle_unique_techs
        self._existing_techs_mode = options.existing_techs
        self._earliest_age = earliest_age
    
    def in_mode(self, tech: Age2TechData) -> bool:
        """Techsanity. Units and Generic are disjoint halves of All."""
        wanted = MODE_TO_OPTION[self._techsanity]
        return wanted is None or wanted in tech.tech_options


    def is_unique_shuffled(self, tech: Age2TechData) -> bool:
        """Shuffle Unique Techs. A shared technology is never held back by it."""
        if TechOption.unique not in tech.tech_options:
            return True
        return self._shuffle_uniques != ShuffleUniqueTechs.option_unshuffled


    def locks(self, tech: Age2TechData) -> bool:
        """Whether Existing Techs withholds a technology the scenario would grant."""
        if self._existing_techs_mode == ExistingTechs.option_lock_technologies:
            return True
        return (self._existing_techs_mode == ExistingTechs.option_only_lock_units
                and TechOption.units in tech.tech_options)


    def reachable(self, tech: Age2TechData) -> bool:
        """Existing Techs. A scenario auto-researches everything below the age it
        starts in, so unless this mode withholds it, a technology no scenario starts
        below is granted on load and never becomes a location the game can check."""
        if self.locks(tech):
            return True
        return self._earliest_age <= tech.age


    def by_building(self, building: Age2BuildingData, civs: Iterable[Age2CivData]) -> list[Age2TechData]:
        """The seed's tech locations, grouped by the building that researches them."""
        building_techs: list[Age2TechData] = []
        if self._techsanity == Techsanity.option_none:
            return []
        building_techs = BUILDING_TO_TECHS[building]
        civ_techs = {tech for civ in civs for tech in CIV_TO_TECHS[civ]}
        for tech in civ_techs.intersection(building_techs):
            if not self.in_mode(tech):
                continue
            if not self.is_unique_shuffled(tech):
                continue
            if not self.reachable(tech):
                continue
            building_techs.append(tech)
        return building_techs
