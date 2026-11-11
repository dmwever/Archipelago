# Difficulty inventory of embedded AI scripts

Generated from the 18 `AP_*.aoe2scenario` files (Ageipelago `scenario-difficulty` branch, 2026-11-11).
Raw scripts: `ai-scripts/<scenario>_p<N>.per`; machine-readable: `difficulty-inventory.json`.
`ai-scripts/` is gitignored (proprietary game content). If it is missing, extract it first with `python -I tools/dump_ai.py`.

## Per-script summary

| Scenario | P | AI name | Live? | Rules w/ difficulty | Comparisons | `#load-if` DIFFICULTY | Loads `scenario difficulty*` | Other |
|---|---|---|---|---|---|---|---|---|
| AP_Attila_1 | 0 | Promisory | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_1 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_1 | 2 | Attila-scn1 player 2.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_1 | 3 | Attila-scn1 player 3.ai | yes | 10 | `<= moderate`×5, `== easy`×4, `== standard`×1 ⚠ |  | scenario difficulty DE |  |
| AP_Attila_1 | 4 | Attila-scn1 player 4.ai | yes | 12 | `<= moderate`×6, `== easy`×6 |  | scenario difficulty DE |  |
| AP_Attila_1 | 5 | Attila-scn1 player 5.ai | yes | 10 | `<= moderate`×7, `== easy`×3 |  | scenario difficulty DE |  |
| AP_Attila_1 | 6 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_1 | 7 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_1 | 8 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_2 | 0 | Promisory | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_2 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_2 | 2 | Attila-scn2 player 2.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_2 | 3 | Attila-scn2 player 3.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_2 | 4 | Attila-scn2 player 4.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_2 | 5 | Attila-scn2 player 5.ai | yes | 2 | `<= moderate`×1, `== hard`×1 |  | scenario difficulty DE |  |
| AP_Attila_2 | 6 | Attila-scn2 player 6.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_2 | 7 | Attila-scn2 player 7.ai | yes | 12 | `<= moderate`×7, `== easy`×1, `== normal`×4 ⚠ |  | scenario difficulty DE |  |
| AP_Attila_2 | 8 | Attila-scn2 player 8.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_3 | 0 | PromiDE | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_3 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_3 | 2 | scenario noncombat.ai | yes | 0 |  |  | scenario difficulty |  |
| AP_Attila_3 | 3 | Attila-scn3 player 3.ai | yes | 7 | `<= moderate`×4, `== easy`×3 |  | scenario difficulty DE |  |
| AP_Attila_3 | 4 | Attila-scn3 player 4.ai | yes | 10 | `<= moderate`×6, `== easy`×4 |  | scenario difficulty DE |  |
| AP_Attila_3 | 5 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_3 | 6 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_3 | 7 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_3 | 8 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_4 | 0 | RandomGame | GAIA | 0 |  |  |  |  |
| AP_Attila_4 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_4 | 2 | Attila-scn4 player 2.ai | yes | 2 | `<= moderate`×2 |  | scenario difficulty DE |  |
| AP_Attila_4 | 3 | Attila-scn4 player 3.ai | yes | 8 | `<= moderate`×6, `== easy`×2 |  | scenario difficulty DE |  |
| AP_Attila_4 | 4 | Attila-scn4 player 4.ai | yes | 20 | `<= moderate`×7, `== easy`×8, `== hard`×3, `== moderate`×2 |  | scenario difficulty DE |  |
| AP_Attila_4 | 5 | Attila-scn4 player 5.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_4 | 6 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_4 | 7 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_4 | 8 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_5 | 0 | RandomGame | GAIA | 0 |  |  |  |  |
| AP_Attila_5 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_5 | 2 | Attila-scn5 player 2.ai | yes | 11 | `<= moderate`×2, `== easy`×5, `== hard`×2, `== moderate`×2 |  | scenario difficulty DE |  |
| AP_Attila_5 | 3 | Attila-scn5 player 3.ai | yes | 23 | `<= moderate`×6, `== easy`×9, `== hard`×4, `== moderate`×4 |  | scenario difficulty DE |  |
| AP_Attila_5 | 4 | Attila-scn5 player 4.ai | yes | 22 | `<= moderate`×5, `== easy`×7, `== hard`×5, `== moderate`×5 |  | scenario difficulty DE |  |
| AP_Attila_5 | 5 | Attila-scn5 player 5.ai | yes | 16 | `<= moderate`×4, `== easy`×6, `== hard`×3, `== moderate`×3 |  | scenario difficulty DE |  |
| AP_Attila_5 | 6 | Fe Immobile AI.ai | yes | 0 |  |  |  |  |
| AP_Attila_5 | 7 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_5 | 8 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_6 | 0 | RandomGame | GAIA | 0 |  |  |  |  |
| AP_Attila_6 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Attila_6 | 2 | Attila-scn6 player 2.ai | yes | 9 | `<= moderate`×3, `== easy`×4, `== hard`×1, `== moderate`×1 |  | scenario difficulty DE |  |
| AP_Attila_6 | 3 | Attila-scn6 player 3.ai | yes | 8 | `<= moderate`×3, `== easy`×3, `== hard`×1, `== moderate`×1 |  | scenario difficulty DE |  |
| AP_Attila_6 | 4 | Attila-scn6 player 4.ai | yes | 11 | `<= moderate`×5, `== easy`×4, `== hard`×1, `== moderate`×1 |  | scenario difficulty DE |  |
| AP_Attila_6 | 5 | Attila-scn6 player 5.ai | yes | 10 | `<= moderate`×5, `== easy`×5 |  | scenario difficulty DE |  |
| AP_Attila_6 | 6 | Attila-scn6 player 6.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Attila_6 | 7 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Attila_6 | 8 | RandomGame | inactive | 0 |  |  |  |  |
| AP_Genghis_1 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_1 | 2 | Mongols-scn1 player 2.ai | yes | 1 | `== hard`×1 |  | scenario difficulty DE |  |
| AP_Genghis_1 | 3 | Mongols-scn1.ai | yes | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-EXTREME`×1, `!DIFFICULTY-HARD`×1, `!DIFFICULTY-HARDEST`×1, `!DIFFICULTY-MODERATE`×1, `DIFFICULTY-EASIEST`×1, `DIFFICULTY-EASY`×1, `DIFFICULTY-EXTREME`×1, `DIFFICULTY-HARD`×1, `DIFFICULTY-HARDEST`×1, `DIFFICULTY-MODERATE`×1 | scenario difficulty DE |  |
| AP_Genghis_1 | 4 | Mongols-scn1.ai | yes | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-EXTREME`×1, `!DIFFICULTY-HARD`×1, `!DIFFICULTY-HARDEST`×1, `!DIFFICULTY-MODERATE`×1, `DIFFICULTY-EASIEST`×1, `DIFFICULTY-EASY`×1, `DIFFICULTY-EXTREME`×1, `DIFFICULTY-HARD`×1, `DIFFICULTY-HARDEST`×1, `DIFFICULTY-MODERATE`×1 | scenario difficulty DE |  |
| AP_Genghis_1 | 5 | Mongols-scn1 player 5.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Genghis_1 | 6 | Mongols-scn1.ai | yes | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-EXTREME`×1, `!DIFFICULTY-HARD`×1, `!DIFFICULTY-HARDEST`×1, `!DIFFICULTY-MODERATE`×1, `DIFFICULTY-EASIEST`×1, `DIFFICULTY-EASY`×1, `DIFFICULTY-EXTREME`×1, `DIFFICULTY-HARD`×1, `DIFFICULTY-HARDEST`×1, `DIFFICULTY-MODERATE`×1 | scenario difficulty DE |  |
| AP_Genghis_1 | 7 | Mongols-scn1 player 7.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Genghis_1 | 8 | Mongols-scn1.ai | yes | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-EXTREME`×1, `!DIFFICULTY-HARD`×1, `!DIFFICULTY-HARDEST`×1, `!DIFFICULTY-MODERATE`×1, `DIFFICULTY-EASIEST`×1, `DIFFICULTY-EASY`×1, `DIFFICULTY-EXTREME`×1, `DIFFICULTY-HARD`×1, `DIFFICULTY-HARDEST`×1, `DIFFICULTY-MODERATE`×1 | scenario difficulty DE |  |
| AP_Genghis_2 | 0 | RandomGame | GAIA | 0 |  |  |  |  |
| AP_Genghis_2 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_2 | 2 | Mongols-scn2 player 2.ai | yes | 1 | `<= hard`×1 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_2 | 3 | Mongols-scn2 player 3.ai | yes | 4 | `<= hard`×1 ⚠, `<= moderate`×1, `== hard`×1, `== moderate`×1 |  | scenario difficulty DE |  |
| AP_Genghis_2 | 4 | Mongols-scn2 player 4.ai | yes | 1 | `== easy`×1 |  |  | `(set-difficulty-parameter ability-to-maintain-distance 100)`; `(set-difficulty-parameter ability-to-dodge-missiles 100)` |
| AP_Genghis_3 | 0 | PromiDE | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_3 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_3 | 2 | Mongols-scn3 player 2.ai | yes | 7 | `== easy`×2, `== hard`×3, `== moderate`×2 |  | scenario difficulty DE |  |
| AP_Genghis_3 | 3 | Mongols-scn3 player 3.ai | yes | 2 | `equal hard`×2 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_3 | 4 | Mongols-scn3 player 4.ai | yes | 4 | `== normal`×2 ⚠, `equal hard`×2 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_3 | 5 | Mongols-scn3 player 5.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Genghis_3 | 6 | Mongols-scn3 player 6.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Genghis_4 | 0 | _ajl | GAIA | 0 |  |  |  |  |
| AP_Genghis_4 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_4 | 2 | Mongols-scn4 player 2.ai | yes | 5 | `== easy`×1, `== hard`×2, `== moderate`×1, `== normal`×1 ⚠ |  |  |  |
| AP_Genghis_4 | 3 | Mongols-scn4 player 3.ai | yes | 2 | `== normal`×2 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_4 | 4 | Mongols-scn4 player 4.ai | yes | 21 | `== easy`×3, `== hard`×13, `== moderate`×4, `== normal`×1 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_4 | 5 | Greg's Peaceful | inactive | 0 |  |  |  |  |
| AP_Genghis_5 | 0 | PromiDE | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_5 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_5 | 2 | Mongols-scn5 player 2.ai | yes | 10 | `<= moderate`×1, `== hard`×3, `== moderate`×3, `== normal`×3 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_5 | 3 | Mongols-scn5 player 3.ai | yes | 2 | `== hard`×1, `== normal`×1 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_5 | 4 | Mongols-scn5 player 4.ai | yes | 9 | `== hard`×3, `== moderate`×3, `== normal`×3 ⚠ |  | scenario difficulty DE |  |
| AP_Genghis_6 | 0 | RandomGame | GAIA | 0 |  |  |  |  |
| AP_Genghis_6 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Genghis_6 | 2 | Mongols-scn6 player 2.ai | yes | 6 | `== easy`×2, `== hard`×2, `== moderate`×2 |  | scenario difficulty DE |  |
| AP_Genghis_6 | 3 | Joan-noncombat | inactive | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_1 | 0 | Promisory | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_1 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_1 | 2 | Joan-noncombat.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_1 | 3 | Joan-noncombat.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_1 | 4 | Joan-noncombat.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_1 | 5 | Joan-scn1 player 5.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_1 | 6 | Joan-noncombat.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_2 | 0 | Promisory | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_2 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_2 | 2 | Joan-scn2 player 2.ai | yes | 14 | `< easy`×1 ⚠, `<= moderate`×1, `== easy`×4, `== hard`×4, `== moderate`×4 |  | scenario difficulty DE |  |
| AP_Joan_2 | 3 | Joan-scn2 player 3.ai | yes | 12 | `<= moderate`×1, `== easy`×3, `== hard`×4, `== moderate`×4 |  | scenario difficulty DE |  |
| AP_Joan_2 | 4 | Joan-scn2 player 4.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_2 | 5 | Joan-noncombat.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_2 | 6 | Joan-noncombat.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_2 | 7 | Joan-scn2 player 7.ai | yes | 9 | `< easy`×1 ⚠, `<= moderate`×1, `== easy`×3, `== hard`×2, `== moderate`×2 |  | scenario difficulty DE |  |
| AP_Joan_3 | 0 | Promisory | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_3 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_3 | 2 | Joan-scn3 player 2.ai | yes | 16 | `<= moderate`×3, `== easy`×5, `== hard`×4, `== moderate`×4 |  | scenario difficulty DE |  |
| AP_Joan_3 | 3 | Joan-scn3 player 3.ai | yes | 12 | `== easy`×4, `== hard`×4, `== moderate`×4 |  | scenario difficulty DE |  |
| AP_Joan_3 | 4 | Joan-scn3 player 4.ai | yes | 9 | `<= moderate`×1, `== easy`×2, `== hard`×3, `== moderate`×3 |  | scenario difficulty DE |  |
| AP_Joan_4 | 0 | PromiDE | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_4 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_4 | 2 | Joan-scn4 player 2.ai | yes | 7 | `<= moderate`×3, `== easy`×2, `== hard`×1, `== moderate`×1 |  | scenario difficulty DE |  |
| AP_Joan_4 | 3 | Joan-scn4 player 3.ai | yes | 11 | `<= moderate`×6, `== easy`×3, `== hard`×1, `== moderate`×1 |  | scenario difficulty DE |  |
| AP_Joan_4 | 4 | Joan-scn4 player 4.ai | yes | 16 | `< moderate`×1 ⚠, `<= moderate`×3, `== easy`×5, `== hard`×3, `== moderate`×3, `>= moderate`×1 ⚠ |  | scenario difficulty DE |  |
| AP_Joan_4 | 5 | Fe Immobile AI.ai | yes | 0 |  |  |  |  |
| AP_Joan_5 | 0 | Promisory | GAIA | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_5 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_5 | 2 | Joan-scn5 player 2.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_5 | 3 | Joan-scn5 player 3.ai | yes | 0 |  |  | scenario difficulty DE | `(set-difficulty-parameter ability-to-maintain-distance 100)`; `(set-difficulty-parameter ability-to-dodge-missiles 100)` |
| AP_Joan_5 | 4 | Joan-scn5 player 4.ai | yes | 0 |  |  | scenario difficulty DE |  |
| AP_Joan_5 | 5 | Fe Immobile AI.ai | yes | 0 |  |  |  |  |
| AP_Joan_6 | 0 | _ajl | GAIA | 0 |  |  |  |  |
| AP_Joan_6 | 1 | PromiDE | P1 (human) | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |
| AP_Joan_6 | 2 | Joan-scn6 player 2.ai | yes | 5 | `<= moderate`×4, `== easy`×1 |  | scenario difficulty DE |  |
| AP_Joan_6 | 3 | Joan-scn6 player 3.ai | yes | 11 | `<= moderate`×3, `== easy`×2, `== hard`×4, `== moderate`×2 |  | scenario difficulty DE |  |
| AP_Joan_6 | 4 | Joan-scn6 player 4.ai | yes | 7 | `<= moderate`×5, `== easy`×2 |  | scenario difficulty DE |  |
| AP_Joan_6 | 5 | Promisory | inactive | 0 |  | `!DIFFICULTY-EASIEST`×1, `!DIFFICULTY-EASY`×1, `!DIFFICULTY-MODERATE`×1 |  |  |

