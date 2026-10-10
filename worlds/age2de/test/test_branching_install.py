"""The objectives panel used to list both branching routes at once.

`scenario_branching` only ever changed which locations generation created; the scenarios still
shipped every branching trigger enabled, and all twenty display as objectives. An `any` seed
therefore showed five Attila 1 objectives that were never locations, next to the one that was.
`/install` now turns off the triggers for the route the seed did not take.

`trigger_call` is a hand-maintained mirror of the XS wrappers, so the checks that it is
complete, unique and correct live here rather than as import-time asserts.
"""
import unittest

from .test_campaign_bundle import SEED
from ..AoE2ScenarioParser.datasets.effects import EffectId
from ..campaign import ScenarioParser
from ..client.handlers.InstallHandler import InstallHandler
from ..generation import Identity
from ..locations.Campaigns import Age2CampaignData
from ..locations.Locations import (TYPE_TO_LOCATIONS, Age2LocationType,
                                   Age2ScenarioLocationData)
from ..locations.Scenarios import Age2ScenarioData
from ..Options import ScenarioBranching

BRANCHING_SCENARIOS = (Age2ScenarioData.AP_ATTILA_1, Age2ScenarioData.AP_ATTILA_4,
                       Age2ScenarioData.AP_JOAN_2, Age2ScenarioData.AP_JOAN_3)
NULL = chr(0)

BRANCHING_TYPES = (Age2LocationType.OBJECTIVE_BRANCHING_ALL,
                   Age2LocationType.OBJECTIVE_BRANCHING_ANY)
BRANCHING_LOCATIONS = [location for type in BRANCHING_TYPES
                       for location in TYPE_TO_LOCATIONS[type]]


class FakeEffect:
    def __init__(self, message: str = "", effect_type: int = EffectId.SCRIPT_CALL):
        self.effect_type = effect_type
        self.message = message


class FakeTrigger:
    def __init__(self, name: str, effects: list, enabled: int = 1):
        self.name = name
        self.effects = effects
        self.enabled = enabled


class FakeScenario:
    def __init__(self, triggers: list):
        self.trigger_manager = type("Manager", (), {"triggers": triggers})()


def branching_locations(scenario: Age2ScenarioData) -> list[Age2ScenarioLocationData]:
    return [location for location in BRANCHING_LOCATIONS if location.scenario == scenario]


def wrappers_of(locations) -> frozenset[str]:
    return frozenset(location.trigger_call for location in locations)


class TestTheWrapperNames(unittest.TestCase):
    def test_every_branching_location_names_a_trigger_call(self):
        for location in BRANCHING_LOCATIONS:
            with self.subTest(location.name):
                self.assertTrue(location.trigger_call)

    def test_no_wrapper_name_is_claimed_twice(self):
        names = [location.trigger_call for location in BRANCHING_LOCATIONS]
        self.assertEqual(len(names), len(set(names)))

    def test_only_branching_locations_name_one(self):
        branching = set(BRANCHING_LOCATIONS)
        for location in Age2ScenarioLocationData:
            if location not in branching:
                with self.subTest(location.name):
                    self.assertEqual(location.trigger_call, "")

    def test_the_branching_locations_sit_in_four_scenarios(self):
        self.assertEqual({location.scenario for location in BRANCHING_LOCATIONS},
                         set(BRANCHING_SCENARIOS))


class TestReadingTheScriptCall(unittest.TestCase):
    def test_a_plain_call_resolves(self):
        self.assertEqual(ScenarioParser.effect_script_call(FakeEffect("KillScout();")),
                         {"KillScout"})

    def test_the_parsers_null_trail_is_ignored(self):
        self.assertEqual(ScenarioParser.effect_script_call(FakeEffect("KillScout();" + NULL)),
                         {"KillScout"})

    def test_a_message_with_two_statements_resolves_both(self):
        self.assertEqual(
            ScenarioParser.effect_script_call(FakeEffect("FreeScout(); KillScout();")),
            {"FreeScout", "KillScout"})

    def test_an_empty_message_resolves_to_nothing(self):
        self.assertEqual(ScenarioParser.effect_script_call(FakeEffect("")), set())

    def test_only_script_call_effects_are_read(self):
        trigger = FakeTrigger("AP Kill Scout", [
            FakeEffect("KillScout();", EffectId.CHANGE_VARIABLE)])
        self.assertEqual(ScenarioParser.trigger_calls_xs_script(trigger), set())


