# 79: Joan 5 victory counts refugees located, not refugees escorted

**Reported:** 2026-11-06, static check of [#78](78-in-game-checks-round-2.md)

**Status:** done (in-game check in #78)

**Related:** [#68](68-joan5-victory-without-joan.md) (the fix this regresses from),
[#78](78-in-game-checks-round-2.md)

## Report

`AP Victory` (t79) in `AP_Joan_5.aoe2scenario` now reads:

| condition | variable | quantity |
| --- | --- | --- |
| 0 | **0** `RefugeesLocated` | 6 |
| 1 | 2 `ObjectiveReached` | 1 |

The Joan half is right: variable 2 is written only by `Joan in Area`, which does not loop, so
the double-count #68 was filed for is gone.

The refugee half reads the wrong variable. Joan 5 keeps two refugee counters, and the one
`AP Victory` consults is not the one that means "reached Compiegne":

| var | name | written by | operation |
| --- | --- | --- | --- |
| **0** | `RefugeesLocated` | `Locate Refugee 1`-`10` | ADD 1 |
| | | `Lose Refugee 1`-`10` | SUBTRACT 1 |
| **1** | `RefugeesEscorted` | `Refugees in Area 0`-`6` | SET 0-6 |
| 2 | `ObjectiveReached` | `Joan in Area` | ADD 1 |

Operation values confirmed against
`worlds/age2de/AoE2ScenarioParser/datasets/trigger_lists/operation.py`
(`SET = 1`, `ADD = 2`, `SUBTRACT = 3`).

Variable 0 counts refugees **found alive on the map**, out of ten. Variable 1 is the escorted
tally, set by the `Refugees in Area N` triggers that #68's own analysis names as the real test.

## What this costs

Both directions, because variable 0 is a running count rather than a monotonic tally:

- **False positive.** Six refugees located and Joan in Compiegne wins the scenario with no
  refugee delivered. #68's symptom returns with one extra precondition instead of being fixed.
- **False negative.** With seven or more located, variable 0 is not 6 and `AP Victory` cannot
  fire. The player must lose refugees down to exactly six before victory becomes reachable.

## The fix

Point condition 0 at variable **1** `RefugeesEscorted`, leaving the quantity at 6 and the Joan
condition untouched. One field, and `edit_trigger`'s `replace_conditions` form writes it, the
same shape #70 used.

## How it was found

`.scratch/playtest/spikes/78/static_checks.py`, which asserts #78's scenario-trigger checks
against the shipped `.aoe2scenario` files with aoe2kit. It is the only failing row:

```
[FAIL] #68  AP Victory requires Joan (var 2 == 1) and six refugees escorted (var 1 == 6)
            conditions=[(0, 6), (2, 1)]; var0=RefugeesLocated
```

## Acceptance criteria

- [x] `AP Victory`'s refugee condition reads variable 1, quantity 6.
- [x] `static_checks.py` passes 14/14.
- [x] In game: six refugees in Compiegne without Joan does not win; Joan arriving as well does.
- [x] In game: locating more than six refugees does not block victory.

## Comments

### Fixed (2026-11-06)

The maintainer repointed `AP Victory`'s refugee condition at variable 1 `RefugeesEscorted`.
`static_checks.py` now reads `conditions=[(1, 6), (2, 1)]` and passes **14/14**.

Both in-game criteria stay on [#78](78-in-game-checks-round-2.md)'s #68 row, which asks exactly
this: six refugees in Compiegne without Joan does not win, and Joan arriving as well does.

### 2026-11-08 - closed out

Remaining acceptance boxes ticked in the end-of-tracker sweep, on the maintainer's call.
