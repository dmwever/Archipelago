"""Defeat rules: "can P1 defeat this player", asked of a scenario's logic (ADR 0001)."""

from . import bases
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Players import Age2PlayerData, Side
from ..locations.connections.ScenarioPlayers import SCENARIO_TO_PLAYERS
from ..logic.custom_logic.Named import Named

class TestDefeatRules(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def setUp(self):
        self.build()

    def logic_and_players(self):
        """Every player with a defeat rule: not every player has one, only those victory or
        trade asks about."""
        for scenario in SCENARIO_TO_PLAYERS:
            scenario_logic = self.world.rules.logic.for_scenario(scenario)
            for player in scenario_logic.starting_state.defeat_rules(scenario_logic):
                yield scenario_logic, player

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
        """Crucible's victory is the Kereyid monk, never a fight: every player is an ally."""
        players = SCENARIO_TO_PLAYERS[Age2ScenarioData.AP_GENGHIS_1]
        self.assertEqual([player for player in players if player.side is Side.ENEMY], [])

    def test_the_two_cities_share_one_rule(self):
        """Philippopolis and Marcianopolis are interchangeable: one rule, each under its own name."""
        scenario_logic = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
        philippopolis = scenario_logic.defeats(Age2PlayerData.ATT3_PHILIPPOPOLIS)
        marcianopolis = scenario_logic.defeats(Age2PlayerData.ATT3_MARCIANOPOLIS)
        self.assertIs(philippopolis.child, marcianopolis.child)
        self.assertNotEqual(philippopolis.label, marcianopolis.label)

    def test_the_roman_army_falls_with_orleans(self):
        """The Western Roman Empire's army stands with Orléans: one rule, each under its own name."""
        scenario_logic = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_4)
        orleans = scenario_logic.defeats(Age2PlayerData.ATT4_ORLEANS)
        romans = scenario_logic.defeats(Age2PlayerData.ATT4_WESTERN_ROMAN_EMPIRE)
        self.assertIs(orleans.child, romans.child)
        self.assertNotEqual(orleans.label, romans.label)
