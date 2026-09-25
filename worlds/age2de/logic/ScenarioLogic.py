from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData

from rule_builder.options import OptionFilter
from rule_builder.rules import False_, Has, Rule, True_

from ..Options import ExistingTechs
from ..locations.Ages import Age2AgeData


VANILLA_AGE_START = OptionFilter(ExistingTechs, ExistingTechs.option_start_in_dark_age, "ne")
DARK_START = OptionFilter(ExistingTechs, ExistingTechs.option_start_in_dark_age)

if TYPE_CHECKING:
    from .. import Age2World
    from ..locations.Scenarios import Age2ScenarioData
    from .Logic import Logic

@dataclass
class ScenarioStartingState:
    is_unlocked: Rule = field(default_factory=lambda: False_())
    has_vils: Rule = field(default_factory=lambda: True_())
    has_base: Rule = field(default_factory=lambda: True_())
    age_playable: dict[Age2AgeData, Rule] = field(default_factory=lambda: { age: False_() for age in Age2AgeData })
    starts_with_building: dict[Age2BuildingData, Rule] = field(default_factory=lambda: { building: False_() for building in Age2BuildingData })
    obtains_unit: dict[Age2UnitData | Age2HeroData | Age2EscortUnitData, Rule] = field(default_factory=dict)
    job_available: dict[Age2VillagerJobData, Rule] = field(
        default_factory=lambda: {job: True_() for job in Age2VillagerJobData})
    has_water_access: Rule = field(default_factory=lambda: True_())
    fixed_force: bool = False
    """A set piece fought with what it hands you. No base, and no age to be in."""

    def __post_init__(self):
        self.age_playable[Age2AgeData.DARK] = True_() & DARK_START

    def default_mercenary_grants(self, scenario: 'Age2ScenarioData') -> None:
        from ..items.Items import Mercenary, SCENARIO_TO_ITEMS
        for item in SCENARIO_TO_ITEMS[scenario]:
            if item.type_data is not Mercenary:
                continue
            for soldier in item.type.units:
                self.obtains_unit[soldier.unit] = (
                    self.obtains_unit.get(soldier.unit, False_()) | Has(item.item_name))
                
class ScenarioLogic:
    starting_state: ScenarioStartingState

    def __init__(self, logic: 'Logic', data: ScenarioStartingState,
                 scenario: 'Age2ScenarioData'):
        self.logic = logic
        self.scenario = scenario
        self.starting_state = data
        data.default_mercenary_grants(scenario)
        # What can be put up here, as opposed to anywhere. See ScenarioBuildingLogic.
        from .scenarios.ScenarioBuildingLogic import ScenarioBuildingLogic
        from .scenarios.ScenarioMilitaryLogic import ScenarioMilitaryLogic
        from .scenarios.ScenarioTechLogic import ScenarioTechLogic
        from .scenarios.ScenarioUnitLogic import ScenarioUnitLogic
        self.buildings = ScenarioBuildingLogic(self)
        self.military = ScenarioMilitaryLogic(self)
        self.techs = ScenarioTechLogic(self)
        self.units = ScenarioUnitLogic(self)
    
    def has_vils(self) -> Rule:
        return self.starting_state.has_vils
    
    def has_base(self) -> Rule:
        return self.starting_state.has_base

    def has_water_access(self) -> Rule:
        return self.starting_state.has_water_access

    def can_reach_age(self, age: Age2AgeData) -> Rule:
        if self.starting_state.fixed_force:
            return False_()
        return self.starting_state.age_playable[age]

    def can_play_age(self, age: Age2AgeData) -> Rule:
        """Able to act in that age here - either by advancing to it, or by opening above it.

        The two halves are separate questions and both count. AgeLogic pairs them the same way
        when it builds the global answer; using can_reach_age alone would say a Castle-age
        scenario cannot put up a House, because age_playable[DARK] is gated on starting in the
        Dark Age.
        """
        return self.can_reach_age(age) | self.start_past_age(age)

    def start_past_age(self, age: Age2AgeData) -> Rule:
        if self.starting_state.fixed_force:
            return False_()
        if self.scenario.vanilla_age > age:
            return True_() & VANILLA_AGE_START
        return False_()
    
    def job_available(self, job: Age2VillagerJobData) -> Rule:
        return self.starting_state.job_available[job]

    def obtains_unit(self, unit: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        authored = self.starting_state.obtains_unit.get(unit)
        if authored is not None:
            return authored
        if unit in self.scenario.trigger_units:
            return True_()
        return False_()

    def start_with_building(self, building: Age2BuildingData) -> Rule:
        """Already standing here, or something this scenario can put up itself."""
        return (self.starting_state.starts_with_building[building]
                | self.buildings.can_build_building(building))
    
    def is_unlocked(self) -> Rule:
        return self.starting_state.is_unlocked