"""Defeat rules: "can P1 defeat this player", asked of a scenario's logic (ADR 0001)."""

from . import bases
from ..Options import PartnerTrade
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
                defeats = scenario_logic.player_logic.defeats
                self.assertIs(defeats(player), defeats(player))

    def test_every_player_can_be_defeated(self):
        for scenario_logic, player in self.logic_and_players():
            with self.subTest(player=player):
                defeat = scenario_logic.player_logic.defeats(player).resolve(self.world)
                self.assertFalse(defeat.always_false)

    def test_the_rule_reads_as_defeat(self):
        for scenario_logic, player in self.logic_and_players():
            with self.subTest(player=player):
                rule = scenario_logic.player_logic.defeats(player)
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
        philippopolis = scenario_logic.player_logic.defeats(Age2PlayerData.ATT3_PHILIPPOPOLIS)
        marcianopolis = scenario_logic.player_logic.defeats(Age2PlayerData.ATT3_MARCIANOPOLIS)
        self.assertIs(philippopolis.child, marcianopolis.child)
        self.assertNotEqual(philippopolis.label, marcianopolis.label)

    def test_every_defended_trade_partner_has_a_rule(self):
        """Partner trade waits on these: a building open once defeated needs a defeat to wait on."""
        for scenario, players in SCENARIO_TO_PLAYERS.items():
            scenario_logic = self.world.rules.logic.for_scenario(scenario)
            rules = scenario_logic.starting_state.defeat_rules(scenario_logic)
            for player in players:
                if player.can_trade_once_defeated:
                    with self.subTest(player=player):
                        self.assertIn(player, rules)

    def test_the_cities_that_offer_no_resistance_are_free(self):
        for scenario, player in (
            (Age2ScenarioData.AP_ATTILA_2, Age2PlayerData.ATT2_DYRRHACHIUM),
            (Age2ScenarioData.AP_ATTILA_2, Age2PlayerData.ATT2_THESSALONICA),
            (Age2ScenarioData.AP_GENGHIS_4, Age2PlayerData.GEN4_KIPCHAKS),
        ):
            with self.subTest(player=player):
                scenario_logic = self.world.rules.logic.for_scenario(scenario)
                defeat = scenario_logic.player_logic.defeats(player).resolve(self.world)
                self.assertTrue(defeat.always_true)

    def test_the_polish_take_a_castle_age_army(self):
        scenario_logic = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_GENGHIS_5)
        polish = scenario_logic.player_logic.defeats(Age2PlayerData.GEN5_POLISH).resolve(self.world)
        self.assertFalse(polish.always_true)
        self.assertFalse(polish.always_false)

    def test_the_roman_army_falls_with_orleans(self):
        """The Western Roman Empire's army stands with Orléans: one rule, each under its own name."""
        scenario_logic = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_4)
        orleans = scenario_logic.player_logic.defeats(Age2PlayerData.ATT4_ORLEANS)
        romans = scenario_logic.player_logic.defeats(Age2PlayerData.ATT4_WESTERN_ROMAN_EMPIRE)
        self.assertIs(orleans.child, romans.child)
        self.assertNotEqual(orleans.label, romans.label)


class TestDefeatAndTradeTerminate(bases.Age2RuleTestBase):
    """Trade with an enemy waits on its defeat, and a defeat asks for an army P1 has to pay for:
    building either must never come back round to itself."""
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def test_every_defeat_and_trade_rule_builds(self):
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        for scenario in SCENARIO_TO_PLAYERS:
            scenario_logic = self.world.rules.logic.for_scenario(scenario)
            with self.subTest(scenario.name):
                for player in scenario_logic.starting_state.defeat_rules(scenario_logic):
                    scenario_logic.player_logic.defeats(player).resolve(self.world)
                scenario_logic.economy.can_earn_gold_by_partner_trade().resolve(self.world)
                scenario_logic.economy.can_earn_wood_by_partner_trade().resolve(self.world)
        self.assertEqual(set(), self.world.rules.logic.scenario_answers_open)