## Guarded rules per script

Each rule: line, difficulty test(s), remaining conditions → actions (chat/disable-self dropped).

### AP_Attila_1 p3 — Attila-scn1 player 3.ai

- L137 `== standard` | (defend-soldier-count >= 10); (timer-triggered 1) → attack-now; disable-timer 1; enable-timer 1 600
- L148 `<= moderate` | (defend-soldier-count >= 10); (timer-triggered 1) → attack-now; disable-timer 1; enable-timer 1 300
- L205 `<= moderate` | (unit-type-count-total villager < 40); (can-train villager) → train villager
- L214 `== easy` | (unit-type-count-total villager < 20); (can-train villager) → train villager
- L275 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 7); (can-build farm) → build farm
- L285 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 13); (can-build farm) → build farm
- L405 `== easy` | (unit-type-count-total cavalry-archer-line < 12); (can-train cavalry-archer-line) → train cavalry-archer-line
- L414 `<= moderate` | (unit-type-count-total cavalry-archer-line < 17); (can-train cavalry-archer-line) → train cavalry-archer-line
- L424 `== easy` | (unit-type-count-total my-unique-unit < 8); (can-train my-unique-unit) → train my-unique-unit
- L433 `<= moderate` | (unit-type-count-total my-unique-unit < 14); (can-train my-unique-unit) → train my-unique-unit

### AP_Attila_1 p4 — Attila-scn1 player 4.ai

- L114 `== easy` | (unit-type-count-total villager < 20); (can-train villager) → train villager
- L123 `<= moderate` | (unit-type-count-total villager < 30); (can-train villager) → train villager
- L194 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 10); (can-build farm) → build farm
- L204 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 15); (can-build farm) → build farm
- L337 `== easy` | (game-time greater-than 360); (unit-type-count-total mangonel-line < 2); (can-train mangonel-line) → train mangonel-line
- L347 `<= moderate` | (game-time greater-than 360); (unit-type-count-total mangonel-line < 4); (can-train mangonel-line) → train mangonel-line
- L357 `== easy` | (game-time greater-than 360); (unit-type-count-total knight-line < 14); (can-train knight-line) → train knight-line
- L367 `<= moderate` | (game-time greater-than 360); (unit-type-count-total knight-line < 20); (can-train knight-line) → train knight-line
- L377 `== easy` | (unit-type-count-total galley-line < 8); (can-train galley-line) → train galley-line
- L386 `<= moderate` | (unit-type-count-total galley-line < 12); (can-train galley-line) → train galley-line
- L395 `== easy` | (unit-type-count-total war-elephant-line < 7); (can-train war-elephant-line) → train war-elephant-line
- L404 `<= moderate` | (unit-type-count-total war-elephant-line < 12); (can-train war-elephant-line) → train war-elephant-line

