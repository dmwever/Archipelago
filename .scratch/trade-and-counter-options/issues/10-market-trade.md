# 10: market_trade option

**What to build:** A yaml option, default off, deciding whether the logic may expect P1 to buy and
sell at its own market. It replaces the `MARKET_ECONOMY` module constant one for one. Logic only.

Spec: Implementation Decisions, "Options", "Trade logic". Glossary: Market trade.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Tests first: market trade is never satisfiable with the option off, and follows the existing market rule with it on
- [ ] The module constant is gone
- [ ] Default off; not in slot data or XS
- [ ] Ageipelago option reference page and index row added
- [ ] Full suite green
