"""Universal Tracker's /explain used to print the whole rule as one paragraph: every scenario's
unlock, structure and payment ORed together inline, thousands of characters for one unit. These pin
the indented answer that replaced it - and that it never disagrees with the rule it explains."""
import random
import re

from BaseClasses import CollectionState

from .bases import Age2RuleTestBase
from ..Options import ShuffleVillager, Techsanity, Unitsanity
from ..explain.Explainer import Explainer, Status
from ..explain.Layout import _ranges
from ..explain.Layout import LOG_WIDTH, SAYS, WIDTH, Lines, text, truth
from ..explain.Lookup import find
from ..explain.Routes import routes_for
from ..locations.Locations import Age2ScenarioLocationData

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
        name = next(name for name in self.explained()
                    if not isinstance(find(self.world, name)[1], Age2ScenarioLocationData))
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
                location = self.multiworld.get_location(name, self.world.player)
                # A scenario's own location leaves its unlock to the region it sits in.
                holds = (location.can_reach(state) if isinstance(data, Age2ScenarioLocationData)
                         else location.access_rule(state))
                with self.subTest(name):
                    self.assertEqual(holds, available)



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


class TestTheCampaignDrill(ExplainTestBase):
    """The campaign level lists each chapter offering the route once, in order, True where it has
    the location on that route - the same lines as the top level's campaign block."""

    def test_each_chapter_once_with_its_status(self):
        explainer = Explainer(self.world)
        state = self.states()[-1]
        checked = 0
        for name in self.explained()[::7]:
            _, data = find(self.world, name)
            for route in routes_for(self.world, data):
                for campaign in self.world.pool.campaigns.enabled:
                    expected = []
                    for scenario in self.world.pool.scenarios.in_campaign(campaign):
                        status = explainer._status(route, scenario, state)
                        if status is not None:
                            expected.append(f"{scenario.chapter}. {scenario.scenario_name} -> "
                                            + str(status is Status.AVAILABLE))
                    if not expected:
                        continue
                    shown = [line.strip().split("  [")[0]
                             for line in explainer._campaign_drill(name, route, campaign, state).plain().split("\n")
                             if re.match(r"^ {12}\d+\. ", line)]
                    with self.subTest(f"{name} / {route.label} / {campaign.campaign_name}"):
                        self.assertEqual(expected, shown)
                    checked += 1
        self.assertGreater(checked, 0)


class TestTheLayout(ExplainTestBase):
    def test_no_line_runs_past_the_width(self):
        """The log loses the indentation of any line it has to wrap itself."""
        state = self.states()[-1]
        for name in self.explained():
            for line in self.plain(name, state).split("\n"):
                with self.subTest(name):
                    self.assertLessEqual(len(line), LOG_WIDTH, line)

    def test_each_chapter_says_whether_it_has_it_on_the_route(self):
        """Under each route, the campaign item, then every chapter offering the route, True where
        that chapter has the location on it by some means."""
        explainer = Explainer(self.world)
        state = self.states()[-1]
        checked = 0
        for name in self.explained()[::3]:
            _, data = find(self.world, name)
            if isinstance(data, Age2ScenarioLocationData):
                continue   # one scenario's own: no campaign rows, straight to the scenario
            expected = []
            for route in routes_for(self.world, data):
                for campaign in self.world.pool.campaigns.enabled:
                    for scenario in self.world.pool.scenarios.in_campaign(campaign):
                        status = explainer._status(route, scenario, state)
                        if status is not None:
                            expected.append(f"{scenario.chapter}. {scenario.scenario_name} -> "
                                            f"{status is Status.AVAILABLE}")
            shown = [line.strip().split("  [")[0] for line in self.plain(name, state).split("\n")
                     if re.match(r"^ {12}\d+\. .+ -> (True|False)", line)]
            with self.subTest(name):
                self.assertEqual(expected, shown)
            checked += 1
        self.assertGreater(checked, 0)

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

    def test_a_long_statement_continues_after_its_rule(self):
        lines = Lines()
        lines.add(3, text("Counters the Cavalry Archer Line in the Imperial Age"),
                  text(SAYS), truth(False), text("  [/explain_more 4]"))
        self.assertEqual(
            [" " * 12 + "Counters the Cavalry Archer Line in the Imperial Age",
             " " * 16 + "-> False  [/explain_more 4]"],
            lines.plain().split("\n"),
        )

    def test_a_statement_within_the_width_stays_on_one_line(self):
        lines = Lines()
        lines.add(1, text("Has a base"), text(SAYS), truth(True))
        self.assertEqual(["    Has a base -> True"], lines.plain().split("\n"))