### AP_Attila_1 p5 — Attila-scn1 player 5.ai

- L45 `== easy` | (event-detected trigger 12); (timer-triggered 1) → cc-add-resource food 300; cc-add-resource wood 300; cc-add-resource gold 300; disable-timer 1; enable-timer 1 600
- L58 `<= moderate` | (event-detected trigger 12); (timer-triggered 1) → cc-add-resource food 600; cc-add-resource wood 600; cc-add-resource gold 600; disable-timer 1; enable-timer 1 600
- L96 `== easy` | (unit-type-count-total militiaman-line < 12); (can-train militiaman-line) → train militiaman-line
- L105 `<= moderate` | (unit-type-count-total militiaman-line < 22); (can-train militiaman-line) → train militiaman-line
- L114 `== easy` | (unit-type-count-total archer-line < 6); (can-train archer-line) → train archer-line
- L123 `<= moderate` | (unit-type-count-total archer-line < 15); (can-train archer-line) → train archer-line
- L132 `<= moderate` | (or (game-time > 900) (difficulty <= moderate) ); (can-research ri-man-at-arms) → research ri-man-at-arms
- L150 `<= moderate` | (can-research ri-fletching) → research ri-fletching
- L158 `<= moderate` | (can-research ri-padded-archer-armor) → research ri-padded-archer-armor
- L166 `<= moderate` | (can-research ri-scale-mail) → research ri-scale-mail

### AP_Attila_2 p5 — Attila-scn2 player 5.ai

- L15 `<= moderate` |  → set-signal 1
- L22 `== hard` |  → set-signal 2

### AP_Attila_2 p7 — Attila-scn2 player 7.ai

- L35 `<= moderate` | (timer-triggered 2) → set-strategic-number sn-percent-attack-soldiers 50; attack-now; enable-timer 1 600
- L79 `== normal` | (unit-type-count-total villager < 24); (can-train villager) → train villager
- L88 `<= moderate` | (unit-type-count-total villager < 34); (can-train villager) → train villager
- L139 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 7); (can-build farm) → build farm
- L149 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 10); (can-build farm) → build farm
- L161 `<= moderate` | (game-time greater-than 360); (unit-type-count-total battering-ram-line > 0); (unit-type-count-total scorpion-line < 4); (can-train scorpion-line) → train scorpion-line
- L181 `== normal` | (game-time greater-than 360); (unit-type-count-total knight-line < 6); (can-train knight-line) → train knight-line
- L191 `<= moderate` | (game-time greater-than 360); (unit-type-count-total knight-line < 12); (can-train knight-line) → train knight-line
- L201 `== normal` | (game-time greater-than 360); (unit-type-count-total militiaman-line < 6); (can-train militiaman-line) → train militiaman-line
- L211 `<= moderate` | (game-time greater-than 360); (unit-type-count-total militiaman-line < 12); (can-train militiaman-line) → train militiaman-line
- L221 `== normal` | (game-time greater-than 360); (unit-type-count-total spearman-line < 6); (can-train spearman-line) → train spearman-line
- L231 `<= moderate` | (game-time greater-than 360); (unit-type-count-total spearman-line < 12); (can-train spearman-line) → train spearman-line

### AP_Attila_3 p3 — Attila-scn3 player 3.ai

- L59 `<= moderate` | (timer-triggered 2); (unit-type-count-total villager > 10) → cc-add-resource gold 75; disable-timer 2; enable-timer 2 60
- L78 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L87 `<= moderate` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L140 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 10); (can-build farm) → build farm
- L150 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 15); (can-build farm) → build farm
- L196 `== easy` | (unit-type-count-total militiaman-line less-than 10); (can-train militiaman-line) → train militiaman
- L205 `<= moderate` | (unit-type-count-total militiaman-line less-than 20); (can-train militiaman-line) → train militiaman

### AP_Attila_3 p4 — Attila-scn3 player 4.ai

- L59 `<= moderate` | (timer-triggered 2); (unit-type-count-total villager > 10) → cc-add-resource gold 75; disable-timer 2; enable-timer 2 60
- L69 `<= moderate` | (timer-triggered 1); (defend-soldier-count >= 8) → disable-timer 1; enable-timer 1 560; attack-now
- L79 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L88 `<= moderate` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L150 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 10); (can-build farm) → build farm
- L160 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 15); (can-build farm) → build farm
- L222 `<= moderate` | (unit-type-count-total spearman-line less-than 12); (can-train spearman-line) → train spearman
- L231 `== easy` | (unit-type-count-total militiaman-line less-than 6); (can-train militiaman-line) → train militiaman
- L240 `== easy` | (unit-type-count-total archer-line less-than 8); (can-train archer-line) → train archer-line
- L251 `<= moderate` | (unit-type-count-total archer-line less-than 18); (can-train archer-line) → train archer-line

### AP_Attila_4 p2 — Attila-scn4 player 2.ai

- L163 `<= moderate` | (or (difficulty <= moderate) (players-stance 1 ally) ); (timer-triggered 1); (defend-soldier-count >= 10) → attack-now; disable-timer 1; enable-timer 1 520
- L336 `<= moderate` | (or (difficulty <= moderate) (players-stance 1 ally) ); (unit-type-count-total archer-line < 15); (can-train archer-line) → train archer-line

### AP_Attila_4 p3 — Attila-scn4 player 3.ai

- L70 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L79 `<= moderate` | (unit-type-count-total villager less-than 35); (can-train villager) → train villager
- L157 `<= moderate` | (building-type-count-total castle less-than 2); (can-build castle) → build castle
- L167 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 10); (can-build farm) → build farm
- L177 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 15); (can-build farm) → build farm
- L297 `<= moderate` | (unit-type-count-total militiaman-line < 10); (can-train militiaman-line) → train militiaman-line
- L314 `<= moderate` | (and (difficulty <= moderate) (current-age == imperial-age) ); (unit-type-count-total knight-line < 30); (can-train knight-line) → train knight-line
- L335 `<= moderate` | (and (difficulty <= moderate) (current-age == imperial-age) ); (unit-type-count-total throwing-axeman-line < 25); (can-train throwing-axeman-line) → train throwing-axeman-line

### AP_Attila_4 p4 — Attila-scn4 player 4.ai

- L57 `== easy` |  → enable-timer 1 2200
- L64 `<= moderate` |  → enable-timer 1 1600
- L71 `== hard` | (timer-triggered 4) → cc-add-resource food 400; cc-add-resource wood 400; cc-add-resource gold 400; cc-add-resource stone 400; disable-timer 4; enable-timer 4 700
- L84 `== easy` | (timer-triggered 1); (defend-soldier-count >= 9) → attack-now; disable-timer 1; enable-timer 1 1020
- L95 `<= moderate` | (timer-triggered 1); (defend-soldier-count >= 20) → attack-now; disable-timer 1; enable-timer 1 720
- L106 `== easy` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L115 `<= moderate` | (unit-type-count-total villager less-than 45); (can-train villager) → train villager
- L176 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 10); (can-build farm) → build farm
- L186 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 15); (can-build farm) → build farm
- L237 `== easy` | (unit-type-count-total spearman-line < 10); (can-train spearman-line) → train spearman-line
- L246 `<= moderate` | (unit-type-count-total spearman-line < 20); (can-train spearman-line) → train spearman-line
- L255 `== easy` | (unit-type-count-total knight-line < 7); (can-train knight-line) → train knight-line
- L264 `<= moderate` | (unit-type-count-total knight-line < 30); (can-train knight-line) → train knight-line
- L273 `== easy` | (unit-type-count-total monk < 1); (can-train monk) → train monk
- L282 `== moderate` | (unit-type-count-total monk < 3); (can-train monk) → train monk
- L291 `== hard` | (unit-type-count-total monk < 6); (can-train monk) → train monk
- L300 `== easy` | (unit-type-count-total throwing-axeman-line < 10); (can-train throwing-axeman-line) → train throwing-axeman-line
- L309 `== moderate` | (unit-type-count-total throwing-axeman-line < 20); (can-train throwing-axeman-line) → train throwing-axeman-line
- L318 `== hard` | (unit-type-count-total throwing-axeman-line < 34); (can-train throwing-axeman-line) → train throwing-axeman-line
- L327 `<= moderate` | (unit-type-count-total scorpion-line < 5); (can-train scorpion-line) → train scorpion-line

### AP_Attila_5 p2 — Attila-scn5 player 2.ai

