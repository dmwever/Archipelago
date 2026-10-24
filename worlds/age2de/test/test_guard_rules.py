"""Guard rules: "can P1 hold the trade route to this player's market or dock open" (ADR 0001).

Nothing is ruled GUARDED yet, so every test here rules one building GUARDED for its own run: the
Eastern Roman Empire's dock in Attila 1, whose owner Attila 1 already writes defeat rules for.
"""

from unittest import mock

from rule_builder.rules import Rule, True_

from . import bases
from ..Options import PartnerTrade
from ..items.Items import Age2ItemData, Resource
from ..locations.Buildings import Age2BuildingData
from ..locations.Players import TRADE_BUILDINGS, Age2PlayerData, Side, TradeAccess
from ..locations.Scenarios import Age2ScenarioData
from ..locations.connections.ScenarioPlayers import SCENARIO_TO_PLAYERS
from ..logic.ScenarioLogic import ScenarioLogic
from ..logic.attila.attila_1 import Attila1StartingState
from ..logic.custom_logic.Named import Named

SCENARIO = Age2ScenarioData.AP_ATTILA_1
OWNER = Age2PlayerData.ATT1_EASTERN_ROMAN_EMPIRE
DOCK = Age2BuildingData.DOCK
GUARD_EVENT = OWNER.guard_event(SCENARIO.scenario_name, DOCK)
DEFEAT_EVENT = OWNER.defeat_event(SCENARIO.scenario_name)

VILLAGER_CAMPS = (
    Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name,
    Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name,
    Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name,
)
VILLAGER_FOOD = Age2ItemData.STARTING_VILLAGER_FOOD.item_name


def scenario_of(player: Age2PlayerData) -> Age2ScenarioData:
    """The scenario a player belongs to - every player belongs to exactly one."""
    return next(scenario for scenario, players in SCENARIO_TO_PLAYERS.items()
                if player in players)


def costs_of_some(scenario_logic: ScenarioLogic) -> Rule:
    """A guard that pays for itself in routes of *some*, as a ruled guard is meant to."""
    economy = scenario_logic.economy
    return (economy.has_some_source(Resource.WOOD)
            & economy.has_some_source(Resource.GOLD))


class GuardedDockTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def build_guarded(self, guard=costs_of_some, **options):
        """Attila 1 with the Eastern Roman dock ruled GUARDED and `guard` its guard rule.

        The patches outlive the build: the partner gate and the player logic both read the record
        again whenever a rule is asked for after it.
        """
        self.enterContext(mock.patch.object(OWNER, "dock", TradeAccess.GUARDED))
        self.enterContext(mock.patch.object(
            Attila1StartingState,
            "trade_guard_rules",
            lambda _self, scenario_logic: {(OWNER, DOCK): guard(scenario_logic)},
        ))
        options.setdefault("partner_trade", PartnerTrade.option_allies_and_enemies)
        return self.build(**options)

    def scenario_logic(self) -> ScenarioLogic:
        return self.world.rules.logic.for_scenario(SCENARIO)

    def holds(self, rule, state) -> bool:
        return bool(rule.resolve(self.world)(state))


class TestTheGuardEventExists(GuardedDockTestBase):

    def test_allies_and_enemies_creates_the_guard_event(self):
        self.build_guarded()
        event = self.world.get_location(GUARD_EVENT)
        guard = self.scenario_logic().player_logic.guards(OWNER, DOCK)
        self.assertEqual(guard.resolve(self.world), event.access_rule)

    def test_allies_creates_no_guard_event(self):
        self.build_guarded(partner_trade=PartnerTrade.option_allies)
        with self.assertRaises(KeyError):
            self.world.get_location(GUARD_EVENT)

    def test_none_creates_no_guard_event(self):
        self.build_guarded(partner_trade=PartnerTrade.option_none)
        with self.assertRaises(KeyError):
            self.world.get_location(GUARD_EVENT)

    def test_the_rule_reads_as_guarding_that_building(self):
        self.build_guarded()
        guard = self.scenario_logic().player_logic.guards(OWNER, DOCK)
        self.assertIsInstance(guard, Named)
        self.assertTrue(
            guard.label.endswith(f"can guard the route to {OWNER.player_name}'s dock"),
            guard.label,
        )


class TestAGuardedBuildingOpensOnEitherEvent(GuardedDockTestBase):
    """GUARDED means "once defeated, or guarded": either event opens the dock, neither leaves it
    shut. Attila 1's only other dock records are closed, so the partner dock is this one."""

    def partner_dock(self):
        return self.scenario_logic().player_logic.can_reach_partner(DOCK)

    def test_the_guard_event_alone_opens_it(self):
        self.build_guarded()
        self.assertTrue(self.holds(self.partner_dock(), self.state_with(GUARD_EVENT)))

    def test_the_defeat_event_alone_opens_it(self):
        self.build_guarded()
        self.assertTrue(self.holds(self.partner_dock(), self.state_with(DEFEAT_EVENT)))

    def test_neither_event_leaves_it_shut(self):
        self.build_guarded()
        self.assertFalse(self.holds(self.partner_dock(), self.state_with()))

    def test_a_guarded_owner_is_still_defeatable(self):
        """It keeps its defeat event, so it still needs defeat rules like any defended owner."""
        self.build_guarded()
        self.assertTrue(OWNER.can_trade_once_defeated)
        self.world.get_location(DEFEAT_EVENT)


