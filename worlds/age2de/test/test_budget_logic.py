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
from ..logic.budget.BudgetOrder import budget_order
from ..logic.budget.BudgetTotal import BudgetTotal
from ..logic.budget.Requirement import required
from ..logic.budget.BudgetSource import RELIC_ALLOWANCE, SOURCE_ALLOWANCE, bootstrap, pays
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

    def cost_of(self, budget, location, waived: frozenset = frozenset()):
        return required(budget.plan([budget.priced(location)]), waived)


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
        self.assertIsNone(budget.priced(Age2AgeData.FEUDAL))
        cost = self.cost_of(budget, Age2TechData.TOWN_WATCH)
        self.assertEqual(cost.ages, [])


class TestPrerequisiteTechs(BudgetTestBase):
    def test_town_patrol_pays_for_town_watch_from_the_dark_age(self):
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        plan = budget.plan([budget.priced(Age2TechData.TOWN_PATROL)])
        own = plan.own_cost()
        expected = {resource: Age2TechData.TOWN_PATROL.cost.get(resource, 0)
                    + Age2TechData.TOWN_WATCH.cost.get(resource, 0) for resource in Resource}
        self.assertEqual(own, {resource: amount for resource, amount in expected.items() if amount})

    def test_a_castle_start_has_town_watch_for_free(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_4)
        plan = budget.plan([budget.priced(Age2TechData.TOWN_PATROL)])
        self.assertEqual(plan.own_cost(), {resource: amount for resource, amount
                                          in Age2TechData.TOWN_PATROL.cost.items() if amount})

    def test_an_upgraded_unit_pays_for_its_upgrade_chain(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_4)
        unit = Age2UnitData.TWO_HANDED_SWORDSMAN
        priced = budget.priced(unit)
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
        archer = budget.priced(Age2UnitData.ARCHER)
        crossbow = budget.priced(Age2UnitData.CROSSBOWMAN)
        self.assertIsNotNone(archer)
        self.assertIsNotNone(crossbow)
        both = budget.plan([archer, crossbow]).own_cost()
        alone = budget.plan([crossbow]).own_cost()
        self.assertEqual(both, alone)


class TestTheVillager(BudgetTestBase):
    def test_the_villager_costs_the_food_that_staffs_a_base(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_2)
        plan = budget.plan([budget.priced(VILLAGER)])
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
            position = {entry.location: index for index, entry in enumerate(order)}
            for index, entry in enumerate(order):
                charged = required(budget.plan(order[:index + 1]), frozenset()).buildings
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
                self.assertEqual([], budget.order)

    def test_what_is_kept_could_be_paid_for(self):
        """With every starting resource, every building standing and every source brought in,
        seeds paid for, the whole order fits: pruning keeps nothing that could never go true."""
        for scenario in self.world.pool.scenarios.included:
            budget = self.budget(scenario)
            if not budget.order:
                continue
            pile = {resource: self.world.pool.resources.totals[resource]
                    for resource in budget.max_budget()}
            every_waiver = frozenset(budget.waivers)
            need = budget.plan(budget.order)
            requirement = required(need, every_waiver)
            with self.subTest(scenario.scenario_name):
                self.assertTrue(pays(pile, dict(requirement.cost), list(range(len(budget.ways))),
                                     budget.ways,
                                     budget.seed_parts(need, requirement, every_waiver),
                                     budget.worth))


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
                       if budget.priced(building) is None)
        self.assertTrue(self.resolved(Age2ScenarioData.AP_ATTILA_1, outside).always_false)

    def test_the_breakdown_adds_up_to_the_requirement(self):
        """The long view a later /explain + /more shows: it has to describe the same total."""
        budget = self.budget(Age2ScenarioData.AP_ATTILA_1)
        resolved = self.resolved(Age2ScenarioData.AP_ATTILA_1, budget.order[-1].location)
        state = self.multiworld.get_all_state(False)
        breakdown = resolved.breakdown(state)
        self.assertEqual(breakdown["requirement"], resolved.requirement(state).cost)
        self.assertEqual(breakdown["scenario"], "The Scourge of God")
        self.assertTrue(breakdown["sources_on"])
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
        self.assertTrue(ship.item.first_in_age)
        its_own = {precursor.location for precursor in budget._precursors[self.SHIP]}
        self.assertEqual([], [entry.location for entry in budget.order[:order.index(self.SHIP)]
                              if entry.age == ship.age and entry.location not in its_own])

    def test_the_transport_item_spares_the_purchase(self):
        """With the boats in hand nothing pays for the ship, nor for what only it needed."""
        budget = self.joan_3()
        spared = frozenset({self.SHIP})
        only_for_ship = ({precursor.location for precursor in budget._precursors[self.SHIP]}
                         - {precursor.location for entry in budget._base
                            if entry.location is not self.SHIP
                            for precursor in (*budget._precursors[entry.location], entry)})
        self.assertFalse(({self.SHIP} | only_for_ship) & budget.needed(spared))
        for entry in budget.order:
            if entry.location is self.SHIP:
                continue   # its own location still pays for itself
            with self.subTest(entry.location.name):
                need = budget.need_for(entry.location, spared)
                self.assertNotIn(self.SHIP.line, {identity for identity, _ in need.own})

    def test_a_switch_only_ever_lowers_the_total(self):
        """Standing a building up or sparing a purchase can only take cost away, so turning
        any switch on never turns a rule from true to false."""
        for scenario in self.world.pool.scenarios.included:
            for entry in self.budget(scenario).order:
                resolved = BudgetTotal(scenario=scenario,
                                       location=entry.location).resolve(self.world)
                costs = [dict(cost) for cost in resolved.costs]
                for mask, bit in itertools.product(range(len(costs)),
                                                   range(len(resolved.switches))):
                    with self.subTest(f"{scenario.scenario_name}: {entry.location.name}"):
                        for resource, amount in costs[mask | 1 << bit].items():
                            self.assertLessEqual(amount, costs[mask].get(resource, 0))


