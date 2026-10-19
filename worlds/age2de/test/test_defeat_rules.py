"""Defeat rules: "can P1 defeat this player", asked of a scenario's logic (ADR 0001)."""

from . import bases
from ..locations.Scenarios import Age2ScenarioData
from ..logic.ScenarioPlayer import ScenarioPlayer
from ..logic.attila.attila_1 import Attila1Player
from ..logic.attila.attila_2 import Attila2Player
from ..logic.attila.attila_3 import Attila3Player
from ..logic.attila.attila_4 import Attila4Player
from ..logic.attila.attila_5 import Attila5Player
from ..logic.attila.attila_6 import Attila6Player
from ..logic.genghis.genghis_1 import Genghis1Player
from ..logic.genghis.genghis_2 import Genghis2Player
from ..logic.genghis.genghis_3 import Genghis3Player
from ..logic.genghis.genghis_4 import Genghis4Player
from ..logic.genghis.genghis_5 import Genghis5Player
from ..logic.genghis.genghis_6 import Genghis6Player
from ..logic.custom_logic.Named import Named

SCENARIO_PLAYERS: dict[Age2ScenarioData, type[ScenarioPlayer]] = {
    Age2ScenarioData.AP_ATTILA_1: Attila1Player,
    Age2ScenarioData.AP_ATTILA_2: Attila2Player,
    Age2ScenarioData.AP_ATTILA_3: Attila3Player,
    Age2ScenarioData.AP_ATTILA_4: Attila4Player,
    Age2ScenarioData.AP_ATTILA_5: Attila5Player,
    Age2ScenarioData.AP_ATTILA_6: Attila6Player,
    Age2ScenarioData.AP_GENGHIS_1: Genghis1Player,
    Age2ScenarioData.AP_GENGHIS_2: Genghis2Player,
    Age2ScenarioData.AP_GENGHIS_3: Genghis3Player,
    Age2ScenarioData.AP_GENGHIS_4: Genghis4Player,
    Age2ScenarioData.AP_GENGHIS_5: Genghis5Player,
    Age2ScenarioData.AP_GENGHIS_6: Genghis6Player,
}

class TestDefeatRules(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Genghis Khan"]

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

    def test_the_two_cities_share_one_rule(self):
        """Philippopolis and Marcianopolis are interchangeable: one rule, each under its own name."""
        scenario_logic = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
        philippopolis = scenario_logic.defeats(Attila3Player.PHILIPPOPOLIS)
        marcianopolis = scenario_logic.defeats(Attila3Player.MARCIANOPOLIS)
        self.assertIs(philippopolis.child, marcianopolis.child)
        self.assertNotEqual(philippopolis.label, marcianopolis.label)

    def test_the_roman_army_falls_with_orleans(self):
        """The Western Roman Empire's army stands with Orléans: one rule, each under its own name."""
        scenario_logic = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_4)
        orleans = scenario_logic.defeats(Attila4Player.ORLEANS)
        romans = scenario_logic.defeats(Attila4Player.WESTERN_ROMAN_EMPIRE)
        self.assertIs(orleans.child, romans.child)
        self.assertNotEqual(orleans.label, romans.label)
