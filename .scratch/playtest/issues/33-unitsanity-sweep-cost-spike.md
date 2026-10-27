# 33: Spike: what do the caveman sweep and the unit checks cost per tick?

**Reported:** 2026-10-26, triage of [#10](10-caveman-sweep-delayed.md)

**Type:** spike

**Status:** ready-for-human

**Blocks:** #10, #34

## Question

How much of the sim tick do `ApplyCaveman` and `checkOwnedUnits` take at high population? Is either
cheap enough to run on every `UnitsanityChecks` tick (once a second)?

Both fixes for #10 rest on this, and nobody has measured it. The early returns in `UnitsanityChecks`
(`Unitsanity.xs:336-347`) are what keep the sweep rare today. The KB warns about exactly this: "A
cheap early `return` in a hot rule masks its true cost"
(`AoE2_AI_Modder/docs/agent/references/XS_MEASURED_BEHAVIOR.md`, *Choosing a poll rate*).

## What the code says (not measured)

- **`ApplyCaveman`** (`Caveman.xs:207`): for each owned unit, `originalTypeOf` scans the caveman
  ledger linearly (up to `CAVEMAN_LEDGER_CAPACITY`, 400). `removeDeadCavemen` walks the ledger once
  per sweep. At 200 pop and a full ledger, that is in the region of 80,000 comparisons.
- **`checkOwnedUnits`** (`Unitsanity.xs:200`): `findUnit` and `canonicalTypeOf` are O(1) array
  reads. #10's brief stopped there and called the function cheap, but it isn't O(1).
  - For every unit whose type has a unit row, `MarkRowOwned` reads `structGetInt(unit, "owned")`
    (`Unitsanity.xs:174`).
  - That read goes through `validateInstanceAttribute` → `findIndexString` (`structs.xs:586,123`),
    a linear string comparison over the Unit struct's attribute names.
  - `MAX_STRUCT_ATTRIBUTES` is 13 and `"owned"` is the 12th, so each read costs about 12 string
    comparisons. There are up to two reads per unit (the type and its canonical type), so a few
    thousand string comparisons per tick at 200 pop.
- **Closest measured evidence** (same KB file, *Per-tick scanning is affordable*):
  - Enumerating the owned-unit id set every tick was within noise.
  - 250 `xsGetObjectCountTotal` calls on every sim tick kept 94% of a 10-second baseline.
  - This suggests `checkOwnedUnits` is cheap, but it is a different workload and doesn't prove it.

## Method

Use the KB's tick-rate method: count rule firings over a 10-second baseline with nothing extra
running, then with the function under test running every tick, and report the retained percentage.

- Put the harness in a throwaway XS file that `.gitignore` covers, never in a live module. Delete it
  once the numbers are recorded.
- Use P1 at about 200 pop of units that have unit rows, under caveman mode, so `ApplyCaveman` does
  real work.
- `ApplyCaveman`: measure with the ledger empty, about 200, and full (400).
- `checkOwnedUnits`: measure at the same population, with rows both owned and not owned.
- Run each at the rule's real cadence (once a second) and at every sim tick, so there is headroom.

## Answer this spike must give

| Result | What #10 and #34 then do |
| --- | --- |
| `checkOwnedUnits` within noise | #34 can drop its gate: checks every tick when caveman is off |
| `ApplyCaveman` within noise even with a full ledger | #10 sweeps every tick. A one-for-one swap is then caught for free |
| `ApplyCaveman` measurable but bounded | #10 adds a seconds-based backstop, like `PROFESSION_SWEEP_SECONDS`, sized from the number |
| `ApplyCaveman` expensive | #10 first makes `originalTypeOf` O(1) (an id-indexed ledger). That is a design change, so it is re-triaged |

Record the numbers here under `## Answer`, then re-triage #10 and #34.