- L141 `== easy` | (unit-type-count-total villager less-than 35); (can-train villager) → train villager
- L150 `<= moderate` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L227 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 14); (can-build farm) → build farm
- L237 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 9); (can-build farm) → build farm
- L373 `== easy` | (unit-type-count-total militiaman-line less-than 25); (can-train militiaman-line) → train militiaman
- L382 `== moderate` | (unit-type-count-total militiaman-line less-than 20); (can-train militiaman-line) → train militiaman
- L391 `== hard` | (unit-type-count-total militiaman-line less-than 15); (can-train militiaman-line) → train militiaman
- L409 `== easy` | (unit-type-count-total trebuchet-set less-than 2); (can-train trebuchet) → train trebuchet
- L418 `== easy` | (unit-type-count-total knight-line less-than 14); (can-train knight-line) → train knight-line
- L427 `== moderate` | (unit-type-count-total knight-line less-than 11); (can-train knight-line) → train knight-line
- L436 `== hard` | (unit-type-count-total knight-line less-than 8); (can-train knight-line) → train knight-line

### AP_Attila_5 p3 — Attila-scn5 player 3.ai

- L74 `== easy` |  → enable-timer 1 1520; set-strategic-number sn-cap-civilian-builders 3
- L82 `== moderate` |  → enable-timer 1 1320; set-strategic-number sn-cap-civilian-builders 4
- L90 `== hard` |  → enable-timer 1 1120; set-strategic-number sn-cap-civilian-builders 5
- L107 `<= moderate` | (timer-triggered 1); (defend-soldier-count >= 14) → disable-timer 1; enable-timer 1 660; attack-now
- L117 `== easy` | (timer-triggered 1); (defend-soldier-count >= 8) → disable-timer 1; enable-timer 1 1200; attack-now
- L128 `== easy` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L138 `<= moderate` | (game-time < 1800); (unit-type-count-total villager less-than 35); (can-train villager) → train villager
- L148 `<= moderate` | (game-time > 1800); (unit-type-count-total villager less-than 45); (can-train villager) → train villager
- L226 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 7); (can-build farm) → build farm
- L236 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 16); (can-build farm) → build farm
- L290 `== easy` | (can-build watch-tower); (building-type-count-total watch-tower < 6) → build watch-tower
- L298 `<= moderate` | (can-build watch-tower); (building-type-count-total watch-tower < 10) → build watch-tower
- L307 `== easy` | (game-time greater-than 100); (unit-type-count-total my-unique-unit-line less-than 6); (can-train my-unique-unit-line) → train my-unique-unit-line
- L317 `== moderate` | (game-time greater-than 100); (unit-type-count-total my-unique-unit-line less-than 15); (can-train my-unique-unit-line) → train my-unique-unit-line
- L327 `== hard` | (game-time greater-than 100); (unit-type-count-total my-unique-unit-line less-than 22); (can-train my-unique-unit-line) → train my-unique-unit-line
- L337 `== easy` | (game-time greater-than 100); (unit-type-count-total militiaman-line less-than 8); (can-train militiaman-line) → train militiaman
- L347 `== moderate` | (game-time greater-than 100); (unit-type-count-total militiaman-line less-than 20); (can-train militiaman-line) → train militiaman
- L357 `== hard` | (game-time greater-than 100); (unit-type-count-total militiaman-line less-than 30); (can-train militiaman-line) → train militiaman
- L376 `== easy` | (game-time greater-than 100); (unit-type-count-total trebuchet-set less-than 2); (can-train trebuchet) → train trebuchet
- L386 `<= moderate` | (game-time greater-than 100); (unit-type-count-total trebuchet-set less-than 4); (can-train trebuchet) → train trebuchet
- L396 `== easy` | (game-time greater-than 100); (unit-type-count-total scorpion-line < 2); (can-train scorpion-line) → train scorpion-line
- L406 `== moderate` | (game-time greater-than 100); (unit-type-count-total scorpion-line less-than 4); (can-train scorpion-line) → train scorpion-line
- L416 `== hard` | (game-time greater-than 100); (unit-type-count-total scorpion-line less-than 8); (can-train scorpion-line) → train scorpion-line

### AP_Attila_5 p4 — Attila-scn5 player 4.ai

- L68 `== easy` |  → enable-timer 1 1020; set-strategic-number sn-cap-civilian-builders 3
- L76 `== moderate` |  → enable-timer 1 820; set-strategic-number sn-cap-civilian-builders 4
- L84 `== hard` |  → enable-timer 1 620; set-strategic-number sn-cap-civilian-builders 5
- L92 `<= moderate` | (timer-triggered 1); (defend-soldier-count >= 15) → disable-timer 1; enable-timer 1 300; attack-now
- L102 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L112 `<= moderate` | (game-time < 1800); (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L122 `<= moderate` | (game-time > 1800); (unit-type-count-total villager less-than 40); (can-train villager) → train villager
- L200 `== easy` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 9); (can-build farm) → build farm
- L210 `<= moderate` | (idle-farm-count <= 1); (game-time greater-than 300); (building-type-count-total farm less-than 18); (can-build farm) → build farm
- L326 `== easy` | (game-time greater-than 100); (unit-type-count-total militiaman-line less-than 15); (can-train militiaman-line) → train militiaman
- L336 `== moderate` | (game-time greater-than 100); (unit-type-count-total militiaman-line less-than 20); (can-train militiaman-line) → train militiaman
- L346 `== hard` | (game-time greater-than 100); (unit-type-count-total militiaman-line less-than 30); (can-train militiaman-line) → train militiaman
- L356 `== easy` | (game-time greater-than 100); (unit-type-count-total spearman-line less-than 10); (can-train spearman-line) → train spearman
- L366 `== moderate` | (game-time greater-than 100); (unit-type-count-total spearman-line less-than 15); (can-train spearman-line) → train spearman
- L376 `== hard` | (game-time greater-than 100); (unit-type-count-total spearman-line less-than 20); (can-train spearman-line) → train spearman
- L395 `== moderate` | (game-time greater-than 100); (unit-type-count-total huskarl-line less-than 15); (can-train huskarl-line) → train huskarl
- L405 `== hard` | (game-time greater-than 100); (unit-type-count-total huskarl-line less-than 20); (can-train huskarl-line) → train huskarl
- L415 `== easy` | (game-time greater-than 100); (unit-type-count-total trebuchet-set less-than 2); (can-train trebuchet) → train trebuchet
- L425 `== moderate` | (game-time greater-than 100); (unit-type-count-total trebuchet-set less-than 4); (can-train trebuchet) → train trebuchet
- L435 `== hard` | (game-time greater-than 100); (unit-type-count-total trebuchet-set less-than 5); (can-train trebuchet) → train trebuchet
- L445 `== easy` | (game-time greater-than 100); (not (town-under-attack)); (unit-type-count-total battering-ram-line less-than 3); (can-train battering-ram-line) → train battering-ram-line
- L456 `<= moderate` | (game-time greater-than 100); (not (town-under-attack)); (unit-type-count-total battering-ram-line less-than 6); (can-train battering-ram-line) → train battering-ram-line

### AP_Attila_5 p5 — Attila-scn5 player 5.ai

- L59 `== easy` |  → enable-timer 1 1320; set-strategic-number sn-cap-civilian-builders 3
- L67 `== moderate` |  → enable-timer 1 1120; set-strategic-number sn-cap-civilian-builders 4
- L75 `== hard` |  → enable-timer 1 920; set-strategic-number sn-cap-civilian-builders 5
- L300 `== easy` | (unit-type-count-total cavalry-archer-line less-than 10); (can-train cavalry-archer-line) → train cavalry-archer
- L309 `<= moderate` | (unit-type-count-total cavalry-archer-line less-than 15); (can-train cavalry-archer-line) → train cavalry-archer
- L318 `== easy` | (and (difficulty == easy) (current-age == imperial-age) ); (unit-type-count-total cavalry-archer-line less-than 15); (can-train cavalry-archer-line) → train cavalry-archer
- L330 `== moderate` | (and (difficulty == moderate) (current-age == imperial-age) ); (unit-type-count-total cavalry-archer-line less-than 20); (can-train cavalry-archer-line) → train cavalry-archer
- L342 `== hard` | (and (difficulty == hard) (current-age == imperial-age) ); (unit-type-count-total cavalry-archer-line less-than 25); (can-train cavalry-archer-line) → train cavalry-archer
- L354 `== easy` | (unit-type-count-total knight-line less-than 6); (can-train knight-line) → train knight
- L363 `<= moderate` | (unit-type-count-total knight-line less-than 8); (can-train knight-line) → train knight
- L372 `== easy` | (and (difficulty == easy) (current-age == imperial-age) ); (unit-type-count-total knight-line less-than 10); (can-train knight-line) → train knight
- L384 `== moderate` | (and (difficulty == moderate) (current-age == imperial-age) ); (unit-type-count-total knight-line less-than 12); (can-train knight-line) → train knight
- L396 `== hard` | (and (difficulty == hard) (current-age == imperial-age) ); (unit-type-count-total knight-line less-than 15); (can-train knight-line) → train knight
- L408 `== easy` | (game-time greater-than 300); (unit-type-count-total trebuchet-set less-than 2); (can-train trebuchet) → train trebuchet
- L418 `<= moderate` | (game-time greater-than 300); (unit-type-count-total trebuchet-set less-than 3); (can-train trebuchet) → train trebuchet
- L428 `<= moderate` | (game-time greater-than 300); (not (town-under-attack)); (unit-type-count-total mangonel-line less-than 4); (can-train mangonel-line) → train mangonel-line

