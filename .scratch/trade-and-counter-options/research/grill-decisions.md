# Grill decisions (age2de: PRs 18/19/20 + options), 2026-10-15

Branch: v0.3.0 in Archipelago-ResourceBudget worktree (dirty WIP: building options; don't touch except adding to Options.py). Never commit.

- PR19 == PR20 (same head f39ac98d). PR18: take UnitCounters edits only; Hulk already on v0.3.0 (934).
- Q1 c: market/dock data at scenario level, not on ScenarioResourceCount. Genghis connected on v0.3.0.
- Unconnected campaigns (Saladin, Barbarossa, ElCid, Montezuma): source, not imported, no tests; keep PR19 per-scenario flags (fixed syntax), dedupe Montezuma, fix Saladin docstring.
- Q3 c: ANTI_UNIT_SIEGE hand-picked. Q9: Mangonel, Bombard, Rocket Cart (+Heavy). NOT scorpion, NOT organ gun.
- Rams: RAM_COUNTERS table (sponge targets only). Counts only with ram AND any military line (Q4 b). Ram vs treb stays in LINE_TO_COUNTERS (Q5 b). Ram = BATTERING_RAM_LINE or ARMORED_ELEPHANT_LINE (Q6 b).
- Q7 d: other PR18 "harder" tags stay as comments, entries live.
- Q8: monks off -> remove every FAITH_LINES counter entry except vs BATTLE_ELEPHANT, WAR_ELEPHANT, ELEPHANT_ARCHER.
- Q10: siege off -> remove anti-unit-siege entries vs armies and ships; keep vs other siege (UnitRoles.SIEGE + Mangonel, Scorpion, Rocket Cart; organ gun = army).
- Q11 c / Q14 b: one option partner_trade Choice: none / allies / allies_and_enemies. Covers carts + cogs.
- Q12 b: data feeds trading_ally default; StartingState may override.
- Q13: enemy market usable once player can defeat its owner.
- Q15 b: per-player records; lift can_beat_*/can_kill_* locals into named rules usable by victory + trade.
- Q16: verb "defeat"; key = per-scenario enum carrying slot + readable name.
- Q17 c defaults: market_trade off, partner_trade allies, monks_can_counter off, siege_can_counter off.
- Q18 a: logic-only; no slot_data, no XS, no version bump.
- Q19 a + PR19 flags: flags mean USABLE (judged), not existence. Per-player hand-written.
- Q20 a: per-player usable_market/usable_dock seeded from scan where flag true; scenario flag derived.
- Q22 a: test all new behavior TDD + regression that lifted defeat rules == old.
- Q23: each slot fixed ALLY or ENEMY (no neutral, no switching); user rules unclear cases one at a time.

## Q24 side rulings
- Attila 1 P3 Scythians: ALLY
- Attila 1 P5 Eastern Roman Empire: ENEMY
- Attila 1 P2 Bleda: IGNORED (no record; logic never trades with or defeats them)
- Attila 2 P6 Thessalonica: ENEMY, usable dock -> Attila 2 enemy_dock becomes TRUE (override PR19)
- Attila 2 P8 Scythians: NEUTRAL (user word; treating as = IGNORED, no record)
- Attila 4 P2 Burgundy: ENEMY (changed from ally; single side only, no "both")
- Attila 5 P6 Franks: NEUTRAL
- Joan 4 P2 Troyes, P3 Chalons, P4 Rheims: ENEMY
- Genghis 4 P4 Khwarazm: ENEMY, MAIN opponent (significantly stronger; not necessarily victory target) -> market not usable
- Joan 1 / Joan 5: fixed-force, skip entirely (no trade). Genghis 1 / Genghis 2 neutral slots own nothing and have no defeat rule: skip.
Side rulings DONE.

## Q21 leftovers resolved
- Attila 4 enemy_dock: DROP -> false
- Genghis 4 ally_market: DROP -> false
- Genghis 5: ally_market, ally_dock DROP -> false; enemy_market -> TRUE (owners: P2 Polish, P4 Germans, BOTH usable)
- Main opponent = significantly stronger than the rest (not necessarily victory target); market/dock never usable.

## Q25 seeding rule (accepted)
Flag true -> slot on that side usable if owns building at start OR its AI builds one, unless main opponent. Flag false -> none usable.
Main opponents: Attila 1 Persians (P4). Attila 2 Eastern Roman Empire (P7). Attila 4 Orléans (P4). Attila 5 Western Roman Empire (P3). Joan 2: enemy_market -> FALSE (scenario ends on partial defeat; nothing tradable). Joan 3: English (P3) main, BUT their dock stays usable (undefended) -> main-opponent exclusion is a default, overridable per building. Each enemy building has a gate: DEFEAT owner (default) or NONE (undefended). Joan 3 English dock = NONE. Joan 6: English (P3) main, no overrides. Genghis 2: Kushluk (P3) main.
Main-opponent asks DONE. Attila 3 Constantinople (P2). Attila 6: none. Genghis 4: Khwarazm.

## Q26 enum name: <Scenario>Player, e.g. Genghis3Player.JIN

## Q27: glossary uses P1 (person) / Player (other slot). Done in CONTEXT.md.
## Q28 a: defeat rules in logic layer: *StartingState.defeat_rules(scenario_logic) -> dict[XPlayer, Rule]; ScenarioLogic.defeats(player) cached; rules files read it. Guard test: defeat rule must not depend on trade with same player.

## Q29 c: user dictates missing defeat rules
- Attila 2 Dyrrhachium (P5 cyan): FREE (True_)
- Attila 2 Thessalonica (P6 purple): FREE
- Genghis 4 Kipchaks (P2 green): FREE
- Genghis 5 Polish (P2 blue): has_base & has_military(CASTLE) & counters(MILITIA,CASTLE) & counters(KNIGHT,CASTLE) & counters(MANGONEL,CASTLE) & has_siege() & can_reach(CASTLE)
- Attila 3 red/green: share can_beat_red_or_green (confirmed Q29.5)

## Q30 a: docs - Ageipelago-ResourceBudget (0.3.0) docs/agent/references/options: 4 new files + index rows, apworld.md (Player records, defeats()); apworld docstrings; drop MARKET_ECONOMY/ALLY_TRADE; rename named("can beat X") -> "can defeat X". Ask before recopying ~/.claude/skills/ageipelago.

## ADR 0001 written (worlds/age2de/docs/adr). Spec at worlds/age2de/docs/spec-trade-and-counter-options.md.

## OPEN (found on spec re-read)
- Q31 a RESOLVED: sponge supersedes PR18 ram removals. RAM_COUNTERS = Archer, Cav Archer, Longbow, Plumed, Rattan, Ballista Elephant, Skirmisher. Ram vs Trebuchet stays plain counter.
- Q32 a RESOLVED: take PR18 petard removals (vs Bombard, Mangonel, Scorpion, Trebuchet); other petard entries stay.
- Q33 RESOLVED: siege targets = Battering Ram, Armored Elephant, Trebuchet, Traction Treb, Mounted Treb, Bombard, Mangonel, Scorpion, Rocket Cart, Heavy Rocket Cart. NOT Fire Archer, NOT Petard, NOT Organ Gun (armies). Own group, not UnitRoles.SIEGE. Mangonel/Rocket Cart don't counter Bombard (table already lacks those entries).
- No open items.