class TestAGuardIsPaidInRoutesOfSome(GuardedDockTestBase):
    """A guard states its own costs as *some*, so no bank pays one and a guard can open a trade
    route with no base behind it."""

    def test_a_guard_of_some_opens_trade_cogs_with_no_base(self):
        self.build_guarded()
        scenario = self.scenario_logic()
        no_base = self.state_without(VILLAGER_FOOD)
        self.assertFalse(self.holds(scenario.has_base(), no_base))
        self.assertTrue(self.holds(scenario.player_logic.guards(OWNER, DOCK), no_base))
        self.assertTrue(self.holds(scenario.economy.can_run_trade_cogs(), no_base))

    def test_a_bank_alone_does_not_pay_a_guard(self):
        """The same wood and gold, held only as banked starting resources: villagers can neither
        chop nor mine, so there is no source of *some* and the guard does not hold."""
        self.build_guarded()
        scenario = self.scenario_logic()
        banked = self.state_without(*VILLAGER_CAMPS)
        resources = self.world.rules.logic.resources
        self.assertTrue(self.holds(resources.has_amount(Resource.WOOD, 400), banked))
        self.assertTrue(self.holds(resources.has_amount(Resource.GOLD, 100), banked))
        self.assertFalse(self.holds(scenario.economy.has_some_source(Resource.WOOD), banked))
        self.assertFalse(self.holds(scenario.player_logic.guards(OWNER, DOCK), banked))


class TestTheGuardRecordsAndRulesAgree(GuardedDockTestBase):
    """Every GUARDED record has a guard rule and defeat rules, and every guard rule's record is
    GUARDED. A missing rule is a KeyError out of `guards()`, which is what this pins."""

    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def guarded_records(self) -> set[tuple[Age2PlayerData, Age2BuildingData]]:
        return {
            (player, building)
            for players in SCENARIO_TO_PLAYERS.values()
            for player in players
            for building in TRADE_BUILDINGS
            if player.trade_access(building) is TradeAccess.GUARDED
        }

    def ruled_records(self) -> set[tuple[Age2PlayerData, Age2BuildingData]]:
        records: set[tuple[Age2PlayerData, Age2BuildingData]] = set()
        for scenario_logic in self.world.rules.logic.scenarios:
            records |= set(scenario_logic.starting_state.trade_guard_rules(scenario_logic))
        return records

    def test_shipped_records_and_guard_rules_match(self):
        self.build()
        self.assertEqual(self.guarded_records(), self.ruled_records())

    def test_the_ruled_records_match_when_one_is_guarded(self):
        self.build_guarded()
        self.assertEqual({(OWNER, DOCK)}, self.guarded_records())
        self.assertEqual(self.guarded_records(), self.ruled_records())

    def test_a_guarded_record_with_no_guard_rule_is_an_error(self):
        self.enterContext(mock.patch.object(OWNER, "dock", TradeAccess.GUARDED))
        with self.assertRaises(KeyError):
            self.build(partner_trade=PartnerTrade.option_allies_and_enemies)

    def test_a_guard_rule_with_no_guarded_record_goes_red(self):
        """The dock stays ONCE_DEFEATED, so no event is created and nothing asks the rule. What
        catches the stray rule is the shipped-records check above: the same assertion that passes
        there fails here."""
        self.enterContext(mock.patch.object(
            Attila1StartingState,
            "trade_guard_rules",
            lambda _self, scenario_logic: {(OWNER, DOCK): True_()},
        ))
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        with self.assertRaises(AssertionError):
            self.assertEqual(self.guarded_records(), self.ruled_records())

    def test_every_guarded_owner_has_defeat_rules(self):
        self.build_guarded()
        for player, _ in self.guarded_records():
            with self.subTest(player=player.name):
                scenario_logic = self.world.rules.logic.for_scenario(scenario_of(player))
                self.assertIn(player, scenario_logic.starting_state.defeat_rules(scenario_logic))

    def test_an_ally_is_never_guarded(self):
        """An ally's gate is built at `allies` too, where no guard event exists to ask for."""
        for player in Age2PlayerData:
            if player.side is not Side.ALLY:
                continue
            for building in TRADE_BUILDINGS:
                with self.subTest(player=player.name, building=building.name):
                    self.assertIsNot(player.trade_access(building), TradeAccess.GUARDED)

    def test_a_guard_event_names_the_building_it_guards(self):
        self.assertEqual(f"{SCENARIO.scenario_name}: Guard {OWNER.player_name}'s dock",
                         OWNER.guard_event(SCENARIO.scenario_name, DOCK))
        self.assertEqual(f"{SCENARIO.scenario_name}: Guard {OWNER.player_name}'s market",
                         OWNER.guard_event(SCENARIO.scenario_name, Age2BuildingData.MARKET))