### AP_Attila_6 p2 — Attila-scn6 player 2.ai

- L93 `== easy` | (event-detected trigger 6) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 5
- L103 `== moderate` | (event-detected trigger 6) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 10
- L113 `== hard` | (event-detected trigger 6) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 20
- L169 `== easy` | (unit-type-count-total knight-line < 6); (can-train knight-line) → train knight-line
- L178 `<= moderate` | (unit-type-count-total knight-line < 16); (can-train knight-line) → train knight-line
- L187 `== easy` | (unit-type-count-total scout-cavalry-line < 6); (can-train scout-cavalry-line) → train scout-cavalry-line
- L196 `<= moderate` | (unit-type-count-total scout-cavalry-line < 16); (can-train scout-cavalry-line) → train scout-cavalry-line
- L213 `== easy` | (unit-type-count-total spearman-line < 12); (can-train spearman-line) → train spearman-line
- L222 `<= moderate` | (unit-type-count-total spearman-line < 25); (can-train spearman-line) → train spearman-line

### AP_Attila_6 p3 — Attila-scn6 player 3.ai

- L91 `== easy` | (event-detected trigger 3) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 5
- L101 `== moderate` | (event-detected trigger 3) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 10
- L111 `== hard` | (event-detected trigger 3) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 20
- L167 `== easy` | (unit-type-count-total knight-line < 6); (can-train knight-line) → train knight-line
- L176 `<= moderate` | (unit-type-count-total knight-line < 18); (can-train knight-line) → train knight-line
- L185 `<= moderate` | (unit-type-count-total trebuchet-set < 4); (can-train trebuchet) → train trebuchet
- L202 `== easy` | (unit-type-count-total archer-line < 12); (can-train archer-line) → train archer-line
- L211 `<= moderate` | (unit-type-count-total archer-line < 25); (can-train archer-line) → train archer-line

### AP_Attila_6 p4 — Attila-scn6 player 4.ai

- L93 `== easy` | (event-detected trigger 7) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 5
- L103 `== moderate` | (event-detected trigger 7) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 10
- L113 `== hard` | (event-detected trigger 7) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 20
- L168 `== easy` | (unit-type-count-total knight-line < 10); (can-train knight-line) → train knight-line
- L177 `<= moderate` | (unit-type-count-total knight-line < 30); (can-train knight-line) → train knight-line
- L186 `<= moderate` | (unit-type-count-total trebuchet-set < 4); (can-train trebuchet) → train trebuchet
- L195 `<= moderate` | (unit-type-count-total monk < 4); (can-train monk) → train monk
- L204 `== easy` | (unit-type-count-total throwing-axeman-line < 8); (can-train throwing-axeman-line) → train throwing-axeman-line
- L213 `<= moderate` | (unit-type-count-total throwing-axeman-line < 16); (can-train throwing-axeman-line) → train throwing-axeman-line
- L222 `== easy` | (unit-type-count-total archer-line < 6); (can-train archer-line) → train archer-line
- L231 `<= moderate` | (unit-type-count-total archer-line < 12); (can-train archer-line) → train archer-line

### AP_Attila_6 p5 — Attila-scn6 player 5.ai

- L84 `== easy` | (event-detected trigger 8) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 5
- L94 `<= moderate` | (event-detected trigger 8) → set-strategic-number sn-percent-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 0; set-strategic-number sn-cap-civilian-builders 10
- L104 `== easy` | (event-detected trigger 9) → cc-add-resource food 400; cc-add-resource wood 400; cc-add-resource gold 400; cc-add-resource stone 400; set-strategic-number sn-cap-civilian-builders 20
- L116 `<= moderate` | (event-detected trigger 9) → cc-add-resource food 700; cc-add-resource wood 700; cc-add-resource gold 700; cc-add-resource stone 700; set-strategic-number sn-cap-civilian-builders 30
- L173 `== easy` | (unit-type-count-total archer-line < 10); (can-train archer-line) → train archer-line
- L182 `<= moderate` | (unit-type-count-total archer-line < 15); (can-train archer-line) → train archer-line
- L191 `== easy` | (unit-type-count-total my-unique-unit-line < 8); (can-train my-unique-unit-line) → train my-unique-unit-line
- L200 `<= moderate` | (unit-type-count-total my-unique-unit-line < 15); (can-train my-unique-unit-line) → train my-unique-unit-line
- L209 `== easy` | (unit-type-count-total militiaman-line < 8); (can-train militiaman-line) → train militiaman-line
- L218 `<= moderate` | (unit-type-count-total militiaman-line < 18); (can-train militiaman-line) → train militiaman-line

### AP_Genghis_1 p2 — Mongols-scn1 player 2.ai

- L27 `== hard` |  → set-signal 201

### AP_Genghis_2 p2 — Mongols-scn2 player 2.ai

- L103 `<= hard` | (timer-triggered 4) → cc-add-resource food 700; cc-add-resource wood 700; cc-add-resource gold 700; disable-timer 4; enable-timer 4 2700

### AP_Genghis_2 p3 — Mongols-scn2 player 3.ai

- L71 `<= hard` | (timer-triggered 4) → cc-add-resource food 700; cc-add-resource wood 700; cc-add-resource gold 700; cc-add-resource stone 700; disable-timer 4; enable-timer 4 2700
- L241 `<= moderate` | (building-type-count-total castle less-than 1); (can-build castle) → build castle
- L319 `== moderate` | (game-time greater-than 360); (unit-type-count-total mangudai-line less-than 8); (can-train mangudai-line) → train mangudai-line
- L330 `== hard` | (game-time greater-than 360); (unit-type-count-total mangudai-line less-than 12); (can-train mangudai-line) → train mangudai-line

### AP_Genghis_2 p4 — Mongols-scn2 player 4.ai

- L57 `== easy` |  → set-signal 201

### AP_Genghis_3 p2 — Mongols-scn3 player 2.ai

- L49 `== hard` | (not (player-in-game 4)) → cc-add-resource wood 1500; cc-add-resource gold 1500; cc-add-resource food 1500
- L352 `== easy` | (not (difficulty == easy)); (game-time greater-than 3600); (unit-type-count-total rocket-cart-line < 5); (can-train rocket-cart-line) → train rocket-cart-line
- L391 `== hard` | (unit-type-count-total fire-lancer-line < 8); (can-train fire-lancer-line) → train fire-lancer-line
- L400 `== moderate` | (unit-type-count-total fire-lancer-line < 5); (can-train fire-lancer-line) → train fire-lancer-line
- L409 `== easy` | (unit-type-count-total fire-lancer-line < 2); (can-train fire-lancer-line) → train fire-lancer-line
- L420 `== moderate` | (game-time greater-than 3600); (unit-type-count-total mounted-trebuchet < 1); (can-train mounted-trebuchet) → train mounted-trebuchet
- L430 `== hard` | (game-time greater-than 3300); (unit-type-count-total mounted-trebuchet < 2); (can-train mounted-trebuchet) → train mounted-trebuchet

### AP_Genghis_3 p3 — Mongols-scn3 player 3.ai

- L275 `equal hard` | (not (difficulty equal hard)); (unit-type-count-total scorpion-line less-than 5); (can-train scorpion-line) → train scorpion-line
- L284 `equal hard` | (unit-type-count-total scorpion-line less-than 7); (can-train scorpion-line) → train scorpion-line

### AP_Genghis_3 p4 — Mongols-scn3 player 4.ai

- L289 `equal hard` | (not (difficulty equal hard)); (current-age equal imperial-age); (unit-type-count-total rocket-cart-line less-than 2); (can-train rocket-cart-line) → train rocket-cart-line
- L299 `equal hard` | (current-age equal imperial-age); (unit-type-count-total rocket-cart-line less-than 5); (can-train rocket-cart-line) → train rocket-cart-line
- L387 `== normal` | (goal 16 98); (building-type-count-total wonder less-than 1); (can-build-with-escrow wonder); (not (difficulty == normal)) → set-strategic-number sn-percent-civilian-explorers 5; set-strategic-number sn-cap-civilian-explorers 1; set-strategic-number sn-minimum-civilian-explorers 1; set-strategic-number sn-percent-civilian-builders 80; set-strategic-number sn-cap-civilian-builders 100; set-strategic-number sn-percent-civilian-gatherers 15; set-doctrine 77
- L404 `== normal` | (goal 16 98); (building-type-count-total wonder less-than 1); (can-build-with-escrow wonder) → set-strategic-number sn-percent-civilian-explorers 5; set-strategic-number sn-cap-civilian-explorers 1; set-strategic-number sn-minimum-civilian-explorers 1; set-strategic-number sn-percent-civilian-builders 80; set-strategic-number sn-cap-civilian-builders 4; set-strategic-number sn-percent-civilian-gatherers 15; set-doctrine 77