class TestSourcesPayForTheirSeeds(BudgetTestBase):
    """A source brings nothing in until its seed stands: boats want a Dock and a Fishing Ship, and
    the wood for them has to be in hand first - banked, or chopped by a source already working."""

    def find(self, wanted):
        """A resolved total in some scenario whose sources include every way `wanted` asks for:
        name -> the part identities that way's seed must be exactly, none already bought."""
        for scenario in self.world.pool.scenarios.included:
            for entry in self.budget(scenario).order:
                resolved = BudgetTotal(scenario=scenario, location=entry.location).resolve(self.world)
                if not hasattr(resolved, "ways"):
                    continue
                found = {}
                for name, identities in wanted.items():
                    for way, (source, _) in enumerate(resolved.ways):
                        parts = resolved.parts[0][way]
                        if (resolved.sources[source][0] == name
                                and {part.identity for part in parts} == identities
                                and not any(part.in_requirement for part in parts)):
                            found[name] = way
                            break
                if len(found) == len(wanted):
                    return resolved, found
        self.skipTest("no scenario in this seed has those ways")

    BOAT = {("building", Age2BuildingData.DOCK), ("own", Age2UnitData.FISHING_SHIP.line)}
    CAMP = {("building", Age2BuildingData.LUMBER_CAMP)}

    @staticmethod
    def search(resolved) -> tuple:
        """The rest of what the search is given, with no switch on."""
        return resolved.ways, resolved.parts[0], resolved.sources

    def pile(self, wood: int) -> dict:
        return {Resource.FOOD: 0, Resource.WOOD: wood, Resource.GOLD: 0, Resource.STONE: 0}

    def test_no_wood_no_boats(self):
        resolved, ways = self.find({"fish": self.BOAT})
        need = {Resource.FOOD: 200}
        self.assertIsNone(bootstrap(self.pile(0), need, [ways["fish"]], *self.search(resolved)))
        self.assertIsNotNone(bootstrap(self.pile(225), need, [ways["fish"]], *self.search(resolved)))

    def test_chopping_can_pay_for_the_boats(self):
        """100 wood puts up a Lumber Camp; what it brings in pays for the Dock and the ship."""
        resolved, ways = self.find({"fish": self.BOAT, "chop": self.CAMP})
        need = {Resource.FOOD: 200}
        self.assertIsNone(bootstrap(self.pile(100), need, [ways["fish"]], *self.search(resolved)))
        found = bootstrap(self.pile(100), need, [ways["fish"], ways["chop"]],
                          *self.search(resolved))
        self.assertIsNotNone(found)
        self.assertEqual({ways["fish"], ways["chop"]}, set(found[0]))

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


class TestCouldEverHave(BudgetTestBase):
    def test_a_fixed_force_scenario_can_build_nothing(self):
        budget = self.budget(Age2ScenarioData.AP_JOAN_1)
        self.assertFalse(any(budget.could_have(building)
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
