# 12: partner_trade with enemies

**What to build:** `allies_and_enemies` also opens usable enemy buildings, each behind its gate:
defended buildings need `defeats(owner)`, undefended ones (Joan 3's English dock) need nothing. Main
opponents' buildings stay closed unless overridden. Add the defeat rules trade needs that victory
never did: Attila 2 Dyrrhachium (free), Attila 2 Thessalonica (free), Genghis 4 Kipchaks (free),
Genghis 5 Polish (a base, a Castle Age army, siege, Castle Age, and counters for the militia, knight
and mangonel lines at Castle Age). Guard against a defeat rule depending on trade with its own player.

Spec: Implementation Decisions, "Defeat rules", "Trade logic". ADR 0001. Glossary: Trade partner,
Defeat, Main opponent. Scan data and AI scripts: `../research/`.

**Blocked by:** 11

**Status:** ready-for-agent

- [ ] Tests first
- [ ] Enemy trade is closed under `allies`, and under `allies_and_enemies` opens exactly when the gate is met
- [ ] Joan 3's English dock is usable without defeating the English
- [ ] A main opponent's buildings stay closed
- [ ] The four new defeat rules exist and resolve as specified
- [ ] Building every scenario's defeat and trade rules raises no recursion
- [ ] Full suite green
