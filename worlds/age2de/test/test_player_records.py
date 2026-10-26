"""Player records: each connected scenario's allies and enemies, and what P1 can trade with."""

import unittest

from ..locations.Buildings import Age2BuildingData
from ..locations.Players import Age2PlayerData, Side, TradeAccess
from ..locations.Scenarios import Age2ScenarioData
from ..locations.connections.ScenarioPlayers import SCENARIO_TO_PLAYERS

MARKET = Age2BuildingData.MARKET
DOCK = Age2BuildingData.DOCK

# PR 19's judged flags, as the design rulings corrected them: ally market, enemy market, ally dock,
# enemy dock. The players are written by hand from these, so the two must never disagree.
JUDGED_FLAGS: dict[Age2ScenarioData, tuple[bool, bool, bool, bool]] = {
    Age2ScenarioData.AP_ATTILA_1: (True, True, False, True),
    Age2ScenarioData.AP_ATTILA_2: (False, True, False, True),
    Age2ScenarioData.AP_ATTILA_3: (False, True, False, True),
    Age2ScenarioData.AP_ATTILA_4: (False, True, False, False),
    Age2ScenarioData.AP_ATTILA_5: (True, True, False, False),
    Age2ScenarioData.AP_ATTILA_6: (False, False, True, True),
    Age2ScenarioData.AP_JOAN_1: (False, False, False, False),
    Age2ScenarioData.AP_JOAN_2: (True, False, False, False),
    Age2ScenarioData.AP_JOAN_3: (False, True, False, True),
    Age2ScenarioData.AP_JOAN_4: (False, False, False, True),
    Age2ScenarioData.AP_JOAN_5: (False, False, False, False),
    Age2ScenarioData.AP_JOAN_6: (False, True, False, True),
    Age2ScenarioData.AP_GENGHIS_1: (False, False, False, False),
    Age2ScenarioData.AP_GENGHIS_2: (False, True, False, False),
    Age2ScenarioData.AP_GENGHIS_3: (False, False, False, True),
    Age2ScenarioData.AP_GENGHIS_4: (False, True, False, False),
    Age2ScenarioData.AP_GENGHIS_5: (False, True, False, False),
    Age2ScenarioData.AP_GENGHIS_6: (False, False, False, False),
}

class TestPlayersFollowTheRulings(unittest.TestCase):
    def test_every_scenario_is_routed(self):
        self.assertEqual(set(SCENARIO_TO_PLAYERS), set(Age2ScenarioData))

    def test_every_player_belongs_to_exactly_one_scenario(self):
        routed = [player for players in SCENARIO_TO_PLAYERS.values() for player in players]
        self.assertCountEqual(routed, list(Age2PlayerData))

    def test_a_players_id_is_its_scenario_then_its_slot(self):
        for scenario, players in SCENARIO_TO_PLAYERS.items():
            for player in players:
                with self.subTest(player=player.name):
                    self.assertEqual(player.id, scenario.id * 10 + player.slot)

    def test_a_player_is_known_by_its_slot(self):
        """Slots are P2 to P8; P1 is the person playing and is never a player here."""
        for player in Age2PlayerData:
            with self.subTest(player=player.name):
                self.assertIn(player.slot, range(2, 9))

    def test_fixed_force_scenarios_record_no_one(self):
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5):
            with self.subTest(scenario.name):
                self.assertEqual(scenario.players, [])

    def test_neutral_and_ignored_slots_have_no_player(self):
        absent = {
            Age2ScenarioData.AP_ATTILA_1: 2,   # Bleda, ignored
            Age2ScenarioData.AP_ATTILA_2: 8,   # the Scythians, neutral
            Age2ScenarioData.AP_ATTILA_5: 6,   # the Franks, neutral
            Age2ScenarioData.AP_GENGHIS_1: 2,  # the Kara-Khitai, neutral
            Age2ScenarioData.AP_GENGHIS_2: 4,  # the Tayichi'uds, neutral
            Age2ScenarioData.AP_GENGHIS_3: 6,  # the Engineers, ignored
        }
        for scenario, slot in absent.items():
            with self.subTest(scenario.name):
                self.assertNotIn(slot, [player.slot for player in scenario.players])

    def test_each_side_is_as_ruled(self):
        sides = {
            Age2PlayerData.ATT1_SCYTHIANS: Side.ALLY,
            Age2PlayerData.ATT1_EASTERN_ROMAN_EMPIRE: Side.ENEMY,
            Age2PlayerData.ATT2_THESSALONICA: Side.ENEMY,
            Age2PlayerData.ATT4_BURGUNDY: Side.ENEMY,
            Age2PlayerData.ATT5_OSTROGOTHS: Side.ALLY,
            Age2PlayerData.ATT6_WESTERN_ROMAN_EMPIRE: Side.ALLY,
            Age2PlayerData.JOAN2_BLOIS: Side.ALLY,
            Age2PlayerData.JOAN4_TROYES: Side.ENEMY,
            Age2PlayerData.JOAN4_CHALONS: Side.ENEMY,
            Age2PlayerData.JOAN4_RHEIMS: Side.ENEMY,
            Age2PlayerData.GEN4_KHWARAZM: Side.ENEMY,
        }
        for player, side in sides.items():
            with self.subTest(player=player.name):
                self.assertIs(player.side, side)

    def test_an_ally_never_waits_on_its_own_defeat(self):
        for player in Age2PlayerData:
            if player.side is not Side.ALLY:
                continue
            with self.subTest(player=player.name):
                self.assertNotIn(TradeAccess.ONCE_DEFEATED, (player.market, player.dock))

    def test_the_kipchaks_are_never_a_trade_partner(self):
        """They surrender and hand their camp to P1: their market becomes P1's own."""
        kipchaks = Age2PlayerData.GEN4_KIPCHAKS
        self.assertEqual((TradeAccess.CLOSED, TradeAccess.CLOSED), (kipchaks.market, kipchaks.dock))

    def test_genghis_5_trades_with_both_the_polish_and_the_germans(self):
        self.assertIsNot(Age2PlayerData.GEN5_POLISH.market, TradeAccess.CLOSED)
        self.assertIsNot(Age2PlayerData.GEN5_GERMANS.market, TradeAccess.CLOSED)
        self.assertIs(Age2PlayerData.GEN5_BOHEMIANS.market, TradeAccess.CLOSED)

    def test_the_players_agree_with_the_judged_flags(self):
        for scenario, flags in JUDGED_FLAGS.items():
            with self.subTest(scenario.name):
                self.assertEqual(
                    (
                        self.is_open_on(scenario, Side.ALLY, MARKET),
                        self.is_open_on(scenario, Side.ENEMY, MARKET),
                        self.is_open_on(scenario, Side.ALLY, DOCK),
                        self.is_open_on(scenario, Side.ENEMY, DOCK),
                    ),
                    flags,
                )

    def is_open_on(self, scenario: Age2ScenarioData, side: Side, building: Age2BuildingData) -> bool:
        return any(
            player.side is side and player.trade_access(building) is not TradeAccess.CLOSED
            for player in scenario.players
        )
