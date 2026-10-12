"""Universal Tracker's /explain used to print the whole rule as one paragraph: every scenario's
unlock, structure and payment ORed together inline, thousands of characters for one unit. These pin
the indented answer that replaced it - and that it never disagrees with the rule it explains."""
import random

from BaseClasses import CollectionState

from .bases import Age2RuleTestBase
from ..Options import ShuffleVillager, Techsanity, Unitsanity
from ..explain.Explainer import Explainer, Status
from ..explain.Layout import _ranges
from ..explain.Layout import WIDTH, Lines, text
from ..explain.Lookup import find
from ..explain.Routes import routes_for

EVERYTHING = dict(techsanity=Techsanity.option_all, unitsanity=Unitsanity.option_all,
                  shuffle_villager=ShuffleVillager.option_include_professions, shuffle_ages=1)


class ExplainTestBase(Age2RuleTestBase):
    def setUp(self) -> None:
        self.build(**EVERYTHING)

    def states(self) -> list[CollectionState]:
        pool = list(self.multiworld.itempool)
        random.Random(7).shuffle(pool)
        states = [CollectionState(self.multiworld), self.multiworld.get_all_state(False)]
        for share in (4, 2):
            state = CollectionState(self.multiworld)
            for item in pool[:len(pool) // share]:
                state.collect(item, prevent_sweep=True)
            state.sweep_for_advancements()
            states.append(state)
        return states

    def explained(self) -> list[str]:
        return [location.name for location in self.multiworld.get_locations(self.world.player)
                if location.address is not None and find(self.world, location.name) is not None]

    def plain(self, typed: str, state: CollectionState) -> str:
        parts = self.world.explain_rule(typed, state)
        return "".join(part["text"] for part in parts)


class TestFindingTheLocation(ExplainTestBase):
    def test_a_name_it_does_not_cover_falls_back_to_ut(self):
        self.assertIsNone(self.world.explain_rule("nowhere at all", CollectionState(self.multiworld)))

    def test_a_loose_name_finds_the_location(self):
        name = self.explained()[0]
        self.assertTrue(self.plain(name.lower(), CollectionState(self.multiworld)).startswith(name))


class TestTheAnswerAgreesWithTheRule(ExplainTestBase):
    """The explanation asks the same pieces the rule is built from, so a chapter is available on
    some route exactly when the location's rule holds."""

    def test_available_somewhere_iff_the_rule_holds(self):
        explainer = Explainer(self.world)
        names = self.explained()
        self.assertTrue(names)
        for state in self.states():
            for name in names:
                _, data = find(self.world, name)
                available = any(
                    explainer._status(route, scenario, state) is Status.AVAILABLE
                        for route in routes_for(self.world, data)
                            for scenario in self.world.pool.scenarios.included
                )
                rule = self.multiworld.get_location(name, self.world.player).access_rule
                with self.subTest(name):
                    self.assertEqual(rule(state), available)



class TestCantMeansNever(ExplainTestBase):
    """"Can't train" is for a chapter no item still to come opens; one an item would open is
    "missing items"."""

    def test_never_does_not_depend_on_the_items_held(self):
        explainer = Explainer(self.world)
        states = self.states()
        for name in self.explained():
            _, data = find(self.world, name)
            for route in routes_for(self.world, data):
                for scenario in self.world.pool.scenarios.included:
                    never = {explainer._status(route, scenario, state) is Status.NEVER
                             for state in states}
                    with self.subTest(f"{name} / {scenario.name}"):
                        self.assertEqual(1, len(never))

    def test_every_item_leaves_nothing_missing(self):
        explainer = Explainer(self.world)
        everything = self.multiworld.get_all_state(False)
        for name in self.explained():
            _, data = find(self.world, name)
            for route in routes_for(self.world, data):
                for scenario in self.world.pool.scenarios.included:
                    with self.subTest(f"{name} / {scenario.name}"):
                        self.assertIsNot(Status.SHORT, explainer._status(route, scenario, everything))


class TestTheCampaignBudget(ExplainTestBase):
    def test_it_opens_on_the_full_total(self):
        """No title line: it opens on the first scenario's full total, no waiver holding."""
        from ..explain.Costs import Costs
        state = CollectionState(self.multiworld)
        _, data = find(self.world, "Build Market")
        route = routes_for(self.world, data)[0]
        offering = [self.world.rules.logic.for_scenario(scenario)
                    for scenario in self.world.pool.scenarios.included]
        costs = Costs(self.world, route, offering)
        for campaign in self.world.pool.campaigns.enabled:
            budgeted = [sl for sl in offering if sl.scenario.campaign is campaign
                        and costs._budget(sl) is not None]
            if not budgeted:
                continue
            first = costs.campaign_budget("Build Market", campaign.campaign_name, state).plain().split("\n")[0]
            with self.subTest(campaign.campaign_name):
                self.assertNotIn("grouped by", first)
                fulls = {"".join(f"{amount} {resource.name.lower()}, " for resource, amount in
                                 costs._budget(sl).table.totals_by_mask[0].cost).rstrip(", ")
                         for sl in budgeted}
                self.assertTrue(any(first.endswith(": " + full) for full in fulls), first)


class TestTheLayout(ExplainTestBase):
    def test_no_line_runs_past_the_width(self):
        """The log loses the indentation of any line it has to wrap itself."""
        state = self.states()[-1]
        for name in self.explained():
            for line in self.plain(name, state).split("\n"):
                with self.subTest(name):
                    self.assertLessEqual(len(line), WIDTH + 20, line)

    def test_one_line_per_campaign_per_route(self):
        state = self.states()[-1]
        campaigns = [campaign.campaign_name for campaign in self.world.pool.campaigns.enabled]
        for name in self.explained():
            counts: dict[str, int] = {}
            route = None
            for line in self.plain(name, state).split("\n"):
                if line.startswith("    ") and not line.startswith("        "):
                    route, counts = line.strip(), {}
                elif any(line.strip().startswith(f"{campaign}: ") for campaign in campaigns):
                    head = line.strip().split(":")[0]
                    counts[head] = counts.get(head, 0) + 1
                    with self.subTest(f"{name} / {route}"):
                        self.assertEqual(1, counts[head])

    def test_explain_more_always_answers(self):
        """UT reports a world that answers nothing as not supporting the command at all."""
        self.assertTrue(self.world.explain_more("1", CollectionState(self.multiworld)))


class TestRuns(Age2RuleTestBase):
    def test_chapters_merge_into_runs(self):
        self.assertEqual("1–3, 5", _ranges([1, 2, 3, 5]))
        self.assertEqual("4", _ranges([4]))

    def test_a_long_line_continues_one_level_deeper(self):
        lines = Lines()
        lines.add_segments(2, "Campaign: ", [[text("x" * 30)] for _ in range(4)])
        rendered = lines.plain().split("\n")
        self.assertGreater(len(rendered), 1)
        self.assertTrue(rendered[1].startswith(" " * 12))
        self.assertTrue(all(len(line) <= WIDTH for line in rendered))


class TestChargeNames(Age2RuleTestBase):
    """A unit price reads as what is trained, not as the line or the food it is kept under."""

    def test_the_villagers_food_is_three_villagers(self):
        from ..explain.Costs import _trained_name
        self.assertEqual("Train Villager x3", _trained_name(("own", "villager"), {}))

    def test_a_line_is_named_by_the_tier_the_order_trains(self):
        from ..explain.Costs import _trained_name
        from ..locations.Units import Age2UnitData
        line = Age2UnitData.MAN_AT_ARMS.line
        self.assertEqual("Train Man-at-Arms",
                         _trained_name(("own", line), {line: Age2UnitData.MAN_AT_ARMS}))


class TestBudgetedItems(ExplainTestBase):
    """/explain Budgeted Items: the seed's sample in its one order, less what no scenario's
    starting resources could ever pay for."""

    def test_it_lists_what_some_scenario_buys_in_the_seeded_order(self):
        from ..explain.Explainer import BUDGETED_ITEMS
        from ..logic.budget.BudgetItem import for_location
        budget = self.world.pool.budget
        from ..explain.Costs import budget_label
        from ..explain.Lookup import _BY_NAME
        from ..logic.budget.BudgetTotal import BudgetTotal
        most = self.world.rules.logic.most_pile

        def budgeted(location) -> bool:
            """In some scenario's order, with its pile able to pay some of what it costs."""
            route = next(route for route in routes_for(self.world, _BY_NAME[location.location_name])
                         if route.price is not None)
            own = [resource for resource, amount in route.price[1].items() if amount > 0]
            for scenario in self.world.pool.scenarios.included:
                total = BudgetTotal(scenario=scenario, location=location).resolve(self.world)
                if isinstance(total, BudgetTotal.Resolved) and any(
                        total.lowest(resource) <= most[resource] for resource in own):
                    return True
            return False

        expected = [budget_label(location) for location in sorted(
            (location for location in budget.entries if budgeted(location)),
            key=lambda location: (for_location(location).age, location is not for_location(location).age,
                                   budget.rank[location]))]
        listed = [line.strip().split(". ", 1)[1].split("  [")[0].rsplit(" (", 1)[0] for line in
                  "".join(part["text"] for part in self.world.explain_rule(
                      BUDGETED_ITEMS.lower(), CollectionState(self.multiworld))).split("\n")
                  if line.startswith("        ")]
        self.assertTrue(expected)
        self.assertEqual(expected, listed)