class TestTheDisableStep(unittest.TestCase):
    def scenario(self) -> FakeScenario:
        return FakeScenario([
            FakeTrigger("AP Resolve Scout Any", [FakeEffect("ResolveScoutAny();")]),
            FakeTrigger("AP Kill Scout", [FakeEffect("KillScout();")]),
            FakeTrigger("AP Defeat Burgundy All", [
                FakeEffect("DefeatBurgundyAll();"),
                FakeEffect("Burgundy Handled", EffectId.CHANGE_VARIABLE)]),
            FakeTrigger("AP Victory", [FakeEffect("Victory();")]),
        ])

    def test_only_the_named_triggers_are_turned_off(self):
        scenario = self.scenario()
        changed = ScenarioParser.disable_triggers([
            Age2ScenarioLocationData.ATT1_KILL_SCOUT,
            Age2ScenarioLocationData.ATT4_DEFEAT_BURGUNDY_ALL])(scenario)
        self.assertTrue(changed)
        self.assertEqual({trigger.name: trigger.enabled
                          for trigger in scenario.trigger_manager.triggers},
                         {"AP Resolve Scout Any": 1, "AP Kill Scout": 0,
                          "AP Defeat Burgundy All": 0, "AP Victory": 1})

    def test_a_disabled_trigger_keeps_its_other_effects(self):
        scenario = self.scenario()
        ScenarioParser.disable_triggers(
            [Age2ScenarioLocationData.ATT4_DEFEAT_BURGUNDY_ALL])(scenario)
        burgundy = scenario.trigger_manager.triggers[2]
        self.assertEqual([effect.effect_type for effect in burgundy.effects],
                         [EffectId.SCRIPT_CALL, EffectId.CHANGE_VARIABLE])

    def test_a_pass_with_nothing_to_turn_off_reports_no_change(self):
        scenario = self.scenario()
        self.assertFalse(ScenarioParser.disable_triggers(
            [Age2ScenarioLocationData.JOAN3_DESTROY_ONE_CASTLE])(scenario))

    def test_an_already_disabled_trigger_is_not_a_change(self):
        scenario = FakeScenario([
            FakeTrigger("AP Kill Scout", [FakeEffect("KillScout();")], enabled=0)])
        self.assertFalse(ScenarioParser.disable_triggers(
            [Age2ScenarioLocationData.ATT1_KILL_SCOUT])(scenario))


class TestWhatTheInstallDecides(unittest.TestCase):
    def handler(self, mode=None, **slot_data) -> InstallHandler:
        if mode is not None:
            slot_data[ScenarioBranching.internal_name] = mode
        handler = InstallHandler()
        handler.setup(list(Age2CampaignData), 3, Identity.seed_tag(SEED, 3), "Dave",
                      slot_data or None, ())
        return handler

    def turned_off(self, mode) -> dict:
        return {scenario.file_stem: sorted(location.trigger_call for location in locations)
                for scenario, locations in self.handler(mode)._disabled_triggers.items()}

    def test_any_turns_off_the_all_route(self):
        self.assertEqual(self.turned_off(ScenarioBranching.option_any)["AP_Attila_1"],
                         ["BetrayBleda", "BlowBledaOff", "FreeScout", "KillScout", "KillTheBoar"])

    def test_all_turns_off_the_any_route(self):
        self.assertEqual(self.turned_off(ScenarioBranching.option_all)["AP_Attila_1"],
                         ["ResolveScoutAny"])

    def test_a_seed_without_the_option_turns_nothing_off(self):
        self.assertEqual(self.handler()._disabled_triggers, {})
        self.assertEqual(self.handler().steps_for(Age2ScenarioData.AP_ATTILA_1), [])

    def test_a_scenario_with_no_branching_locations_is_never_parsed(self):
        handler = self.handler(ScenarioBranching.option_any)
        self.assertEqual(handler.steps_for(Age2ScenarioData.AP_ATTILA_2), [])

    def test_a_scenario_with_no_locations_on_the_unused_route_is_never_parsed(self):
        # Joan 2's four castles are all OBJECTIVE_BRANCHING_ALL, so `all` leaves it alone.
        handler = self.handler(ScenarioBranching.option_all)
        self.assertNotIn(Age2ScenarioData.AP_JOAN_2, handler._disabled_triggers)
        self.assertEqual(handler.steps_for(Age2ScenarioData.AP_JOAN_2), [])

    def test_a_campaign_that_is_not_installed_is_left_out(self):
        handler = InstallHandler()
        handler.setup([Age2CampaignData.JOAN], 3, Identity.seed_tag(SEED, 3), "Dave",
                      {ScenarioBranching.internal_name: ScenarioBranching.option_any}, ())
        self.assertEqual(set(handler._disabled_triggers),
                         {Age2ScenarioData.AP_JOAN_2, Age2ScenarioData.AP_JOAN_3})

    def test_the_rebase_and_branching_steps_compose(self):
        handler = self.handler(ScenarioBranching.option_any, techsanity=3, tech_behavior=0,
                               shuffle_unique_techs=1, existing_techs=1)
        steps = handler.steps_for(Age2ScenarioData.AP_JOAN_2)
        self.assertEqual(len(steps), 2)
        self.assertIs(steps[0], ScenarioParser.rebase_to_dark)

    def test_only_the_four_branching_scenarios_are_parsed(self):
        handler = self.handler(ScenarioBranching.option_any)
        parsed = [scenario for scenario in Age2ScenarioData if handler.steps_for(scenario)]
        self.assertEqual(set(parsed), set(BRANCHING_SCENARIOS))