### AP_Genghis_4 p2 — Mongols-scn4 player 2.ai

- L65 `== easy` | (unit-type-count-total skirmisher-line < 2); (can-train skirmisher-line) → train skirmisher-line
- L75 `== moderate` | (unit-type-count-total skirmisher-line < 3); (can-train skirmisher-line) → train skirmisher-line
- L85 `== hard` | (unit-type-count-total skirmisher-line < 4); (can-train skirmisher-line) → train skirmisher-line
- L123 `== normal` |  → set-signal 202
- L132 `== hard` |  → set-signal 203

### AP_Genghis_4 p3 — Mongols-scn4 player 3.ai

- L247 `== normal` | (not (difficulty == normal)); (unit-type-count-total my-unique-unit-line less-than 8); (can-train my-unique-unit-line) → train my-unique-unit-line
- L256 `== normal` | (unit-type-count-total my-unique-unit-line less-than 3); (can-train my-unique-unit-line) → train my-unique-unit-line

### AP_Genghis_4 p4 — Mongols-scn4 player 4.ai

- L308 `== hard` | (not (difficulty == hard)); (unit-type-count-total monk less-than 1); (can-train monk) → train monk
- L317 `== hard` | (not (difficulty == hard)); (unit-type-count-total cavalry-archer-line less-than 8); (can-train cavalry-archer-line) → train cavalry-archer-line
- L326 `== hard` | (not (difficulty == hard)); (unit-type-count-total knight-line less-than 8); (can-train knight-line) → train knight-line
- L344 `== hard` | (not (difficulty == hard)); (unit-type-count-total war-elephant-line less-than 8); (can-train war-elephant-line) → train war-elephant-line
- L354 `== normal` | (not (difficulty == normal)); (unit-type-count-total scorpion-line < 1); (can-train scorpion-line) → train scorpion-line
- L364 `== moderate` | (unit-type-count-total trebuchet-set < 1); (can-train trebuchet) → train trebuchet
- L375 `== hard` | (unit-type-count-total monk less-than 2); (can-train monk) → train monk
- L384 `== hard` | (unit-type-count-total cavalry-archer-line less-than 10); (can-train cavalry-archer-line) → train cavalry-archer-line
- L393 `== hard` | (unit-type-count-total knight-line less-than 11); (can-train knight-line) → train knight-line
- L403 `== hard` | (unit-type-count-total war-elephant-line less-than 11); (can-train war-elephant-line) → train war-elephant-line
- L413 `== hard` | (unit-type-count-total scorpion-line < 3); (can-train scorpion-line) → train scorpion-line
- L423 `== hard` | (unit-type-count-total trebuchet-set < 2); (can-train trebuchet) → train trebuchet
- L450 `== easy` | (timer-triggered 9); (food-amount < 200) → cc-add-resource food 60; disable-timer 9; enable-timer 9 60
- L460 `== moderate` | (timer-triggered 9); (food-amount < 400) → cc-add-resource food 112; disable-timer 9; enable-timer 9 60
- L470 `== hard` | (timer-triggered 9); (food-amount < 900) → cc-add-resource food 112; disable-timer 9; enable-timer 9 60
- L483 `== easy` | (timer-triggered 10); (wood-amount < 200) → cc-add-resource wood 60; disable-timer 10; enable-timer 10 60
- L493 `== moderate` | (timer-triggered 10); (wood-amount < 400) → cc-add-resource wood 90; disable-timer 10; enable-timer 10 60
- L503 `== hard` | (timer-triggered 10); (wood-amount < 700) → cc-add-resource wood 110; disable-timer 10; enable-timer 10 60
- L515 `== easy` | (timer-triggered 11); (gold-amount < 200) → cc-add-resource gold 60; disable-timer 11; enable-timer 11 60
- L525 `== moderate` | (timer-triggered 11); (gold-amount < 400) → cc-add-resource gold 90; disable-timer 11; enable-timer 11 60
- L535 `== hard` | (timer-triggered 11); (gold-amount < 600) → cc-add-resource gold 110; disable-timer 11; enable-timer 11 60

### AP_Genghis_5 p2 — Mongols-scn5 player 2.ai

- L66 `<= moderate` | (game-time > 420) → set-strategic-number sn-percent-attack-soldiers 30; attack-now
- L321 `== normal` | (unit-type-count-total militiaman-line < 9); (or (unit-type-count-total mangonel-line > 1) (town-under-attack) ); (can-train militiaman-line) → train militiaman-line
- L335 `== moderate` | (unit-type-count-total militiaman-line < 12); (or (unit-type-count-total mangonel-line > 1) (town-under-attack) ); (can-train militiaman-line) → train militiaman-line
- L348 `== hard` | (unit-type-count-total militiaman-line < 16); (or (unit-type-count-total mangonel-line > 1) (town-under-attack) ); (can-train militiaman-line) → train militiaman-line
- L363 `== normal` | (unit-type-count-total knight-line < 6); (or (unit-type-count-total mangonel-line > 1) (town-under-attack) ); (can-train knight-line) → train knight-line
- L376 `== moderate` | (unit-type-count-total knight-line < 8); (or (unit-type-count-total mangonel-line > 1) (town-under-attack) ); (can-train knight-line) → train knight-line
- L389 `== hard` | (unit-type-count-total knight-line < 11); (or (unit-type-count-total mangonel-line > 1) (town-under-attack) ); (can-train knight-line) → train knight-line
- L405 `== normal` | (unit-type-count-total mangonel-line < 2); (can-train mangonel-line) → train mangonel-line
- L414 `== moderate` | (unit-type-count-total mangonel-line < 4); (can-train mangonel-line) → train mangonel-line
- L423 `== hard` | (unit-type-count-total mangonel-line < 6); (can-train mangonel-line) → train mangonel-line

### AP_Genghis_5 p3 — Mongols-scn5 player 3.ai

- L84 `== normal` |  → set-signal 201
- L93 `== hard` |  → set-signal 202

### AP_Genghis_5 p4 — Mongols-scn5 player 4.ai

- L325 `== normal` | (unit-type-count-total spearman-line less-than 7); (can-train spearman-line) → train spearman-line
- L334 `== moderate` | (unit-type-count-total spearman-line less-than 9); (can-train spearman-line) → train spearman-line
- L343 `== hard` | (unit-type-count-total spearman-line less-than 12); (can-train spearman-line) → train spearman-line
- L354 `== normal` | (unit-type-count-total archer-line less-than 8); (can-train archer-line) → train archer-line
- L363 `== moderate` | (unit-type-count-total archer-line less-than 12); (can-train archer-line) → train archer-line
- L372 `== hard` | (unit-type-count-total archer-line less-than 15); (can-train archer-line) → train archer-line
- L391 `== normal` | (unit-type-count-total teutonic-knight-line less-than 5); (can-train teutonic-knight-line) → train teutonic-knight-line
- L400 `== moderate` | (unit-type-count-total teutonic-knight-line less-than 8); (can-train teutonic-knight-line) → train teutonic-knight-line
- L409 `== hard` | (unit-type-count-total teutonic-knight-line less-than 10); (can-train teutonic-knight-line) → train teutonic-knight-line

### AP_Genghis_6 p2 — Mongols-scn6 player 2.ai

- L234 `== easy` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L243 `== moderate` | (unit-type-count-total villager less-than 40); (can-train villager) → train villager
- L252 `== hard` | (unit-type-count-total villager less-than 50); (can-train villager) → train villager
- L437 `== easy` | (unit-type-count-total scorpion-line < 2); (can-train scorpion-line) → train scorpion-line
- L446 `== moderate` | (unit-type-count-total scorpion-line < 4); (can-train scorpion-line) → train scorpion-line
- L455 `== hard` | (unit-type-count-total scorpion-line < 5); (can-train scorpion-line) → train scorpion-line

### AP_Joan_2 p2 — Joan-scn2 player 2.ai

