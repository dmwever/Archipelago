from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData

from rule_builder.rules import False_, Has, Rule, True_

from ..items.Items import Age2ItemData, Resource
from .budget.BudgetItem import BASE
from .budget.BudgetTotal import BudgetTotal
from ..locations.Ages import Age2AgeData

if TYPE_CHECKING:
    from .. import Age2World
    from ..locations.Scenarios import Age2ScenarioData
    from .Logic import Logic
    from .budget.BudgetItem import PricedLocation

@dataclass
class ScenarioStartingState:
    is_unlocked: Rule = field(default_factory=lambda: False_())
    has_vils: Rule = field(default_factory=lambda: True_())
    has_base: Rule = field(default_factory=lambda: False_())
    # A base is no use where you cannot stand: some scenarios must first reach the ground
    # they are meant to settle. Kept free of the economy, since has_base feeds it.
    meets_additional_base_requirements: Rule = field(default_factory=lambda: True_())
    max_age: Age2AgeData = Age2AgeData.IMPERIAL
    age_playable: dict[Age2AgeData, Rule] = field(default_factory=dict)
    starts_with_building: dict[Age2BuildingData, Rule] = field(default_factory=lambda: { building: False_() for building in Age2BuildingData })
    obtains_unit: dict[Age2UnitData | Age2HeroData | Age2EscortUnitData, Rule] = field(default_factory=dict)
    job_available: dict[Age2VillagerJobData, Rule] = field(
        default_factory=lambda: {job: True_() for job in Age2VillagerJobData})
    has_water_access: Rule = field(default_factory=lambda: True_())
    must_steal_base: Rule = field(default_factory=lambda: False_())
    fixed_force: bool = False
    starting_gold_mine: Rule = field(default_factory=lambda: True_())
    starting_stone_mine: Rule = field(default_factory=lambda: True_())
    starting_trees: Rule = field(default_factory=lambda: True_())
    starting_bushes: Rule = field(default_factory=lambda: True_())
    starting_hunting: Rule = field(default_factory=lambda: True_())
    starting_fish: Rule = field(default_factory=lambda: True_())
    starting_sheep: Rule = field(default_factory=lambda: True_())
    starting_oysters: Rule = field(default_factory=lambda: False_())
    starting_whales: Rule = field(default_factory=lambda: False_())
    starting_relics: Rule = field(default_factory=lambda: True_())
    trading_ally: Rule = field(default_factory=lambda: False_())
    required_purchases: 'dict[PricedLocation, Rule]' = field(default_factory=dict)
    """What the scenario has to buy to be beaten, and the rule that makes buying it unnecessary
    (False_ if nothing does). Each joins its budget order, drawn or not."""
    easy_resource_sources: dict[Resource, Rule] = field(
        default_factory=lambda: {resource: False_() for resource in Resource})

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
        from .scenarios.ScenarioAgeLogic import ScenarioAgeLogic
        from .scenarios.ScenarioBuildingLogic import ScenarioBuildingLogic
        from .scenarios.ScenarioCivilizationLogic import ScenarioCivilizationLogic
        from .scenarios.ScenarioMilitaryLogic import ScenarioMilitaryLogic
        from .scenarios.ScenarioTechLogic import ScenarioTechLogic
        from .scenarios.ScenarioResourceLogic import ScenarioResourceLogic
        from .scenarios.ScenarioUnitLogic import ScenarioUnitLogic
        self.civilization = ScenarioCivilizationLogic(self)
        self.ages = ScenarioAgeLogic(self)
        self.buildings = ScenarioBuildingLogic(self)
        self.military = ScenarioMilitaryLogic(self)
        self.techs = ScenarioTechLogic(self)
        self.units = ScenarioUnitLogic(self)
        self.economy = ScenarioResourceLogic(self)
    
    def has_vils(self) -> Rule:
        return self.starting_state.has_vils
    
    def can_have_base(self) -> Rule:
        """A base, less paying for it: one to start with or one to put up, and the ground to
        stand it on."""
        return ((self.starting_state.has_base | self.buildings.can_build_base())
                & self.starting_state.meets_additional_base_requirements)

    def has_base(self) -> Rule:
        """A base, paid for: the villagers' food, and the Town Center and House where none
        stands. Through the budget only - the easy sources of wood and gold ask for a base
        themselves."""
        return self.can_have_base() & BudgetTotal(scenario=self.scenario, location=BASE)

    def has_water_access(self) -> Rule:
        return self.starting_state.has_water_access

    def job_available(self, job: Age2VillagerJobData) -> Rule:
        return self.starting_state.job_available[job]

    def obtains_unit(self, unit: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        authored = self.starting_state.obtains_unit.get(unit)
        if authored is not None:
            return authored
        return False_()

    def has_building(self, building: Age2BuildingData) -> Rule:
        return (self.starting_state.starts_with_building[building]
                | self.buildings.can_build_building(building))
    
    def is_unlocked(self) -> Rule:
        return self.starting_state.is_unlocked