class TestDirectCommands(ExplainTestBase):
    """/explain [campaign or scenario] <location> goes straight to that branch."""

    def plain_of(self, typed: str) -> str | None:
        parts = self.world.explain_rule(typed, CollectionState(self.multiworld))
        return None if parts is None else "".join(part["text"] for part in parts)

    def a_location(self) -> str:
        from ..explain.Lookup import _BY_NAME
        names = {location.name for location in self.multiworld.get_locations(self.world.player)}
        return next(name for name, data in _BY_NAME.items() if name in names and routes_for(self.world, data))

    def test_each_form_answers(self):
        name = self.a_location()
        campaign = self.world.pool.campaigns.enabled[0]
        scenario = self.world.pool.scenarios.in_campaign(campaign)[0]
        word = campaign.campaign_name.split()[0]
        for typed in (f"{campaign.campaign_name} {name}", f"{word} {name}",
                      f"{word} {scenario.chapter} {name}", f"{scenario.scenario_name} {name}",
                      f"{word} {scenario.chapter} {name.lower()}"):
            with self.subTest(typed):
                answer = self.plain_of(typed)
                self.assertIsNotNone(answer)
                self.assertNotIn("No location here matches", answer)

    def test_a_scenario_view_names_the_scenario(self):
        name = self.a_location()
        scenario = self.world.pool.scenarios.included[0]
        self.assertTrue(self.plain_of(f"{scenario.scenario_name} {name}").startswith(
            f"{name} in {scenario.scenario_name}"))

    def test_a_scenario_location_goes_straight_to_its_scenario(self):
        scenario = self.world.pool.scenarios.included[0]
        word = scenario.campaign.campaign_name.split()[0]
        expected = f"Victory in {scenario.scenario_name}"
        for typed in (f"{scenario.scenario_name}: Victory", f"{word} {scenario.chapter} Victory"):
            with self.subTest(typed):
                answer = self.plain_of(typed)
                self.assertTrue(answer.startswith(expected), answer)
                self.assertIn("Completes it", answer)

    def test_a_scenario_location_elsewhere_is_not_offered(self):
        first, second = self.world.pool.scenarios.included[:2]
        word = second.campaign.campaign_name.split()[0]
        self.assertEqual("Victory -> Not Offered",
                         self.plain_of(f"{word} {second.chapter} {first.scenario_name}: Victory"))

    def test_a_campaign_outside_the_seed_says_so(self):
        from ..locations.Campaigns import Age2CampaignData
        missing = next((campaign for campaign in Age2CampaignData
                        if campaign not in self.world.pool.campaigns.enabled), None)
        if missing is None:
            self.skipTest("every campaign is in this seed")
        self.assertEqual(f"{missing.campaign_name} isn't in this seed.",
                         self.plain_of(f"{missing.campaign_name} {self.a_location()}"))


class TestEasySourceCommands(ExplainTestBase):
    """/explain [campaign or scenario] Easy <resource> Source opens the easy source at that level."""

    def test_each_level_answers_with_the_question(self):
        from ..items.Items import Resource
        state = CollectionState(self.multiworld)
        campaign = self.world.pool.campaigns.enabled[0]
        scenario = self.world.pool.scenarios.in_campaign(campaign)[0]
        word = campaign.campaign_name.split()[0]
        for resource in (Resource.WOOD, Resource.FOOD, Resource.GOLD, Resource.STONE):
            noun = resource.name.lower()
            for typed, opens in ((f"Easy {noun} Source", f"Easy {noun.title()} Source"),
                                 (f"easy {noun}", f"Easy {noun.title()} Source"),
                                 (f"{word} Easy {noun} Source",
                                  f"Easy {noun.title()} Source\n    Has {campaign.campaign_name} Campaign"),
                                 (f"{word} {scenario.chapter} Easy {noun}", f"{scenario.scenario_name}: ")):
                with self.subTest(typed):
                    parts = self.world.explain_rule(typed, state)
                    self.assertIsNotNone(parts)
                    self.assertTrue("".join(part["text"] for part in parts).startswith(opens))

    def test_a_scenario_view_agrees_with_the_question(self):
        from ..items.Items import Resource
        for state in self.states():
            for scenario in self.world.pool.scenarios.included:
                sl = self.world.rules.logic.for_scenario(scenario)
                held = sl.economy.has_easy_source(Resource.WOOD).resolve(self.world)(state)
                parts = Explainer(self.world)._easy_view(Resource.WOOD, scenario.campaign, scenario, state).parts()
                question = next(part for part in parts if part["text"] == "Can easily gather wood")
                with self.subTest(scenario.name):
                    self.assertEqual("green" if held else "salmon", question["color"])


class TestNoMarkerOpensToOneLine(ExplainTestBase):
    """A name or question that would open to a single line, or to nothing, is drawn as a chain or
    with no marker: every question view behind a marker has a title and at least two lines."""

    ROUTE_WORDS = ("Builds it", "Trains it", "Researches it", "Reaches it", "Does the job",
                   "Starts with it", "Handed over")

    def test_every_question_marker_opens_to_several_lines(self):
        explainer = Explainer(self.world)
        state = self.states()[-1]
        checked = 0
        word = self.world.pool.campaigns.enabled[0].campaign_name.split()[0]
        for name in self.explained()[::5]:
            for scenario in self.world.pool.scenarios.included[:3]:
                if not explainer.explain_rule(f"{word} {scenario.chapter} {name}", state):
                    continue
                for title, build in list(explainer._entries):
                    if (title.startswith("what ") or "(in " in title
                            or any(f": {words}" in title for words in self.ROUTE_WORDS)):
                        continue
                    shown = build(state).plain().split("\n")
                    with self.subTest(title):
                        self.assertGreaterEqual(len(shown), 3, "\n".join(shown))
                    checked += 1
        self.assertGreater(checked, 0)