- L103 `<= moderate` | (unit-type-count-total villager > 16); (current-age == feudal-age) → set-goal 16 98
- L190 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L199 `== moderate` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L208 `== hard` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L218 `== easy` | (unit-type-count-total villager less-than 25); (current-age == castle-age); (can-train villager) → train villager
- L228 `== moderate` | (unit-type-count-total villager less-than 30); (current-age == castle-age); (can-train villager) → train villager
- L238 `== hard` | (unit-type-count-total villager less-than 35); (current-age == castle-age); (can-train villager) → train villager
- L282 `< easy` | (building-type-count-total monastery less-than 1); (can-build monastery) → build monastery
- L357 `== easy` | (up-compare-goal gl-available-food-amount > 75); (current-age == castle-age); (unit-type-count-total militiaman-line less-than 8); (can-train militiaman-line) → train militiaman-line
- L368 `== moderate` | (up-compare-goal gl-available-food-amount > 75); (current-age == castle-age); (unit-type-count-total militiaman-line less-than 12); (can-train militiaman-line) → train militiaman-line
- L379 `== hard` | (up-compare-goal gl-available-food-amount > 75); (current-age == castle-age); (unit-type-count-total militiaman-line less-than 17); (can-train militiaman-line) → train militiaman-line
- L390 `== easy` | (up-compare-goal gl-available-food-amount > 75); (current-age == castle-age); (unit-type-count-total spearman-line less-than 12); (can-train spearman-line) → train spearman-line
- L401 `== moderate` | (up-compare-goal gl-available-food-amount > 75); (current-age == castle-age); (unit-type-count-total spearman-line less-than 17); (can-train spearman-line) → train spearman-line
- L412 `== hard` | (up-compare-goal gl-available-food-amount > 75); (current-age == castle-age); (unit-type-count-total spearman-line less-than 21); (can-train spearman-line) → train spearman-line

### AP_Joan_2 p3 — Joan-scn2 player 3.ai

- L117 `== easy` | (unit-type-count-total villager less-than 15); (can-train villager) → train villager
- L126 `== moderate` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L135 `== hard` | (unit-type-count-total villager less-than 35); (can-train villager) → train villager
- L242 `== easy` | (unit-type-count-total longbowman-line < 6); (can-train longbowman-line) → train longbowman-line
- L251 `== moderate` | (unit-type-count-total longbowman-line < 12); (can-train longbowman-line) → train longbowman-line
- L260 `== hard` | (unit-type-count-total longbowman-line < 20); (can-train longbowman-line) → train longbowman-line
- L269 `<= moderate` | (unit-type-count-total monk less-than 1); (can-train monk) → train monk
- L278 `== easy` | (unit-type-count-total militiaman-line < 9); (can-train militiaman-line) → train militiaman-line
- L287 `== moderate` | (unit-type-count-total militiaman-line < 14); (can-train militiaman-line) → train militiaman-line
- L296 `== hard` | (unit-type-count-total militiaman-line < 18); (can-train militiaman-line) → train militiaman-line
- L305 `== moderate` | (game-time < 2400); (unit-type-count-total mangonel-line < 2); (can-train mangonel-line) → train mangonel-line
- L315 `== hard` | (game-time < 2400); (unit-type-count-total mangonel-line < 3); (can-train mangonel-line) → train mangonel-line

### AP_Joan_2 p7 — Joan-scn2 player 7.ai

- L116 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L125 `== moderate` | (unit-type-count-total villager less-than 26); (can-train villager) → train villager
- L134 `== hard` | (unit-type-count-total villager less-than 32); (can-train villager) → train villager
- L192 `< easy` | (building-type-count-total monastery less-than 1); (can-build monastery) → build monastery
- L253 `== easy` | (unit-type-count-total knight-line < 7); (can-train knight-line) → train knight-line
- L262 `== moderate` | (unit-type-count-total knight-line < 12); (can-train knight-line) → train knight-line
- L271 `== hard` | (unit-type-count-total knight-line < 15); (can-train knight-line) → train knight-line
- L288 `== easy` | (not (town-under-attack)); (unit-type-count-total battering-ram-line < 3); (can-train battering-ram-line) → train battering-ram-line
- L298 `<= moderate` | (not (town-under-attack)); (unit-type-count-total battering-ram-line < 4); (can-train battering-ram-line) → train battering-ram-line

### AP_Joan_3 p2 — Joan-scn3 player 2.ai

- L95 `== easy` |  → enable-timer 1 2000
- L102 `== moderate` |  → set-strategic-number sn-cap-civilian-builders 3; enable-timer 1 1200
- L110 `== hard` |  → set-strategic-number sn-cap-civilian-builders 5; enable-timer 1 900
- L128 `== easy` | (unit-type-count-total villager less-than 18); (can-train villager) → train villager
- L137 `== moderate` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L146 `== hard` | (unit-type-count-total villager less-than 32); (can-train villager) → train villager
- L213 `== easy` | (building-type-count-total barracks less-than 1); (can-build barracks) → build barracks
- L222 `<= moderate` | (building-type-count-total barracks less-than 2); (can-build barracks) → build barracks
- L270 `== easy` | (up-compare-goal gl-available-food-amount > 110); (unit-type-count-total militiaman-line < 10); (can-train militiaman-line) → train militiaman-line
- L280 `== moderate` | (up-compare-goal gl-available-food-amount > 60); (unit-type-count-total militiaman-line < 15); (can-train militiaman-line) → train militiaman-line
- L290 `== hard` | (up-compare-goal gl-available-food-amount > 60); (unit-type-count-total militiaman-line < 20); (can-train militiaman-line) → train militiaman-line
- L300 `== easy` | (up-compare-goal gl-available-food-amount > 110); (unit-type-count-total spearman-line < 8); (can-train spearman-line) → train spearman-line
- L310 `== moderate` | (up-compare-goal gl-available-food-amount > 60); (unit-type-count-total spearman-line < 12); (can-train spearman-line) → train spearman-line
- L320 `== hard` | (up-compare-goal gl-available-food-amount > 60); (unit-type-count-total spearman-line < 15); (can-train spearman-line) → train spearman-line
- L338 `<= moderate` | (unit-type-count-total mangonel-line < 4); (can-train mangonel-line) → train mangonel-line
- L347 `<= moderate` | (building-type-count-total watch-tower-line < 5); (can-build watch-tower-line) → build watch-tower-line

### AP_Joan_3 p3 — Joan-scn3 player 3.ai

- L118 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L126 `== moderate` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L134 `== hard` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L240 `== easy` | (unit-type-count-total longbowman-line < 10); (can-train longbowman-line) → train longbowman-line
- L249 `== moderate` | (unit-type-count-total longbowman-line < 14); (can-train longbowman-line) → train longbowman-line
- L258 `== hard` | (unit-type-count-total longbowman-line < 18); (can-train longbowman-line) → train longbowman-line
- L267 `== easy` | (unit-type-count-total knight-line < 5); (can-train knight-line) → train knight-line
- L276 `== moderate` | (unit-type-count-total knight-line < 8); (can-train knight-line) → train knight-line
- L285 `== hard` | (unit-type-count-total knight-line < 12); (can-train knight-line) → train knight-line
- L294 `== easy` | (unit-type-count-total militiaman-line < 8); (can-train militiaman-line) → train militiaman-line
- L303 `== moderate` | (unit-type-count-total militiaman-line < 12); (can-train militiaman-line) → train militiaman-line
- L312 `== hard` | (unit-type-count-total militiaman-line < 15); (can-train militiaman-line) → train militiaman-line

### AP_Joan_3 p4 — Joan-scn3 player 4.ai

- L94 `== moderate` |  → set-strategic-number sn-cap-civilian-builders 3
- L101 `== hard` |  → set-strategic-number sn-cap-civilian-builders 5
- L138 `== easy` | (unit-type-count-total villager less-than 25); (can-train villager) → train villager
- L146 `== moderate` | (unit-type-count-total villager less-than 35); (can-train villager) → train villager
- L154 `== hard` | (unit-type-count-total villager less-than 45); (can-train villager) → train villager
- L270 `<= moderate` | (unit-type-count-total villager > 20); (game-time > 2700); (current-age == castle-age) → set-goal 16 99
- L343 `== easy` | (unit-type-count-total knight-line < 8); (can-train knight-line) → train knight-line
- L352 `== moderate` | (unit-type-count-total knight-line < 12); (can-train knight-line) → train knight-line
- L361 `== hard` | (unit-type-count-total knight-line < 17); (can-train knight-line) → train knight-line

### AP_Joan_4 p2 — Joan-scn4 player 2.ai

- L161 `== easy` |  → enable-timer 1 2000
- L168 `== moderate` |  → set-strategic-number sn-cap-civilian-builders 3; enable-timer 1 1500
- L176 `== hard` |  → set-strategic-number sn-cap-civilian-builders 5; enable-timer 1 1200
- L350 `== easy` | (unit-type-count-total villager less-than 18); (can-train villager); (goal 2 1) → train villager
- L360 `<= moderate` | (unit-type-count-total villager less-than 45); (can-train villager); (goal 2 1) → train villager
- L430 `<= moderate` | (unit-type-count-total spearman-line < 30); (or (unit-type-count-total knight-line > 2) (town-under-attack) ); (can-train spearman-line); (goal 2 1) → train spearman-line
- L453 `<= moderate` | (unit-type-count-total knight-line < 18); (can-train knight-line); (goal 2 1) → train knight-line

### AP_Joan_4 p3 — Joan-scn4 player 3.ai

