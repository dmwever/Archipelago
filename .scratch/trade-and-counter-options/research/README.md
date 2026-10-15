# Research: markets, docks, diplomacy and AI scripts (2026-10-15)

Raw material behind the spec's player records. Read-only scans; nothing here is imported or tested.
Copied from a design session's scratchpad so later sessions (ticket 11 in particular) need not rescan.

## Contents

- `grill-decisions.md`: the design session's running decision log (Q1-Q33). The spec is the
  authority; this is the raw trail, including every per-scenario ruling.
- `out.json`: per scenario, per player slot: name, colour, stance toward P1 (both directions),
  market count (unit 84), dock count (unit 45). `scripts/show.py` pretty-prints it.
- `out2.txt`, `out3.txt`: trigger scans (enabled and disabled): Change Diplomacy, Change Ownership of
  markets/docks, and which triggers activate which.
- `per/`: every AI script embedded in the scenarios, one per player, `b_` = read from the
  `.aoe2campaign` bundle (Attila, Joan), `l_` = read from the loose `.aoe2scenario` (Genghis).
- `scripts/`: the scan scripts. They hardcode this worktree's `worlds/age2de` path for the vendored
  AoE2ScenarioParser.

## Sources

- Attila and Joan: the Ageipelago `.aoe2campaign` bundles (bundles are newer than loose scenarios);
  loose scenarios on `0.3.0` matched them for players, diplomacy, markets, docks and triggers.
- Genghis: loose `AP_Genghis_1..6.aoe2scenario` only; no bundle exists.
- Saladin, Barbarossa, El Cid, Montezuma: no scenario files on this machine, so not scanned.

## Findings that matter for ticket 11

- **"AI builds one"**: almost every AI script has `(building-type-count-total market < 1)
  (can-build market) => (build market)`. Grep `per/` for `build market` / `build dock`.
  Players whose AI never builds either: all of Attila 6; Joan 1 and Joan 5 (stub AIs); Genghis 2 P4;
  Genghis 4 P2; Genghis 5 P3. Genghis 1 has the rule but no villagers, so it never fires.
- AI scripts that build docks: Attila 1 P4, Joan 3 P3, Joan 4 P2 and P3 (only if AI goal 2 = 1),
  Joan 6 P2 and P3, Genghis 3 P4.
- Joan 2: trigger "AP Setup" gives Burgundy's market and dock to Gaia at t=0.
- No trigger anywhere creates or replaces a market or dock; triggers only change ownership.
- **Gap:** every AI loads vanilla include files ("scenario market", "scenario difficulty DE",
  "scenario upgrades DE", "scenario resign") that are not on this machine, so anything they do
  (likely trading in "scenario market") is unverified.

## Reminder

PR 19's market and dock flags record judged **usability**, not building existence. The scan
disagreed with them in 10 of 16 scenarios; the flags, as corrected by the rulings in the spec, win.
Never "correct" a flag from this data. Use it only to find which player owns or builds a building.
