"""A scenario's running total: what it asks the opening pile and early gathering to pay for.

Logic used to price a location on its own, and to charge nothing for the age-ups, buildings and
prerequisite techs it dragged in, so a scenario could be asked for far more than one run can pay.
These pin what the total charges, what it lets off, and that it never grows as items arrive.
"""
import itertools

from BaseClasses import CollectionState

from . import bases
from ..generation.pools.BudgetPool import VILLAGER
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..logic.custom_logic.ResourceAmount import contributors
from ..logic.budget.BudgetItem import BASE
from ..logic.budget.BudgetTotal import BudgetTotal
from ..logic.budget.Requirement import Requirement
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
        return self.world.rules.logic.for_scenario(scenario).budget.order

    def state_with(self, *item_names: str) -> CollectionState:
        state = CollectionState(self.multiworld)
        for name in item_names:
            state.collect(self.world.create_item(name), prevent_sweep=True)
        return state

    def waived(self, budget, state: CollectionState) -> frozenset:
        standing = budget.scenario.budget.standing_buildings
        return frozenset(
            building for building, rule in standing.items()
                if rule.resolve(self.world)(state)
        )

    def cost_of(self, budget, location, waived: frozenset = frozenset()):
        return Requirement(budget.plan([budget.get_priced_item(location)]), waived, budget.scenario.budget.terms)


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

        archer = [self.cost_of(budget, Age2UnitData.ARCHER, waived)
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
        cost = self.cost_of(budget, Age2BuildingData.BLACKSMITH, bleda)
        self.assertGreaterEqual(cost.cost[Resource.WOOD], Age2BuildingData.BLACKSMITH.cost[Resource.WOOD])


class TestAgeUps(BudgetTestBase):
    def test_a_dark_start_pays_for_feudal_and_its_town_center(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        cost = self.cost_of(budget, Age2TechData.TOWN_WATCH)
        self.assertEqual(cost.ages, [Age2AgeData.FEUDAL])
        self.assertIn(Age2BuildingData.TOWN_CENTER, cost.buildings)
        self.assertGreaterEqual(cost.cost[Resource.FOOD], 500)

    def test_a_base_lets_the_town_center_off(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        bleda = self.waived(budget, self.state_with(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name))
        cost = self.cost_of(budget, Age2TechData.TOWN_WATCH, bleda)
        self.assertNotIn(Age2BuildingData.TOWN_CENTER, cost.buildings)

    def test_a_feudal_start_does_not_pay_for_feudal(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_2)
        self.assertIsNone(budget.get_priced_item(Age2AgeData.FEUDAL))
        cost = self.cost_of(budget, Age2TechData.TOWN_WATCH)
        self.assertEqual(cost.ages, [])


class TestPrerequisiteTechs(BudgetTestBase):
    def test_town_patrol_pays_for_town_watch_from_the_dark_age(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        plan = budget.plan([budget.get_priced_item(Age2TechData.TOWN_PATROL)])
        own = plan.own_cost()
        expected = {resource: Age2TechData.TOWN_PATROL.cost.get(resource, 0)
                    + Age2TechData.TOWN_WATCH.cost.get(resource, 0) for resource in Resource}
        self.assertEqual(own, {resource: amount for resource, amount in expected.items() if amount})

    def test_a_castle_start_has_town_watch_for_free(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_4)
        plan = budget.plan([budget.get_priced_item(Age2TechData.TOWN_PATROL)])
        self.assertEqual(plan.own_cost(), {resource: amount for resource, amount
                                          in Age2TechData.TOWN_PATROL.cost.items() if amount})

    def test_an_upgraded_unit_pays_for_its_upgrade_chain(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_4)
        unit = Age2UnitData.TWO_HANDED_SWORDSMAN
        priced = budget.get_priced_item(unit)
        plan = budget.plan([priced])
        charged = {
            price.identity for price in priced.need.own_price
                if isinstance(price.identity, Age2TechData)
        }
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
        archer = budget.get_priced_item(Age2UnitData.ARCHER)
        crossbow = budget.get_priced_item(Age2UnitData.CROSSBOWMAN)
        self.assertIsNotNone(archer)
        self.assertIsNotNone(crossbow)
        both = budget.plan([archer, crossbow]).own_cost()
        alone = budget.plan([crossbow]).own_cost()
        self.assertEqual(both, alone)


class TestTheVillager(BudgetTestBase):
    def test_the_villager_costs_the_food_that_staffs_a_base(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_2)
        plan = budget.plan([budget.get_priced_item(VILLAGER)])
        food = Age2ItemData.STARTING_VILLAGER_FOOD.type.amount
        self.assertEqual(plan.own_cost(), {Resource.FOOD: food})


class TestPrecursors(BudgetTestBase):
    def test_no_entry_is_its_own_precursor(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            for entry in budget.order:
                with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                    self.assertNotIn(entry.location, [p.location for p in budget.precursors(entry)])

    def test_listing_precursors_changes_no_requirement(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            for entry in budget.order:
                with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                    alone = Requirement(budget.plan([entry]), frozenset(), budget.scenario.budget.terms)
                    listed = Requirement(budget.plan([*budget.precursors(entry), entry]), frozenset(),
                                         budget.scenario.budget.terms)
                    self.assertEqual(alone.cost, listed.cost)

    def test_precursors_come_before_their_entry(self):
        """Climb buildings are interchangeable: any two will do, so an entry's own cheapest pair
        need not be the pair its place in the order ends up paying for. Everything else it
        cannot be had without, and every building its running total does charge, comes first."""
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            order = budget.order
            position = {entry.location: index for index, entry in enumerate(order)}
            for index, entry in enumerate(order):
                charged = Requirement(budget.plan(order[:index + 1]), frozenset(), budget.scenario.budget.terms).buildings
                for precursor in budget.precursors(entry):
                    if precursor.location not in position:
                        continue
                    if (isinstance(precursor.location, Age2BuildingData)
                            and precursor.location not in charged
                            and position[precursor.location] > index):
                        continue   # an interchangeable building this place did not need
                    with self.subTest(f"{scenario.scenario_name}: {entry.location.name} after "
                                      f"{precursor.location.name}"):
                        self.assertLess(position[precursor.location], index)

    def test_the_order_climbs_the_ages(self):
        for scenario in self.world.pool.scenarios.included:
            sampled = [entry for entry in self.budget(scenario).order
                       if entry.location in self.world.pool.budget.entries]
            self.assertEqual([entry.age for entry in sampled],
                             sorted(entry.age for entry in sampled))


class TestNeedsAddInAnyOrder(BudgetTestBase):
    """A Need used to carry its scenario's start age and age-ups, and adding two dropped them: two
    settled needs summed charged every age from the Dark Age, or raised a KeyError on the first
    age-up. The terms live in Requirement now, so a Need is a plain union."""

    def test_settling_then_adding_costs_what_adding_then_settling_does(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            terms, logic = budget.scenario.budget.terms, budget.scenario.budget
            order = budget.order
            for first, second in zip(order, order[1:]):
                with self.subTest(f"{scenario.scenario_name}: {first.location.name} + "
                                  f"{second.location.name}"):
                    each = logic.settle(first.need) + logic.settle(second.need)
                    together = logic.settle(first.need + second.need)
                    self.assertEqual(Requirement(each, frozenset(), terms).cost,
                                     Requirement(together, frozenset(), terms).cost)


class TestTheTotalNeverGrows(BudgetTestBase):
    """Adding a waived building must never raise what a running total asks for, or a location
    could fall out of logic as items arrive."""

    def test_waiving_one_more_building_never_raises_the_requirement(self):
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            order = budget.order
            waivable = sorted(budget.scenario.budget.standing_buildings, key=int)
            for end in range(1, len(order) + 1):
                plan = budget.plan(order[:end])
                for size in range(len(waivable) + 1):
                    for waived in itertools.combinations(waivable, size):
                        base = Requirement(plan, frozenset(waived), budget.scenario.budget.terms).cost
                        for extra in waivable:
                            if extra in waived:
                                continue
                            more = Requirement(plan, frozenset((*waived, extra)), budget.scenario.budget.terms).cost
                            for resource, amount in more.items():
                                if amount > base.get(resource, 0):
                                    self.fail(f"{scenario.scenario_name}: waiving {extra.name} on "
                                              f"top of {[w.name for w in waived]} raised "
                                              f"{resource.name} from {base.get(resource, 0)} "
                                              f"to {amount} at entry {end}")

    def test_a_longer_prefix_never_pays_for_less_of_itself(self):
        """Each entry's own price, and every age climbed, stays charged further down the order.

        Buildings can move: an age-up charges the first two of its choices in the seed's order,
        and a later entry that buys another of them - a Barracks for a Militia - counts towards
        it instead, so a longer total can drop one building for another. That is accepted, so
        only the entries' own prices and the ages are checked here."""
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            order = budget.order
            previous_own: dict = {}
            previous_ages: list = []
            for end in range(1, len(order) + 1):
                plan = budget.plan(order[:end])
                own = plan.own_cost()
                ages = Requirement(plan, frozenset(), budget.scenario.budget.terms).ages
                with self.subTest(f"{scenario.scenario_name}: entry {end}"):
                    for resource, amount in previous_own.items():
                        self.assertGreaterEqual(own.get(resource, 0), amount)
                    self.assertLessEqual(set(previous_ages), set(ages))
                previous_own, previous_ages = own, ages


class TestFixedForce(BudgetTestBase):
    def test_a_fixed_force_scenario_has_no_budget(self):
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5):
            budget = self.budget(scenario)
            if not budget.scenario.starting_state.fixed_force:
                continue
            with self.subTest(scenario.scenario_name):
                self.assertEqual([], budget.order)


class TestEasySources(BudgetTestBase):
    """A resource with an easy source is left out of the total; the pile pays for the rest."""

    def resolved(self, scenario, location):
        return BudgetTotal(scenario=scenario, location=location).resolve(self.world)

    def test_the_base_never_asks_an_easy_source(self):
        for scenario in self.world.pool.scenarios.included:
            resolved = self.resolved(scenario, BASE)
            if isinstance(resolved, BudgetTotal.Resolved):
                with self.subTest(scenario.scenario_name):
                    self.assertEqual((), resolved.easy)

    def test_an_easy_source_covers_what_the_pile_lacks(self):
        """With every item but the starting gold, a total that costs gold is in logic exactly when
        gold has an easy source: the rest of the pile still pays for everything else, the base
        included."""
        gold = [name for name, _ in contributors(Resource.GOLD)]
        state = self.state_without(*gold)
        checked = 0
        for entry in self.budget(Age2ScenarioData.AP_ATTILA_1).order:
            resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, entry.location)
            if not dict(resolved.table.total(state).cost).get(Resource.GOLD):
                continue
            with self.subTest(entry.location.name):
                self.assertEqual(resolved.easy_source_holds(Resource.GOLD, state), resolved(state))
                checked += 1
        self.assertTrue(checked, "nothing in the order costs gold")

    def test_more_items_never_take_a_location_away(self):
        """Collect the pool one item at a time; once a total is in logic it stays in."""
        import random
        rng = random.Random(1)
        pool = list(self.multiworld.itempool)
        rng.shuffle(pool)
        for scenario in (Age2ScenarioData.AP_ATTILA_1, Age2ScenarioData.AP_JOAN_3):
            if scenario not in self.world.pool.scenarios.included:
                continue
            rules = [(entry.location.name,
                      BudgetTotal(scenario=scenario, location=entry.location).resolve(self.world))
                     for entry in self.budget(scenario).order]
            state, held = CollectionState(self.multiworld), set()
            for item in pool[:len(pool) // 2]:
                state.collect(item, prevent_sweep=True)
                for name, rule in rules:
                    now = rule(state)
                    self.assertFalse(name in held and not now,
                                     f"{scenario.scenario_name}: {name} fell out on {item.name}")
                    if now:
                        held.add(name)


class TestTheRule(BudgetTestBase):
    def resolved(self, scenario, location):
        return BudgetTotal(scenario=scenario, location=location).resolve(self.world)

    def test_every_pile_item_is_a_dependency(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, budget.order[0].location)
        dependencies = set(resolved.item_dependencies())
        for resource in Resource:
            for name, _ in contributors(resource):
                self.assertIn(name, dependencies)

    def test_everything_in_the_order_fits_with_every_item(self):
        state = self.multiworld.get_all_state(False)
        for scenario in self.world.pool.scenarios.included:
            for entry in self.budget(scenario).order:
                with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                    self.assertTrue(self.resolved(scenario, entry.location)(state))

    def test_an_empty_pile_affords_nothing_costly(self):
        state = CollectionState(self.multiworld)
        for entry in self.budget(Age2ScenarioData.AP_ATTILA_1).order:
            resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, entry.location)
            if resolved.requirement(None).cost:
                self.assertFalse(resolved(state), entry.location.name)
                break

    def test_a_location_outside_the_order_is_never_afforded(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        outside = next(building for building in Age2BuildingData
                       if budget.get_priced_item(building) is None)
        self.assertTrue(self.resolved(Age2ScenarioData.AP_ATTILA_1, outside).always_false)

    def test_the_breakdown_adds_up_to_the_requirement(self):
        """The long view a later /explain + /more shows: it has to describe the same total."""
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, budget.order[-1].location)
        state = self.multiworld.get_all_state(False)
        breakdown = resolved.breakdown(state)
        self.assertEqual(breakdown["requirement"], resolved.requirement(state).cost)
        self.assertEqual(breakdown["scenario"], "The Scourge of God")
        self.assertIn("easy_sources", breakdown)
        self.assertEqual(resolved.breakdown()["waived"], [])

    def test_the_explanation_names_the_scenario_and_totals(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        text = self.resolved(Age2ScenarioData.AP_ATTILA_1, budget.order[-1].location).explain_str()
        self.assertIn("The Scourge of God", text)
        self.assertIn("food", text)
class TestRequiredPurchases(BudgetTestBase):
    """Joan 3 cannot be crossed without a Transport Ship: the scenario buys one, unless the
    Transport item hands it the boats."""

    SHIP = Age2UnitData.TRANSPORT_SHIP

    def joan_3(self):
        if Age2ScenarioData.AP_JOAN_3 not in self.world.pool.scenarios.included:
            self.skipTest("Joan 3 is not in this playthrough")
        return self.budget(Age2ScenarioData.AP_JOAN_3)

    def test_the_ship_leads_its_age(self):
        """Only the ship's own precursors come before it in its age."""
        budget = self.joan_3()
        order = [entry.location for entry in budget.order]
        ship = budget.order[order.index(self.SHIP)]
        its_own = {precursor.location for precursor in budget._precursors[self.SHIP]}
        self.assertEqual([], [entry.location for entry in budget.order[:order.index(self.SHIP)]
                              if entry.age == ship.age and entry.location not in its_own])

    def test_the_transport_item_spares_the_purchase(self):
        """With the boats in hand nothing pays for the ship, nor for what only it needed."""
        budget = self.joan_3()
        spared = frozenset({self.SHIP})
        only_for_ship = ({precursor.location for precursor in budget._precursors[self.SHIP]}
                         - {precursor.location for entry in budget._initial_order
                            if entry.location is not self.SHIP
                            for precursor in (*budget._precursors[entry.location], entry)})
        self.assertFalse(({self.SHIP} | only_for_ship) & budget.needed(spared))
        for entry in budget.order:
            if entry.location is self.SHIP:
                continue   # its own location still pays for itself
            with self.subTest(entry.location.name):
                need = budget.running_total_for(entry.location, spared)
                self.assertNotIn(self.SHIP.line, {price.identity for price in need.own_price})

    def test_a_switch_only_ever_lowers_the_total(self):
        """Standing a building up or sparing a purchase can only take cost away, so turning
        any switch on never turns a rule from true to false."""
        for scenario in self.world.pool.scenarios.included:
            for entry in self.budget(scenario).order:
                resolved = BudgetTotal(scenario=scenario,
                                       location=entry.location).resolve(self.world)
                costs = [dict(total.cost) for total in resolved.table.totals_by_mask]
                for mask, bit in itertools.product(range(len(costs)),
                                                   range(len(resolved.table.waivers))):
                    with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                        for resource, amount in costs[mask | 1 << bit].items():
                            self.assertLessEqual(amount, costs[mask].get(resource, 0))


class TestTheTransportIsACrossing(TestRequiredPurchases):
    """The given Transport is a crossing of its own, not a discount on building one. No Dock
    location and no ship units here, so until something after the ship needs a Dock for itself -
    a Dock tech - the Transport in hand means no later location is charged one."""

    def setUp(self) -> None:
        self.build(**{**HARD, "shuffle_buildings": {"Tech"}, "unitsanity": Unitsanity.option_none})

    def test_the_transport_item_lets_later_totals_off_the_dock(self):
        budget = self.joan_3()
        dock = Age2BuildingData.DOCK
        order = [entry.location for entry in budget.order]
        self.assertNotIn(dock, order, "a Dock location would owe the Dock whatever crosses")

        transport = Age2ItemData.AP_JOAN_3_TRANSPORT.item_name
        with_boats, without_boats = self.state_without(), self.state_without(transport)
        checked = 0
        for entry in budget.order[order.index(self.SHIP) + 1:]:
            if dock in self.cost_of(budget, entry.location).buildings:
                break   # from here on the Dock is owed whatever crosses the water
            resolved = BudgetTotal(scenario=Age2ScenarioData.AP_JOAN_3,
                                   location=entry.location).resolve(self.world)
            with self.subTest(entry.location.name):
                self.assertIn(dock, resolved.requirement(without_boats).buildings)
                self.assertNotIn(dock, resolved.requirement(with_boats).buildings)
                checked += 1
        self.assertTrue(checked, "nothing between the ship and a Dock of its own to check")


class TestCouldEverHave(BudgetTestBase):
    def test_a_fixed_force_scenario_can_build_nothing(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_1)
        self.assertFalse(any(budget.scenario.budget.could_have(building)
                             for building in Age2BuildingData))


class TestNeverLaterThanEasySources(BudgetTestBase):
    """The budget only ever adds a way in: wherever an easy source of everything a location
    costs would put it in logic, the location's real rule must agree."""

    def test_the_budget_never_takes_a_location_away(self):
        import random
        rng = random.Random(0)
        pool = list(self.multiworld.itempool)
        states = [CollectionState(self.multiworld), self.multiworld.get_all_state(False)]
        for size in (len(pool) // 4, len(pool) // 2, 3 * len(pool) // 4):
            for _ in range(3):
                state = CollectionState(self.multiworld)
                for item in rng.sample(pool, size):
                    state.collect(item, prevent_sweep=True)
                states.append(state)
        for scenario in self.world.rules.logic.scenarios:
            economy = scenario.economy
            pairs = []
            for tech in self.world.pool.techs.shuffled:
                priced = [resource for resource, amount in tech.cost.items() if amount > 0]
                structure = scenario.techs.can_research_structurally(tech)
                pairs.append((tech.name, structure & economy.can_sustain(priced),
                              scenario.techs.can_research(tech)))
            for building in self.world.pool.buildings.locations:
                priced = [resource for resource, amount in building.cost.items() if amount > 0]
                structure = scenario.buildings.can_build_building(building)
                pairs.append((building.name, structure & economy.can_sustain(priced),
                              structure & economy.can_pay(building.cost, building)))
            for name, easy, real in pairs:
                easy, real = easy.resolve(self.world), real.resolve(self.world)
                for state in states:
                    if easy(state) and not real(state):
                        self.fail(f"{scenario.scenario.scenario_name}: {name} is in logic on easy "
                                  f"sources alone but not under its real rule")
