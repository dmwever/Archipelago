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

    def __init__(self, options: Age2Options, earliest_age: Age2AgeData,
                 civs: Iterable[Age2CivData]):
        self._techsanity = options.techsanity
        self._shuffle_uniques = options.shuffle_unique_techs
        self._existing_techs_mode = options.existing_techs
        self._earliest_age = earliest_age
        self._researchable = {tech for civ in civs for tech in CIV_TO_TECHS[civ]}
    
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


    def includes(self, tech: Age2TechData) -> bool:
        """Whether this technology is one of the seed's locations."""
        if self._techsanity == Techsanity.option_none:
            return False
        if tech not in self._researchable:
            return False
        return (self.in_mode(tech) and self.is_unique_shuffled(tech)
                and self.reachable(tech))


    def by_building(self, building: Age2BuildingData) -> list[Age2TechData]:
        """The seed's tech locations this building researches. A technology whose
        research building is a unique replacement is listed under both, so it is
        placed only in the standard building it names first."""
        return [tech for tech in BUILDING_TO_TECHS[building]
                if tech.buildings[0] is building and self.includes(tech)]
