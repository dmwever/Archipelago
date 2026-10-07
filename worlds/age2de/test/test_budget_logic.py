"""A scenario's running total: what it asks the opening pile and early gathering to pay for.

Logic used to price a location on its own, and to charge nothing for the age-ups, buildings and
prerequisite techs it dragged in, so a scenario could be asked for far more than one run can pay.
These pin what the total charges, what it lets off, and that it never grows as items arrive.
"""
import itertools

from BaseClasses import CollectionState

from . import bases
from ..generation.pools.BudgetPool import VILLAGER, BudgetKind
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..logic.custom_logic.ResourceAmount import contributors
from ..logic.custom_logic.BudgetTotal import BudgetTotal, budget_order, required
from ..generation.pools.BudgetPool import RELIC_ALLOWANCE, SOURCE_ALLOWANCE
from ..Options import ShuffleVillager, Techsanity, Unitsanity

HARD = dict(
    shuffle_buildings={"Economy", "Tech", "Military"},
    shuffle_ages=1,
    techsanity=Techsanity.option_all,
    unitsanity=Unitsanity.option_all,
    shuffle_villager=ShuffleVillager.option_include_professions,
)


class BudgetTestBase(bases.Age2RuleTestBase):
    def setUp(self) -> None:
        self.build(**HARD)

    def budget(self, scenario: Age2ScenarioData):
        return budget_order(self.world.rules.logic.for_scenario(scenario),
                                 self.world)

    def state_with(self, *item_names: str) -> CollectionState:
        state = CollectionState(self.multiworld)
        for name in item_names:
            state.collect(self.world.create_item(name), prevent_sweep=True)
        return state

    def waived(self, budget, state: CollectionState) -> frozenset:
        return frozenset(building for building, rule in budget.waivers.items()
                         if rule.resolve(self.world)(state))

    def cost_of(self, budget, kind: BudgetKind, location,
                waived: frozenset = frozenset()):
        return required(budget.plan([budget.priced(kind, location)]), waived)