- L180 `== easy` | (event-detected trigger 15); (goal 2 1) → enable-timer 1 1240
- L189 `== moderate` | (event-detected trigger 15); (goal 2 1) → set-strategic-number sn-cap-civilian-builders 3; enable-timer 1 740
- L199 `== hard` | (event-detected trigger 15); (goal 2 1) → set-strategic-number sn-cap-civilian-builders 5; enable-timer 1 340
- L370 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L379 `<= moderate` | (unit-type-count-total villager less-than 42); (can-train villager); (goal 2 1) → train villager
- L485 `<= moderate` | (unit-type-count-total knight-line less-than 20); (can-train knight-line); (goal 2 1) → train knight-line
- L505 `<= moderate` | (not (town-under-attack)); (unit-type-count-total battering-ram-line less-than 5); (can-train battering-ram-line); (goal 2 1) → train battering-ram-line
- L516 `== easy` | (unit-type-count-total scorpion-line less-than 3); (can-train scorpion-line); (goal 2 1) → train scorpion-line
- L526 `<= moderate` | (unit-type-count-total scorpion-line less-than 5); (can-train scorpion-line); (goal 2 1) → train scorpion-line
- L536 `<= moderate` | (unit-type-count-total scorpion-line less-than 8); (can-train scorpion-line); (goal 2 1) → train scorpion-line
- L555 `<= moderate` | (unit-type-count-total cannon-galleon-line < 4); (can-train cannon-galleon-line); (goal 2 1) → train cannon-galleon-line

### AP_Joan_4 p4 — Joan-scn4 player 4.ai

- L152 `== easy` |  → enable-timer 2 2850
- L159 `== moderate` |  → set-strategic-number sn-cap-civilian-builders 3; enable-timer 2 2450
- L167 `== hard` |  → set-strategic-number sn-cap-civilian-builders 5; enable-timer 2 1850
- L292 `== easy` | (unit-type-count-total villager less-than 22); (can-train villager); (goal 2 1) → train villager
- L302 `== moderate` | (unit-type-count-total villager less-than 35); (can-train villager); (goal 2 1) → train villager
- L312 `== hard` | (unit-type-count-total villager less-than 45); (can-train villager); (goal 2 1) → train villager
- L346 `== easy` | (game-time > 1820); (unit-type-count-total villager > 20); (current-age == castle-age); (goal 2 1) → set-goal 16 99
- L357 `<= moderate` | (unit-type-count-total villager > 25); (current-age == castle-age); (goal 2 1) → set-goal 16 99
- L462 `<= moderate` | (unit-type-count-total longbowman-line less-than 20); (can-train longbowman-line); (goal 2 1) → train longbowman-line
- L481 `== moderate` | (unit-type-count-total knight-line less-than 5); (can-train knight-line); (goal 2 1) → train knight-line
- L491 `== hard` | (unit-type-count-total knight-line less-than 7); (can-train knight-line); (goal 2 1) → train knight-line
- L501 `== easy` | (unit-type-count-total mangonel-line less-than 1); (can-train mangonel-line); (goal 2 1) → train mangonel-line
- L511 `>= moderate` | (unit-type-count-total mangonel-line less-than 3); (can-train mangonel-line); (goal 2 1) → train mangonel-line
- L521 `< moderate` | (unit-type-count-total mangonel-line less-than 5); (can-train mangonel-line); (goal 2 1) → train mangonel-line
- L531 `== easy` | (unit-type-count-total trebuchet-set less-than 2); (can-train trebuchet); (goal 2 1) → train trebuchet
- L541 `<= moderate` | (unit-type-count-total trebuchet-set less-than 6); (can-train trebuchet); (goal 2 1) → train trebuchet

### AP_Joan_6 p2 — Joan-scn6 player 2.ai

- L96 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L105 `<= moderate` | (unit-type-count-total villager less-than 45); (can-train villager) → train villager
- L225 `<= moderate` | (event-detected trigger 1); (unit-type-count-total militiaman-line < 50); (can-train militiaman-line) → train militiaman-line
- L244 `<= moderate` | (event-detected trigger 1); (unit-type-count-total spearman-line < 35); (can-train spearman-line) → train spearman-line
- L263 `<= moderate` | (event-detected trigger 1); (unit-type-count-total monk < 3); (can-train monk) → train monk

### AP_Joan_6 p3 — Joan-scn6 player 3.ai

- L68 `== easy` | (event-detected trigger 1); (game-time > 2100) → set-strategic-number sn-percent-attack-soldiers 20; set-signal 30; attack-now; enable-timer 1 920
- L81 `== moderate` | (event-detected trigger 1); (game-time > 1700) → set-strategic-number sn-percent-attack-soldiers 25; set-signal 30; attack-now; enable-timer 1 920
- L94 `== hard` | (event-detected trigger 1); (game-time > 1400) → set-strategic-number sn-percent-attack-soldiers 30; set-signal 30; attack-now; enable-timer 1 920
- L131 `== easy` | (unit-type-count-total villager less-than 21); (can-train villager) → train villager
- L140 `== moderate` | (unit-type-count-total villager less-than 30); (can-train villager) → train villager
- L149 `== hard` | (unit-type-count-total villager less-than 40); (can-train villager) → train villager
- L292 `<= moderate` | (unit-type-count-total longbowman-line < 25); (can-train longbowman-line) → train longbowman-line
- L309 `<= moderate` | (unit-type-count-total mangonel-line < 4); (can-train mangonel-line) → train mangonel-line
- L326 `<= moderate` | (unit-type-count-total knight-line < 18); (can-train knight-line) → train knight-line
- L335 `== hard` | (unit-type-count-total scorpion-line < 6); (can-train scorpion-line) → train scorpion-line
- L352 `== hard` | (unit-type-count-total trebuchet-set < 6); (can-train trebuchet) → train trebuchet

### AP_Joan_6 p4 — Joan-scn6 player 4.ai

- L65 `== easy` |  → set-strategic-number sn-percent-attack-soldiers 70; set-strategic-number sn-number-explore-groups 1; enable-timer 1 1200
- L74 `<= moderate` |  → set-strategic-number sn-percent-attack-soldiers 80; set-strategic-number sn-number-explore-groups 1; enable-timer 1 300
- L93 `== easy` | (unit-type-count-total villager less-than 20); (can-train villager) → train villager
- L102 `<= moderate` | (unit-type-count-total villager less-than 45); (can-train villager) → train villager
- L240 `<= moderate` | (unit-type-count-total knight-line < 40); (can-train knight-line) → train knight-line
- L249 `<= moderate` | (unit-type-count-total trebuchet-set < 4); (can-train trebuchet) → train trebuchet
- L266 `<= moderate` | (unit-type-count-total scout-cavalry-line < 30); (can-train scout-cavalry-line) → train scout-cavalry-line

## Identical script bodies

- `95d4a9db`: AP_Attila_1_p1.per, AP_Attila_2_p1.per, AP_Attila_3_p0.per, AP_Attila_3_p1.per, AP_Attila_4_p1.per, AP_Attila_5_p1.per, AP_Attila_6_p1.per, AP_Genghis_1_p1.per, AP_Genghis_2_p1.per, AP_Genghis_3_p0.per, AP_Genghis_3_p1.per, AP_Genghis_4_p1.per, AP_Genghis_5_p0.per, AP_Genghis_5_p1.per, AP_Genghis_6_p1.per, AP_Joan_1_p1.per, AP_Joan_2_p1.per, AP_Joan_3_p1.per, AP_Joan_4_p0.per, AP_Joan_4_p1.per, AP_Joan_5_p1.per, AP_Joan_6_p1.per
- `02864859`: AP_Attila_1_p6.per, AP_Attila_1_p7.per, AP_Attila_1_p8.per, AP_Attila_3_p5.per, AP_Attila_3_p6.per, AP_Attila_3_p7.per, AP_Attila_3_p8.per, AP_Attila_4_p0.per, AP_Attila_4_p6.per, AP_Attila_4_p7.per, AP_Attila_4_p8.per, AP_Attila_5_p0.per, AP_Attila_5_p7.per, AP_Attila_5_p8.per, AP_Attila_6_p0.per, AP_Attila_6_p7.per, AP_Attila_6_p8.per, AP_Genghis_2_p0.per, AP_Genghis_6_p0.per
- `b984998c`: AP_Attila_2_p0.per, AP_Joan_5_p0.per, AP_Joan_6_p5.per
- `4385df60`: AP_Attila_5_p6.per, AP_Joan_4_p5.per, AP_Joan_5_p5.per
- `2d279a86`: AP_Genghis_1_p3.per, AP_Genghis_1_p4.per, AP_Genghis_1_p6.per, AP_Genghis_1_p8.per
- `036a6634`: AP_Genghis_4_p0.per, AP_Joan_6_p0.per
- `3ead5727`: AP_Genghis_6_p3.per, AP_Joan_1_p2.per, AP_Joan_1_p3.per, AP_Joan_1_p4.per, AP_Joan_1_p6.per, AP_Joan_2_p5.per, AP_Joan_2_p6.per
- `8b3d2e40`: AP_Joan_2_p0.per, AP_Joan_3_p0.per