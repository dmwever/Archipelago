# 11: Player trade records and partner_trade with allies

**What to build:** Every connected scenario's `Player` enum covers its allies and enemies, each
carrying a fixed side, a main-opponent flag, usable market, usable dock, and a gate per enemy
building (defeat its owner, or none). Seed the records by the agreed rule (PR 19 flag true: a player
on that side is usable if it owns the building at start or its AI builds one, unless it is a main
opponent; flag false: none usable) and apply every design ruling listed in the spec. The
scenario-level ally/enemy market and dock facts are derived from the records. `trading_ally`
defaults from the records and a starting state can still override it. A `partner_trade` option
(none / allies / allies and enemies, default allies) replaces `ALLY_TRADE`; this ticket makes `none`
and `allies` work.

Spec: Implementation Decisions, "Player records", "Seeding the records", "Trade logic". Glossary:
Trade partner, Partner trade, Main opponent.

Data for seeding (who owns or builds which market or dock, per slot): `../research/` - start with
its README. The raw per-scenario rulings are in `../research/grill-decisions.md`.

**Blocked by:** 05

**Status:** done

- [x] Tests first, through economy rules on a built world
- [x] Records match every ruling in the spec (sides, neutral/ignored slots absent, main opponents, overridden flags)
- [x] Derived scenario flags agree with the records for every connected scenario
- [x] `none`: no partner trade anywhere; `allies`: trade opens only where an ally has a usable building
- [x] `trading_ally` follows the records (override dropped on review, see Comments)
- [x] `ALLY_TRADE` constant gone; option not in slot data or XS
- [x] Ageipelago option reference page and index row added
- [x] Full suite green

## Comments

- Reshaped on review: players are `Age2PlayerData` (`locations/Players.py`), one member per scenario
  player with the data inline (id = scenario id then slot; name, slot, `Side`, main opponent,
  `TradeAccess` for market and dock: CLOSED / OPEN / ONCE_DEFEATED). `connections/ScenarioPlayers.py`
  routes them (`SCENARIO_TO_PLAYERS` -> `Age2ScenarioData.players`). The per-scenario `XPlayer`
  enums, `logic/ScenarioPlayer.py` and `has_usable` are gone; there are no scenario-level flags.
- The `trading_ally` field is dropped: a rule must never be `None`, so there is no starting-state
  override. `ScenarioLogic.has_trading_ally()` is true when any ally keeps a market or dock `OPEN`.
- `PartnerTrade` (`partner_trade`): none / allies / allies_and_enemies, default allies.
  `allies_and_enemies` behaves as `allies` until ticket 12. `ALLY_TRADE` gone; `ally_trade_gold` /
  `ally_trade_wood` became `can_earn_gold_by_partner_trade` / `can_earn_wood_by_partner_trade`, behind
  `can_reach_partner(building)`.
- Ally trade is now live by default in Attila 1, Attila 5, Attila 6 and Joan 2. No recursion.
- Players with no defeat rule: Attila 2 Sofia, Naissus, Adrianople, Dyrrhachium, Thessalonica;
  Genghis 4 Kipchaks; Genghis 5 Polish; Joan 4 English Guards; every ally but Attila 1's Scythians.
  `test_defeat_rules` now walks the players that have defeat rules.
- Open for the user: Genghis 3 Engineers stay without a member (pre-existing decision, though the scan
  says enemy). Attila 1's Scythians are allies from the start, so ally trade is open from the start,
  even though the alliance forms at trigger D26 and can break at D27.
- Ageipelago: `partner-trade.md`, its index row and defaults line; `market-trade.md` no longer
  mentions `ALLY_TRADE`.