class TestStartingBuildingsAreLetOff(BudgetTestBase):
    """Bleda's Camp stands up seven buildings and a Town Center; Attila's Camp only a Stable."""

    def test_bledas_camp_waives_its_buildings(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        bleda = self.waived(budget, self.state_with(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name))
        attila = self.waived(budget, self.state_with(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name))
        neither = self.waived(budget, self.state_with())
        self.assertEqual(neither, frozenset())
        self.assertEqual(attila, {Age2BuildingData.STABLE})
        self.assertLessEqual({Age2BuildingData.TOWN_CENTER, Age2BuildingData.BARRACKS,
                              Age2BuildingData.ARCHERY_RANGE, Age2BuildingData.BLACKSMITH}, bleda)

        archer = [self.cost_of(budget, BudgetKind.UNIT, Age2UnitData.ARCHER, waived)
                  for waived in (bleda, attila, neither)]
        self.assertNotIn(Age2BuildingData.ARCHERY_RANGE, archer[0].buildings)
        self.assertIn(Age2BuildingData.ARCHERY_RANGE, archer[1].buildings)
        self.assertIn(Age2BuildingData.BARRACKS, archer[2].buildings)
        self.assertLess(archer[0].cost[Resource.WOOD], archer[1].cost[Resource.WOOD])
        self.assertLessEqual(archer[1].cost[Resource.WOOD], archer[2].cost[Resource.WOOD])

    def test_a_building_entry_is_charged_even_when_one_stands(self):
        """Build Blacksmith means putting up another one, whatever the camp left standing."""
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        bleda = self.waived(budget, self.state_with(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name))
        cost = self.cost_of(budget, BudgetKind.BUILDING, Age2BuildingData.BLACKSMITH, bleda)
        self.assertGreaterEqual(cost.cost[Resource.WOOD], Age2BuildingData.BLACKSMITH.cost[Resource.WOOD])


class TestAgeUps(BudgetTestBase):
    def test_a_dark_start_pays_for_feudal_and_its_town_center(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        cost = self.cost_of(budget, BudgetKind.TECH, Age2TechData.TOWN_WATCH)
        self.assertEqual(cost.ages, (Age2AgeData.FEUDAL,))
        self.assertIn(Age2BuildingData.TOWN_CENTER, cost.buildings)
        self.assertGreaterEqual(cost.cost[Resource.FOOD], 500)

    def test_a_base_lets_the_town_center_off(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        bleda = self.waived(budget, self.state_with(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name))
        cost = self.cost_of(budget, BudgetKind.TECH, Age2TechData.TOWN_WATCH, bleda)
        self.assertNotIn(Age2BuildingData.TOWN_CENTER, cost.buildings)

    def test_a_feudal_start_does_not_pay_for_feudal(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_2)
        self.assertIsNone(budget.priced(BudgetKind.AGE, Age2AgeData.FEUDAL))
        cost = self.cost_of(budget, BudgetKind.TECH, Age2TechData.TOWN_WATCH)
        self.assertEqual(cost.ages, ())


class TestPrerequisiteTechs(BudgetTestBase):
    def test_town_patrol_pays_for_town_watch_from_the_dark_age(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        plan = budget.plan([budget.priced(BudgetKind.TECH, Age2TechData.TOWN_PATROL)])
        own = plan.own_cost()
        expected = {resource: Age2TechData.TOWN_PATROL.cost.get(resource, 0)
                    + Age2TechData.TOWN_WATCH.cost.get(resource, 0) for resource in Resource}
        self.assertEqual(own, {resource: amount for resource, amount in expected.items() if amount})

    def test_a_castle_start_has_town_watch_for_free(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_4)
        plan = budget.plan([budget.priced(BudgetKind.TECH, Age2TechData.TOWN_PATROL)])
        self.assertEqual(plan.own_cost(), {resource: amount for resource, amount
                                          in Age2TechData.TOWN_PATROL.cost.items() if amount})

    def test_an_upgraded_unit_pays_for_its_upgrade_chain(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_4)
        unit = Age2UnitData.TWO_HANDED_SWORDSMAN
        priced = budget.priced(BudgetKind.UNIT, unit)
        plan = budget.plan([priced])
        charged = {identity for identity, _ in priced.need.own if isinstance(identity, Age2TechData)}
        # The Rising opens in Castle: Long Swordsman is paid for, Man-at-Arms it did itself.
        self.assertEqual(charged, {unit.upgrade_tech, unit.upgrade_tech.prerequisite})
        self.assertNotIn(Age2TechData.MAN_AT_ARMS, charged)
        expected: dict = {}
        for owner in (unit, *charged):
            for resource, amount in owner.cost.items():
                expected[resource] = expected.get(resource, 0) + amount
        self.assertEqual(plan.own_cost(), expected)


class TestOneLineOnePurchase(BudgetTestBase):
    """Archer and Crossbowman are one unit trained and one upgrade researched."""

    def test_two_tiers_of_a_line_cost_one_unit(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_2)
        archer = budget.priced(BudgetKind.UNIT, Age2UnitData.ARCHER)
        crossbow = budget.priced(BudgetKind.UNIT, Age2UnitData.CROSSBOWMAN)
        self.assertIsNotNone(archer)
        self.assertIsNotNone(crossbow)
        both = budget.plan([archer, crossbow]).own_cost()
        alone = budget.plan([crossbow]).own_cost()
        self.assertEqual(both, alone)


class TestTheVillager(BudgetTestBase):
    def test_the_villager_costs_the_food_that_staffs_a_base(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_2)
        plan = budget.plan([budget.priced(BudgetKind.VILLAGER, VILLAGER)])
        food = Age2ItemData.STARTING_VILLAGER_FOOD.type.amount
        self.assertEqual(plan.own_cost(), {Resource.FOOD: food})


class TestPrecursors(BudgetTestBase):
    def test_no_entry_is_its_own_precursor(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            for entry in budget.order:
                with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                    self.assertNotIn(entry.key, [p.key for p in budget.precursors(entry)])

    def test_listing_precursors_changes_no_requirement(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            for entry in budget.order:
                with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                    alone = required(budget.plan([entry]), frozenset())
                    listed = required(budget.plan([*budget.precursors(entry), entry]), frozenset())
                    self.assertEqual(alone.cost, listed.cost)

    def test_precursors_come_before_their_entry(self):
        """Climb buildings are interchangeable: any two will do, so an entry's own cheapest pair
        need not be the pair its place in the order ends up paying for. Everything else it
        cannot be had without, and every building its running total does charge, comes first."""
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            order = budget.order
            position = {entry.key: index for index, entry in enumerate(order)}
            for index, entry in enumerate(order):
                charged = required(budget.plan(order[:index + 1]), frozenset()).buildings
                for precursor in budget.precursors(entry):
                    if precursor.key not in position:
                        continue
                    if (precursor.kind is BudgetKind.BUILDING
                            and precursor.location not in charged
                            and position[precursor.key] > index):
                        continue   # an interchangeable building this place did not need
                    with self.subTest(f"{scenario.scenario_name}: {entry.location.name} after "
                                      f"{precursor.location.name}"):
                        self.assertLess(position[precursor.key], index)

    def test_the_order_climbs_the_ages(self):
        for scenario in self.world.pool.scenarios.included:
            sampled = [entry for entry in self.budget(scenario).order
                       if self.world.pool.budget.includes(*entry.key)]
            self.assertEqual([entry.age for entry in sampled],
                             sorted(entry.age for entry in sampled))


class TestTheTotalNeverGrows(BudgetTestBase):
    """Adding a waived building must never raise what a running total asks for, or a location
    could fall out of logic as items arrive."""

    def test_waiving_one_more_building_never_raises_the_requirement(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            order = budget.order
            waivable = sorted(budget.waivers, key=int)
            for end in range(1, len(order) + 1):
                plan = budget.plan(order[:end])
                for size in range(len(waivable) + 1):
                    for waived in itertools.combinations(waivable, size):
                        base = required(plan, frozenset(waived)).cost
                        for extra in waivable:
                            if extra in waived:
                                continue
                            more = required(plan, frozenset((*waived, extra))).cost
                            for resource, amount in more.items():
                                if amount > base.get(resource, 0):
                                    self.fail(f"{scenario.scenario_name}: waiving {extra.name} on "
                                              f"top of {[w.name for w in waived]} raised "
                                              f"{resource.name} from {base.get(resource, 0)} "
                                              f"to {amount} at entry {end}")

    def test_a_longer_prefix_never_asks_for_less(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            order = budget.order
            previous: dict = {}
            for end in range(1, len(order) + 1):
                cost = required(budget.plan(order[:end]), frozenset()).cost
                for resource, amount in previous.items():
                    self.assertGreaterEqual(cost.get(resource, 0), amount)
                previous = cost


class TestSourcesAndBudget(BudgetTestBase):
    def test_relics_add_fifty_gold_each(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_3)
        relics = [source for source in budget.sources if source[0] == "relics"]
        self.assertEqual(1, len(relics))
        count = budget.scenario.economy.counts.relic_count
        self.assertEqual(relics[0][1:3], (Resource.GOLD, RELIC_ALLOWANCE * count))

    def test_every_other_source_is_worth_the_same(self):
        for scenario in self.world.pool.scenarios.included:
            for name, _, amount, _ in self.budget(scenario).sources:
                if name != "relics":
                    self.assertEqual(SOURCE_ALLOWANCE, amount)

    def test_a_fixed_force_scenario_has_no_budget(self):
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5):
            budget = self.budget(scenario)
            if not budget.scenario.starting_state.fixed_force:
                continue
            with self.subTest(scenario.scenario_name):
                self.assertEqual([], budget.sources)
                self.assertEqual((), budget.order)

    def test_pruned_entries_could_never_be_paid_for(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            most = budget.max_budget()
            every_waiver = frozenset(budget.waivers)
            need = required(budget.plan(budget.order), every_waiver).cost
            for resource, amount in need.items():
                self.assertLessEqual(amount, most[resource])


class TestTheRule(BudgetTestBase):
    def resolved(self, scenario, kind, location):
        return BudgetTotal(scenario=scenario, kind=kind, location=location).resolve(self.world)

    def test_every_pile_item_is_a_dependency(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, *budget.order[0].key)
        dependencies = set(resolved.item_dependencies())
        for resource in Resource:
            for name, _ in contributors(resource):
                self.assertIn(name, dependencies)

    def test_everything_in_the_order_fits_with_every_item(self):
        state = self.multiworld.get_all_state(False)
        for scenario in self.world.pool.scenarios.included:
            for entry in self.budget(scenario).order:
                with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                    self.assertTrue(self.resolved(scenario, *entry.key)(state))

    def test_an_empty_pile_affords_nothing_costly(self):
        state = CollectionState(self.multiworld)
        for entry in self.budget(Age2ScenarioData.AP_ATTILA_1).order:
            resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, *entry.key)
            if resolved.requirement(None).cost:
                self.assertFalse(resolved(state), entry.location.name)
                break

    def test_a_location_outside_the_order_is_never_afforded(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        outside = next(building for building in Age2BuildingData
                       if budget.priced(BudgetKind.BUILDING, building) is None)
        self.assertTrue(self.resolved(Age2ScenarioData.AP_ATTILA_1, BudgetKind.BUILDING,
                                      outside).always_false)

    def test_the_breakdown_adds_up_to_the_requirement(self):
        """The long view a later /explain + /more shows: it has to describe the same total."""
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, *budget.order[-1].key)
        state = self.multiworld.get_all_state(False)
        breakdown = resolved.breakdown(state)
        self.assertEqual(breakdown["requirement"], resolved.requirement(state).cost)
        self.assertEqual(breakdown["scenario"], "The Scourge of God")
        self.assertTrue(breakdown["sources_on"])
        self.assertEqual(resolved.breakdown()["waived"], [])

    def test_the_explanation_names_the_scenario_and_totals(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        text = self.resolved(Age2ScenarioData.AP_ATTILA_1, *budget.order[-1].key).explain_str()
        self.assertIn("The Scourge of God", text)
        self.assertIn("food", text)
class TestCouldEverHave(BudgetTestBase):
    def test_a_fixed_force_scenario_can_build_nothing(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_1)
        self.assertFalse(any(budget.could_have(building)
                             for building in Age2BuildingData))
