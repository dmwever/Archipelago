# 10: market_trade option

**What to build:** A yaml option, default off, deciding whether the logic may expect P1 to buy and
sell at its own market. It replaces the `MARKET_ECONOMY` module constant one for one. Logic only.

Spec: Implementation Decisions, "Options", "Trade logic". Glossary: Market trade.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Tests first: market trade is never satisfiable with the option off, and follows the existing market rule with it on
- [x] The module constant is gone
- [x] Default off; not in slot data or XS
- [x] Ageipelago option reference page and index row added
- [x] Full suite green

## Comments

- The option is `MarketTrade` (`market_trade`). `ScenarioResourceLogic.market_trades` reads
  `self.world.options.market_trade` where `MARKET_ECONOMY` was; the rule behind it is unchanged.
- `TestMarketTrade` in test_economy_rules: off by default; off, false in every scenario; on, depends
  on the Market item, false with neither wood nor endless food, satisfiable with wood. The old
  termination test now builds with the option instead of patching the constant.
- `market_trade` added to `LOGIC_ONLY` (test_slot_data_wire) and the pools exemption list.
- Ageipelago: `market-trade.md`, its index row and its line in the defaults yaml, on the `0.3.0` branch.
