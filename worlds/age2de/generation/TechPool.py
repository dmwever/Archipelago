from ..locations.Techs import Age2TechData, TechOption, researchable

MODE_TO_OPTION = {
    Techsanity.option_none: None,
    Techsanity.option_units: TechOption.units,
    Techsanity.option_generic: TechOption.generic,
    Techsanity.option_all: None
}

class TechPool:

    def __init__(self, techsanity: int, shuffle_uniques: int, earliest_age: Age2AgeData,
                 existing_techs_mode: int):
        self._techsanity = techsanity
        self._shuffle_uniques = shuffle_uniques
        self._earliest_age = earliest_age
        self._existing_techs_mode = existing_techs_mode
    
    def in_mode(self, tech: Age2TechData) -> bool:
        """Techsanity. Units and Generic are disjoint halves of All."""
        wanted = MODE_TO_OPTION[self._techsanity]
        return wanted is None or wanted in tech.tech_options


    def is_unique_shuffled(self, tech: Age2TechData) -> bool:
        """Shuffle Unique Techs. A shared technology is never held back by it."""
        if TechOption.unique not in tech.tech_options:
            return True
        return self._shuffle_uniques != ShuffleUniqueTechs.option_unshuffled


    def reachable(self, tech: Age2TechData) -> bool:
        """Existing Techs. A scenario auto-researches everything below the age it
        starts in, so unless this mode withholds it, a technology no scenario starts
        below is granted on load and never becomes a location the game can check."""
        if ExistingTechs.locks(self._existing_techs_mode, TechOption.units in tech.tech_options):
            return True
        return self._earliest_age <= tech.age


    def by_building(self, civs: Iterable[Age2CivData]) -> dict[Age2BuildingData, list[Age2TechData]]:
        """The seed's tech locations, grouped by the building that researches them."""
        out: dict[Age2BuildingData, list[Age2TechData]] = {}
        if self._techsanity == Techsanity.option_none:
            return out
        for tech in researchable(civs):
            if not self.in_mode(tech):
                continue
            if not self.is_unique_shuffled(tech):
                continue
            if not self.reachable(tech):
                continue
            out.setdefault(tech.buildings[0], []).append(tech)
        return out
