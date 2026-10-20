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

**Status:** done

- [x] Tests first
- [x] Enemy trade is closed under `allies`, and under `allies_and_enemies` opens exactly when the gate is met
- [x] Joan 3's English dock is usable without defeating the English
- [x] A main opponent's buildings stay closed
- [x] The four new defeat rules exist and resolve as specified
- [x] Building every scenario's defeat and trade rules raises no recursion
- [x] Full suite green

## Comments

- Built through events, not `defeats(owner)` inline: easy gold/wood -> enemy trade -> defeat -> army
  -> `can_pay` -> easy gold/wood. That loop hit every defeat that costs resources, not only one
  trading with its own player, and raised `RecursionError` from `ScenarioHasEasyResource` at
  `set_rules`. Chosen on review: at `allies_and_enemies` each player with a `ONCE_DEFEATED`
  building gets a hidden event location `"<scenario>: Can Defeat <player>"` (rule `defeats(player)`,
  set in `ScenarioRules.set_defeat_event_rules`), and the trade gate is
  `ScenarioLogic.has_defeated(player)`. "Can Defeat" because "Defeat Metz" and others are real
  locations. No events at `none` or `allies`, so the default region graph is unchanged. ADR 0001's
  consequence rewritten to match.
- `can_reach_partner` is an OR of one gate per partner (`OPEN` -> true, `ONCE_DEFEATED` -> event,
  `CLOSED` dropped); an open partner building makes the enemy gates for that building redundant.
- Ruled on review: the Kipchaks are never a trade partner (they hand their camp, market included, to
  P1). Their market is now `CLOSED`. Their free defeat rule stays, as specified.
- New defeat rules: Attila 2 Dyrrhachium and Thessalonica free, Genghis 4 Kipchaks free, Genghis 5
  Polish as specified.
- No typecheck run: mypy is not installed in this environment.
- Ageipelago: `partner-trade.md` describes the gate, the defeat events and the new tests.
