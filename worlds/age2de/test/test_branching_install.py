"""The objectives panel used to list both branching routes at once.

`scenario_branching` only ever changed which locations generation created; the scenarios still
shipped every branching trigger enabled, and all twenty display as objectives. An `any` seed
therefore showed five Attila 1 objectives that were never locations, next to the one that was.
`/install` now turns off the triggers for the route the seed did not take.

`trigger_call` is a hand-maintained mirror of the XS wrappers, so the checks that it is
complete, unique and correct live here rather than as import-time asserts.

The bundle-parsing cases at the bottom are the slowest in the suite and skip unless
AGEIPELAGO_PATH points at the Ageipelago checkout.
"""
import re
import tempfile
import unittest
from pathlib import Path

from .test_campaign_bundle import AGEIPELAGO_BUNDLES, SEED
from ..AoE2ScenarioParser.datasets.effects import EffectId
from ..AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from ..campaign import ScenarioParser
from ..campaign.CampaignReader import Campaign
from ..client.handlers.InstallHandler import InstallHandler
from ..generation import Identity
from ..locations.Campaigns import Age2CampaignData
from ..locations.Locations import (TYPE_TO_LOCATIONS, Age2LocationType,
                                   Age2ScenarioLocationData)
from ..locations.Scenarios import Age2ScenarioData
from ..Options import ScenarioBranching

AGEIPELAGO_XS = AGEIPELAGO_BUNDLES.parent / "xs"
AGEIPELAGO_SCENARIOS = AGEIPELAGO_BUNDLES.parent / "scenario"
BRANCHING_SCENARIOS = (Age2ScenarioData.AP_ATTILA_1, Age2ScenarioData.AP_ATTILA_4,
                       Age2ScenarioData.AP_JOAN_2, Age2ScenarioData.AP_JOAN_3)
WRAPPER = re.compile(r"void\s+(\w+)\s*\(\s*\)\s*\{(.*?)\}", re.DOTALL)
CHECK = re.compile(r"AP_Check_Location\s*\(\s*(\d+)\s*\)")
TRAILING_TAG = re.compile(r"\((?:Any|All)\)\s*$", re.IGNORECASE)
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


def read(body: bytes) -> AoE2DEScenario:
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder, "in.aoe2scenario")
        source.write_bytes(body)
        return AoE2DEScenario.from_file(str(source))


def bundle_bodies(campaign: Age2CampaignData) -> dict[str, bytes]:
    path = AGEIPELAGO_BUNDLES / Identity.source_campaign_file_name(campaign.file_stem)
    return {scenario.file_name: scenario.body for scenario in Campaign(str(path)).scenarios}


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
                               lock_techs=0, shuffle_unique_techs=1, existing_techs=1)
        steps = handler.steps_for(Age2ScenarioData.AP_JOAN_2)
        self.assertEqual(len(steps), 2)
        self.assertIs(steps[0], ScenarioParser.rebase_to_dark)

    def test_only_the_four_branching_scenarios_are_parsed(self):
        handler = self.handler(ScenarioBranching.option_any)
        parsed = [scenario for scenario in Age2ScenarioData if handler.steps_for(scenario)]
        self.assertEqual(set(parsed), set(BRANCHING_SCENARIOS))


@unittest.skipUnless(AGEIPELAGO_BUNDLES.is_dir(), "Set AGEIPELAGO_PATH to run this")
class TestAgainstTheAgeipelagoCheckout(unittest.TestCase):
    def test_every_trigger_call_resolves_to_its_recorded_location_id(self):
        found = {}
        for path in sorted(AGEIPELAGO_XS.glob("AP_*.xs")):
            for name, body in WRAPPER.findall(path.read_text(encoding="utf-8")):
                ids = CHECK.findall(body)
                if len(ids) == 1:
                    found[name] = int(ids[0])
        for location in BRANCHING_LOCATIONS:
            with self.subTest(location.name):
                self.assertIn(location.trigger_call, found)
                self.assertEqual(found[location.trigger_call], location.id)

    def test_every_branching_location_has_exactly_one_trigger_in_the_bundles(self):
        for campaign in Age2CampaignData:
            bodies = bundle_bodies(campaign)
            for scenario in BRANCHING_SCENARIOS:
                file_name = f"{scenario.file_stem}.aoe2scenario"
                if file_name not in bodies:
                    continue
                with self.subTest(scenario.file_stem):
                    wanted = wrappers_of(branching_locations(scenario))
                    counted = {name: 0 for name in wanted}
                    for trigger in read(bodies[file_name]).trigger_manager.triggers:
                        for name in ScenarioParser.trigger_calls_xs_script(trigger) & wanted:
                            counted[name] += 1
                    self.assertEqual(counted, {name: 1 for name in wanted})

    def test_a_real_scenario_survives_a_branching_pass(self):
        body = bundle_bodies(Age2CampaignData.ATTILA)["AP_Attila_1.aoe2scenario"]
        before = read(body).trigger_manager.triggers
        names = [trigger.name for trigger in before]
        for type, turned_off in ((Age2LocationType.OBJECTIVE_BRANCHING_ALL, 5),
                                 (Age2LocationType.OBJECTIVE_BRANCHING_ANY, 1)):
            with self.subTest(type=type.name):
                unused = [location for location
                          in branching_locations(Age2ScenarioData.AP_ATTILA_1)
                          if location.type == type]
                after = read(ScenarioParser.apply(
                    body, [ScenarioParser.disable_triggers(unused)]))
                triggers = after.trigger_manager.triggers
                self.assertEqual([trigger.name for trigger in triggers], names)
                flipped = [trigger.name for trigger, was in zip(triggers, before)
                           if trigger.enabled != was.enabled]
                self.assertEqual(len(flipped), turned_off)

    def test_the_branching_tags_are_gone_from_the_scenario_files(self):
        for scenario in BRANCHING_SCENARIOS:
            path = AGEIPELAGO_SCENARIOS / f"{scenario.file_stem}.aoe2scenario"
            wanted = wrappers_of(branching_locations(scenario))
            for trigger in AoE2DEScenario.from_file(str(path)).trigger_manager.triggers:
                if not ScenarioParser.trigger_calls_xs_script(trigger) & wanted:
                    continue
                with self.subTest(trigger.name):
                    self.assertNotIn("(Branching:", trigger.description)
                    self.assertNotRegex(trigger.description, TRAILING_TAG)
                    self.assertNotRegex(trigger.short_description, TRAILING_TAG)
                    self.assertEqual(trigger.description_stid, 0)
