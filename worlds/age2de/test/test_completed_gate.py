"""#208: in Universal Tracker a scenario's victory event - the door to the next scenario - is had
once the scenario is completed (its bit in `{team}_{player}_scenario_complete`), not once its win
rule holds. Generation keeps the win rule, and so does UT with deferred connections turned off."""
from BaseClasses import CollectionState
from test.general import setup_solo_multiworld

from .. import Age2World
from ..client.DataStorage import DataStorage
from ..client.handlers.CampaignHandler import CampaignHandler
from ..locations.Campaigns import Age2CampaignData
from .bases import Age2RuleTestBase

KEY = "{team}_{player}_scenario_complete"


class CompletedGateTestBase(Age2RuleTestBase):
    deferred: str | None = "default"

    def setUp(self) -> None:
        self.build()
        attila = self.world.pool.scenarios.in_campaign(Age2CampaignData.ATTILA)
        self.first, self.second = attila[0], attila[1]

    def build(self, **options) -> Age2World:
        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        if self.deferred is not None:
            world.multiworld.generation_is_fake = True
            world.multiworld.enforce_deferred_connections = self.deferred
        world.options.enabled_campaigns.value = set(self.campaigns)
        world.options.starting_campaigns.value = set(self.starting_campaigns)
        for name, value in options.items():
            getattr(world.options, name).value = value
        for step in ("generate_early", "create_regions", "create_items", "set_rules"):
            getattr(world, step)()
        self.world = world
        self.multiworld = world.multiworld
        return world

    def door(self, scenario) -> str:
        return f"{scenario.scenario_name}: Unlock Next Scenario"

    def victory(self, scenario) -> str:
        return f"{scenario.scenario_name}: Victory"

    def complete(self, *scenarios) -> None:
        field = DataStorage(self.world.pool.campaigns.enabled).scenario_field(scenarios)
        self.world.reconnect_found_entrances(KEY, field)

    def has(self, item: str, state: CollectionState) -> bool:
        return state.has(item, self.world.player)

    def plain(self, typed: str, state: CollectionState) -> str | None:
        parts = self.world.explain_rule(typed, state)
        return None if parts is None else "".join(part["text"] for part in parts)

    def more(self, number: int, state: CollectionState) -> str:
        return "".join(part["text"] for part in self.world.explain_more(str(number), state))


class TestTheDoorWaitsForCompletion(CompletedGateTestBase):
    def test_the_world_asks_ut_for_the_completion_key(self):
        self.assertEqual(KEY, getattr(Age2World, "found_entrances_datastorage_key", None))

    def test_win_items_held_but_unplayed_leaves_the_door_shut(self):
        self.assertFalse(self.has(self.door(self.first), self.state_without()))

    def test_a_completed_bit_opens_the_door(self):
        self.complete(self.first)
        self.assertTrue(self.has(self.door(self.first), self.state_without()))

    def test_before_the_first_reply_nothing_is_completed(self):
        self.world.reconnect_found_entrances(KEY, None)
        self.assertEqual(set(), self.world.completed_scenarios)
        self.assertFalse(self.has(self.door(self.first), self.state_without()))

    def test_a_completed_scenario_opens_without_its_win_items(self):
        self.complete(self.first)
        state = self.state_with()
        state.sweep_for_advancements()
        self.assertTrue(self.has(self.door(self.first), state))

    def test_the_next_scenario_is_out_of_logic_until_completed(self):
        self.assertFalse(self.can_reach(self.victory(self.second), self.state_without()))
        self.complete(self.first)
        self.assertTrue(self.can_reach(self.victory(self.second), self.state_without()))


class TestTheBitOrderIsTheClients(CompletedGateTestBase):
    campaigns = ["Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Joan of Arc"]

    def setUp(self) -> None:
        self.build()

    def test_each_bit_names_the_scenario_the_client_wrote(self):
        handler = CampaignHandler(list(Age2CampaignData))
        handler.setup_victory_requirements(dict(self.world.fill_slot_data()))
        client = DataStorage(handler.included_campaigns())
        self.assertTrue(self.world.pool.scenarios.included)
        for scenario in self.world.pool.scenarios.included:
            with self.subTest(scenario.scenario_name):
                self.world.reconnect_found_entrances(KEY, 1 << client.scenario_bit(scenario))
                self.assertEqual({scenario}, self.world.completed_scenarios)


class WinRuleDoor:
    def test_the_door_follows_the_win_rule(self):
        self.assertTrue(self.has(self.door(self.first), self.state_without()))
        state = self.state_with()
        state.sweep_for_advancements()
        self.assertFalse(self.has(self.door(self.first), state))


class TestDeferredConnectionsOff(WinRuleDoor, CompletedGateTestBase):
    deferred = "off"

    def test_explain_keeps_the_item_wording(self):
        locked = self.state_without("Progressive Attila Scenario")
        answer = self.plain(self.victory(self.second), locked)
        self.assertIn(f"Has {self.door(self.first)} -> True", answer)
        self.assertNotIn("completed", answer)


class TestOutsideTheTracker(WinRuleDoor, CompletedGateTestBase):
    deferred = None

    def test_naming_the_door_is_left_to_ut(self):
        self.assertIsNone(self.plain(f"Complete {self.first.scenario_name}", self.state_without()))


class TestExplainShowsTheDoorAsCompleted(CompletedGateTestBase):
    def test_not_completed_has_a_marker_that_says_why(self):
        state = self.state_without()
        answer = self.plain(self.victory(self.second), state)
        line = next(line for line in answer.split("\n") if f"{self.first.scenario_name} completed" in line)
        self.assertNotIn(self.door(self.first), answer)
        self.assertIn("-> False", line)
        number = int(line.split("[/explain_more ")[1].rstrip("]"))
        more = self.more(number, state).split("\n")
        self.assertEqual(f"{self.first.scenario_name} completed -> False", more[0])
        self.assertEqual("The server has no win recorded; winning it in game opens the next.",
                         more[1].strip())
        self.assertEqual("To complete it,", more[2].strip())
        self.assertTrue(more[3].strip().startswith(f"Victory in {self.first.scenario_name}"), more[3])
        self.assertGreater(len(more[3]) - len(more[3].lstrip()), len(more[2]) - len(more[2].lstrip()))

    def test_completed_has_no_marker(self):
        self.complete(self.first)
        state = self.state_without("Progressive Attila Scenario")
        answer = self.plain(self.victory(self.second), state)
        line = next(line for line in answer.split("\n") if f"{self.first.scenario_name} completed" in line)
        self.assertEqual(f"{self.first.scenario_name} completed -> True", line.strip())

    def test_naming_the_door_or_its_event_gives_the_completed_view(self):
        state = self.state_without()
        for typed in (self.door(self.first), f"Complete {self.first.scenario_name}",
                      f"complete {self.first.scenario_name.lower()}"):
            with self.subTest(typed):
                answer = self.plain(typed, state)
                self.assertIsNotNone(answer)
                self.assertTrue(answer.startswith(f"{self.first.scenario_name} completed -> False"), answer)
                self.assertIn("To complete it,", answer)
