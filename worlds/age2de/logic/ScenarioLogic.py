from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData

from rule_builder.rules import False_, Has, Rule, True_

from ..items.Items import Age2ItemData, Resource
from .custom_logic.Named import Named
from .custom_logic.ScenarioQuestions import a_or_an
from .ScenarioPlayer import ScenarioPlayer
from ..locations.Ages import Age2AgeData

if TYPE_CHECKING:
    from .. import Age2World
    from ..locations.Scenarios import Age2ScenarioData
    from .Logic import Logic

@dataclass
class ScenarioStartingState:
    is_unlocked: Rule = field(default_factory=lambda: False_())
    has_vils: Rule = field(default_factory=lambda: True_())
    has_base: Rule = field(default_factory=lambda: False_())
    # A base is no use where you cannot stand: some scenarios must first reach the ground
    # they are meant to settle. Kept free of the economy, since has_base feeds it.
    meets_additional_base_requirements: Rule = field(default_factory=lambda: True_())
    age_playable: dict[Age2AgeData, Rule] = field(default_factory=dict)
    starts_with_building: dict[Age2BuildingData, Rule] = field(default_factory=lambda: { building: False_() for building in Age2BuildingData })
    obtains_unit: dict[Age2UnitData | Age2HeroData | Age2EscortUnitData, Rule] = field(default_factory=dict)
    obtains_tech: dict[Age2TechData, Rule] = field(default_factory=dict)
    job_available: dict[Age2VillagerJobData, Rule] = field(
        default_factory=lambda: {job: True_() for job in Age2VillagerJobData})
    has_water_access: Rule = field(default_factory=lambda: True_())
    must_steal_base: Rule = field(default_factory=lambda: False_())
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

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        """What P1 needs to defeat each opponent, keyed by this scenario's players. Built once,
        on the first ask, and read through ScenarioLogic.defeats."""
        return {}

class ScenarioLogic:
    starting_state: ScenarioStartingState

    def __init__(self, logic: 'Logic', data: ScenarioStartingState,
                 scenario: 'Age2ScenarioData'):
        self.logic = logic
        self.scenario = scenario
        self.starting_state = data
        self._defeats: dict[ScenarioPlayer, Rule] | None = None
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
        return self.named("has villagers", self.starting_state.has_vils)

    def has_builders(self) -> Rule:
        """Villagers who can put a building up. With professions shuffled, only once the Builder
        profession arrives: without it a villager can never swap into a Builder."""
        return self.has_vils() & self.logic.units.has_profession_item(Age2VillagerJobData.BUILDER_MALE)

    def can_have_base(self) -> Rule:
        """A base, less paying for it: one to start with or one to put up, and the ground to
        stand it on."""
        return ((self.starting_state.has_base | self.buildings.can_build_base())
                & self.starting_state.meets_additional_base_requirements)

    def has_base(self) -> Rule:
        """A base, paid for: the villagers' food, and the Town Center's wood and stone where none
        stands. Paid by the items that seed it, never by an easy source - the easy sources ask
        for a base themselves."""
        return self.named("has a base", self._has_base())

    def _has_base(self) -> Rule:
        standing = (self.starting_state.has_base
                    | self.starting_state.starts_with_building[Age2BuildingData.TOWN_CENTER])
        town_center = (Has(Age2ItemData.TOWN_CENTER_WOOD.item_name)
                       & Has(Age2ItemData.TOWN_CENTER_STONE.item_name))
        return (self.can_have_base()
                & Has(Age2ItemData.STARTING_VILLAGER_FOOD.item_name)
                & (standing | town_center))

    def defeats(self, player: ScenarioPlayer) -> Rule:
        """P1 can overcome this player's army and take its ground. The same rule on every ask,
        so victory and anything else asking about this player share one."""
        if self._defeats is None:
            self._defeats = {
                opponent: self.named(f"can defeat {opponent.player_name}", rule)
                for opponent, rule in self.starting_state.defeat_rules(self).items()
            }
        return self._defeats[player]

    def has_water_access(self) -> Rule:
        return self.starting_state.has_water_access

    def job_available(self, job: Age2VillagerJobData) -> Rule:
        return self.starting_state.job_available[job]

    def obtains_unit(self, unit: Age2UnitData | Age2HeroData | Age2EscortUnitData) -> Rule:
        authored = self.starting_state.obtains_unit.get(unit)
        if authored is not None:
            return authored
        return False_()

    def named(self, asks: str, rule: Rule) -> Rule:
        """A rule of this scenario under a name - `asks` is how it reads after the scenario's name,
        "can hunt". It holds exactly when `rule` does; /explain shows it as one line."""
        return Named(rule, label=f"{self.scenario.scenario_name} {asks}")

    def obtains_tech(self, tech: Age2TechData) -> Rule:
        authored = self.starting_state.obtains_tech.get(tech)
        if authored is not None:
            return authored
        return False_()

    def has_building(self, building: Age2BuildingData) -> Rule:
        name = building.location_name.removeprefix("Build ")
        return self.named(f"has {a_or_an(name)} {name}, standing or buildable", self._has_building(building))

    def _has_building(self, building: Age2BuildingData) -> Rule:
        return (self.starting_state.starts_with_building[building]
                | self.buildings.can_build_building(building))

    def is_unlocked(self) -> Rule:
        return self.starting_state.is_unlocked