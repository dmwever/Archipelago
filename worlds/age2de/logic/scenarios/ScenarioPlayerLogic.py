from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Or, Rule, True_

from ...Options import PartnerTrade
from ...locations.Buildings import Age2BuildingData
from ...locations.Players import Age2PlayerData, Side, TradeAccess

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

class ScenarioPlayerLogic:
    """What P1 can do about the scenario's other players: defeat them, and trade with them."""

    def __init__(self, scenario: 'ScenarioLogic'):
        self.scenario = scenario
        self.logic = scenario.logic
        self.world = scenario.logic.world
        self._defeats: dict[Age2PlayerData, Rule] | None = None

    # -- defeat -------------------------------------------------------------------------------

    def defeats(self, player: Age2PlayerData) -> Rule:
        if self._defeats is None:
            defeat_rules = self.scenario.starting_state.defeat_rules(self.scenario)
            self._defeats = {
                opponent: self.scenario.named(f"can defeat {opponent.player_name}", rule)
                for opponent, rule in defeat_rules.items()
            }
        return self._defeats[player]

    def has_defeated(self, player: Age2PlayerData) -> Rule:
        return Has(player.defeat_event(self.scenario.scenario.scenario_name))

    # -- trade --------------------------------------------------------------------------------

    def has_trading_ally(self) -> Rule:
        has_open_ally_building = any(
            player.side is Side.ALLY and TradeAccess.OPEN in (player.market, player.dock)
            for player in self.scenario.scenario.players
        )
        return True_() if has_open_ally_building else False_()

    def can_reach_partner(self, building: Age2BuildingData) -> Rule:
        """A trade partner's market or dock, as far as the yaml lets the logic count on one."""
        partner_trade = self.world.options.partner_trade
        if partner_trade == PartnerTrade.option_none:
            return False_()
        gates = [
            self._partner_gate(player, building) for player in self.scenario.scenario.players
                if player.side is Side.ALLY
                or partner_trade == PartnerTrade.option_allies_and_enemies
        ]
        gates = [gate for gate in gates if not isinstance(gate, False_)]
        if not gates:
            return False_()
        return Or(*gates)

    def _partner_gate(self, player: Age2PlayerData, building: Age2BuildingData) -> Rule:
        """What stands between P1 and this player's market or dock."""
        access = player.trade_access(building)
        if access is TradeAccess.OPEN:
            return True_()
        if access is TradeAccess.ONCE_DEFEATED:
            return self.has_defeated(player)
        return False_()
