# 61: Attila 6's "P5 has a wonder" watcher tests player 4, so Purple's Wonders are unwatched

**Reported:** 2026-10-31, found while checking [#60](60-genghis3-jin-wonder-no-threat.md)

**Status:** wontfix

## Report

Checked on the steer that Attila 6 probably shares Genghis 3's Wonder gap. It does not share
that one - Attila 6 implements its Wonder threat in triggers rather than leaning on the global
victory mode, so the custom-victory change did not disarm it. It has a different defect.

## Attila 6's Wonder machinery

Wonders are not placed on the map. Five triggers build them at runtime with `place_foundation`:

| trigger | enabled | builds for |
| --- | --- | --- |
| t1 `Purple Constructs Wonder (time)` | yes | **player 5** at (123,72) |
| t2 `Red Constructs Wonder` | yes | player 2 at (216,24) |
| t3 `Green Constructs Wonder (time)` | no | player 3 at (33,55) |
| t4 `Orange Constructs Wonder` | yes | player 4 at (136,178) |
| t5 `Purple Constructs Wonder 2` | yes | **player 5** at (129,78) |

So Red is 2, Green is 3, Orange is 4, **Purple is 5**.

Four watchers then deactivate `t33` when an enemy owns a Wonder:

| trigger | name | tests player |
| --- | --- | --- |
| t29 | `P2 has a wonder` | 2 |
| t30 | `P3 has a wonder` | 3 |
| t31 | `P4 has a wonder` | 4 |
| **t32** | **`P5 has a wonder`** | **4** |

## Defect 1: t32 tests the wrong player

`t32` is named for player 5 and tests player 4, which t31 already covers. **Purple is player 5
and builds two of the five Wonders** (t1 and t5), so neither is ever noticed by this watcher.

## Defect 2: t33 is never re-armed

Searching every activate/deactivate effect that targets trigger 33:

```
deactivate by t29  P2 has a wonder
deactivate by t30  P3 has a wonder
deactivate by t31  P4 has a wonder
deactivate by t32  P5 has a wonder
```

Four deactivations, **zero activations**. Nothing turns t33 back on, so destroying the Wonder
does not undo the block. Once Red, Green or Orange completes one, t33 is off for the rest of the
scenario.

## What t33 is, and what is not known

t33 is unnamed and carries four `PLAYER_DEFEATED` conditions for players 2, 3, 4 and 5 - the
same four as `t34 [O] Defeat Italians` and `t35 AP Defeat the Italians` - and a single effect of
**type 91**.

**Effect 91 cannot be named.** aoe2kit's table ends at 90 (`create_decision`) and
AoE2ScenarioParser's dataset ends at 90 as well. Given the matching conditions it is plausibly
the victory declaration, but that is an inference, not a reading, and the severity of defect 2
rests on it.

## The AP side is not affected

`t34` and `t35` are never deactivated - no activate or deactivate effect targets either. So the
AP location `AP Defeat the Italians` and the objective display both survive an enemy Wonder.
Whatever t33 does, it is not the AP check.

The five AP Wonder locations are sound too. Each `AP Destroy <colour> Wonder` trigger starts
disabled and is activated by its matching constructor, and tests that the player owns no Wonder
and that none stands in the Wonder's area:

| AP trigger | activated by |
| --- | --- |
| t42 `AP Destroy Purple Wonder` | t1 |
| t43 `AP Destroy Green Wonder` | t3, t20, t21 |
| t44 `AP Destroy Red Wonder` | t2 |
| t45 `AP Destroy Orange Wonder` | t4 |
| t46 `AP Destroy Purple Wonder 2` | t5 |

## What this needs

1. Point `t32` at player 5.
2. Decide whether t33 should be re-armed when the Wonder falls, which first needs effect 91
   identified. Opening the scenario in the DE editor names it in one look.

Both are scenario edits. Neither touches logic: no rule references the Wonder watchers, and the
five AP Wonder locations already work.

## Comments

### Closed (2026-11-04)

Wontfix by the maintainer. Found during #60's audit, not seen in play, and no AP location depends on t32 or t33.
