"""Defeat rules: "can P1 defeat this player", asked of a scenario's logic (ADR 0001)."""

from . import bases
from ..locations.Scenarios import Age2ScenarioData
from ..logic.ScenarioPlayer import ScenarioPlayer
from ..logic.genghis.genghis_1 import Genghis1Player
from ..logic.genghis.genghis_2 import Genghis2Player
from ..logic.genghis.genghis_3 import Genghis3Player
from ..logic.genghis.genghis_4 import Genghis4Player
from ..logic.genghis.genghis_5 import Genghis5Player
from ..logic.genghis.genghis_6 import Genghis6Player
from ..logic.custom_logic.Named import Named

SCENARIO_PLAYERS: dict[Age2ScenarioData, type[ScenarioPlayer]] = {
    Age2ScenarioData.AP_GENGHIS_1: Genghis1Player,
    Age2ScenarioData.AP_GENGHIS_2: Genghis2Player,
    Age2ScenarioData.AP_GENGHIS_3: Genghis3Player,
    Age2ScenarioData.AP_GENGHIS_4: Genghis4Player,
    Age2ScenarioData.AP_GENGHIS_5: Genghis5Player,
    Age2ScenarioData.AP_GENGHIS_6: Genghis6Player,
}

class TestDefeatRules(bases.Age2RuleTestBase):
    campaigns = ["Genghis Khan"]
    starting_campaigns = ["Genghis Khan"]

    def setUp(self):
        self.build()

    def logic_and_players(self):
        for scenario, players in SCENARIO_PLAYERS.items():
            for player in players:
                yield self.world.rules.logic.for_scenario(scenario), player

    def test_asking_twice_returns_the_same_rule(self):
        for scenario_logic, player in self.logic_and_players():
            with self.subTest(player=player):
                self.assertIs(scenario_logic.defeats(player), scenario_logic.defeats(player))

    def test_every_player_can_be_defeated(self):
        for scenario_logic, player in self.logic_and_players():
            with self.subTest(player=player):
                self.assertFalse(scenario_logic.defeats(player).resolve(self.world).always_false)

    def test_the_rule_reads_as_defeat(self):
        for scenario_logic, player in self.logic_and_players():
            with self.subTest(player=player):
                rule = scenario_logic.defeats(player)
                self.assertIsInstance(rule, Named)
                self.assertTrue(rule.label.endswith(f"can defeat {player.player_name}"), rule.label)

    def test_a_player_is_known_by_its_slot(self):
        """Slots are P2 to P8; P1 is the person playing and is never a Player."""
        for _, player in self.logic_and_players():
            with self.subTest(player=player):
                self.assertIn(player.slot, range(2, 9))

    def test_crucible_has_no_one_to_defeat(self):
        """Crucible's victory is the Kereyid monk, never a fight."""
        self.assertEqual(list(Genghis1Player), [])
