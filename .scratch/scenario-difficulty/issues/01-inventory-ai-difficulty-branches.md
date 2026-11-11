# Inventory difficulty branches in embedded AIs

Type: task
Status: resolved
Blocked by:

## Question

What does every embedded AI script in the 18 AP scenarios do with `difficulty`? Produce a
per-script catalogue: scenario, player, AI name, each `difficulty` comparison (operator + level),
and what the guarded rules set (villager caps, building counts, army counts, resource thresholds,
attack timing). Flag the odd forms seen in a first pass (`== normal`, `== standard`, `< easy`,
`difficulty equal`, `>= moderate`) and any script that branches on difficulty some other way.
Also list which scripts carry no difficulty branch (pass-through candidates).

AFK. Link the catalogue as an asset; record headline counts in the answer.

## Answer

Catalogue: [`../assets/difficulty-inventory.md`](../assets/difficulty-inventory.md) (per-script table
plus every guarded rule as conditions → actions), machine-readable
[`../assets/difficulty-inventory.json`](../assets/difficulty-inventory.json), raw scripts in
[`../assets/ai-scripts/`](../assets/ai-scripts/) as `<scenario>_p<N>.per`. Regenerate with
[`../assets/tools/dump_ai.py`](../assets/tools/dump_ai.py) then
[`../assets/tools/analyze.py`](../assets/tools/analyze.py), run from the Archipelago root. `ai-scripts/` is gitignored because the scripts are proprietary game
content; if it is missing, run `dump_ai.py` to extract it before reading or analysing them.

**Level values.** Lower is harder: easiest 4, standard/easy 3, moderate 2, hard 1, hardest 0,
extreme -1 (`DifficultyLevel` in the vendored parser datasets; lobby "Standard" is AI `easy`). So
`<= moderate` means moderate *or harder*, and `< easy` means moderate or harder. The AoE2 knowledge
base has no AI-script entry for `difficulty`; that the `.per` fact uses the same scale is inferred
from the trigger enum, not sourced.

**Headline counts.** 127 embedded scripts; only 75 sit on a live AI slot (active, not P1, not GAIA).

| Group | Scripts | Difficulty use |
|---|---|---|
| Live, runtime `(difficulty …)` rules | 44 | 407 guarded rules |
| Live, compile-time `#load-if-defined DIFFICULTY-*` | 4 | Mongols-scn1.ai (Genghis 1 p3/4/6/8): Ornlu wolf range 2–7 and timer 8–3 across six levels, fallback 8/2 |
| Live, no branch of its own | 27 | 20 named campaign AIs (Attila 1 p2, Attila 2 p2/3/4/6/8, Attila 4 p5, Attila 6 p6, Genghis 1 p5/7, Genghis 3 p5/6, Joan 1 p5, Joan 2 p4, Joan 5 p2/3/4), Joan-noncombat ×6, scenario noncombat ×1, Fe Immobile ×3 |
| Inert (P1, GAIA or inactive slot) | 52 | PromiDE ×22 and Promisory ×7 gate only boar hunting via `#load-if-not-defined DIFFICULTY-EASIEST/EASY/MODERATE`; RandomGame ×19, _ajl ×2, Greg's Peaceful ×1 have none |

**Comparisons across the 407 rules:** `== easy` 119, `<= moderate` 117, `== hard` 80,
`== moderate` 63, `== normal` 17, `equal hard` 4, `<= hard` 2, `< easy` 2, `== standard` 1,
`>= moderate` 1, `< moderate` 1. Ten rules wrap the test in `not`, eight in `and`.

**Odd forms.**
- `== normal` (17; Attila 2 p7, Genghis 3 p4, Genghis 4 p2/p3/p4, Genghis 5 p2/p3/p4) and
  `== standard` (1; Attila 1 p3). Neither symbol is confirmed to exist in the AI language; if
  undefined the rule may never fire or the script may fail to load. Unresolved: ticket
  [Shared AI libraries and difficulty symbols](08-shared-ai-libraries.md).
- `equal hard` (Genghis 3 p3/p4): word-operator spelling of `==`, same meaning.
- `< easy`, `>= moderate`, `< moderate`, `<= hard` (Joan 2 p2/p7, Joan 4 p4, Genghis 2 p2/p3):
  valid; direction matters because lower is harder (`>= moderate` = moderate or easier).
- `sn-do-not-scale-for-difficulty-level 1` (Attila 4 p5, no branch otherwise): opts that AI out
  of the engine's own difficulty scaling.
- Compile-time `#load-if-defined DIFFICULTY-*` is a second branching mechanism the builder must
  resolve alongside runtime `(difficulty …)` facts.

**What guarded rules set** (top actions): `train villager` 60 (villager caps, e.g. 20 on easy vs 40
on moderate+), unit training caps per line (knight 36, militia 23, spearman 17, scorpion 16,
trebuchet 16, archer 14, mangonel 13, …), `build farm` 20 (farm caps 7 vs 13),
`sn-cap-civilian-builders` 34 and other civilian/attack percentages, timers 54/25 (attack cadence,
e.g. attack every 600 s on easy vs 300 s on moderate+), `attack-now` 14, and **`cc-add-resource`
39: periodic free resources scaled by difficulty** (e.g. 300 vs 600 of each per 600 s).

**Shared libraries.** 70 of the 75 live scripts `(load "scenario difficulty DE")` (one loads
`scenario difficulty`), a game-shipped file not available here. Its content may matter as much as
the embedded branches; graduated to [Shared AI libraries and difficulty symbols](08-shared-ai-libraries.md).

**Map correction.** The charting note's pass-through list holds: PromiDE, Promisory, RandomGame,
_ajl, Greg's Peaceful only sit on inert slots, and Joan-noncombat / Fe Immobile have no branch. Add
the 20 named campaign AIs above and Mongols-scn1.ai's compile-time branch to that picture.
