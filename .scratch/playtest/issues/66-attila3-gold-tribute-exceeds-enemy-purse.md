# 66: Attila 3's gold items tribute 3000 from enemies who hold 500 and 600

**Reported:** 2026-11-02, playtesting

**Status:** needs-triage

## Report

Did not receive Attila 3 Green Gold.

## The delivery chain

`AP_ATTILA_3_GREEN_GOLD` (1006) sets `Attila3GreenGold()`. The scenario acts on it in **t48
`AP Give Green TC Gold`**:

| kind | detail |
| --- | --- |
| condition | `destroy_object` **2705** |
| condition | `script_call HasAttila3GreenGold();` |
| effect | `tribute` **quantity 3000, resource 3 (gold), source_player 3, target_player 1** |

Object 2705 is unit **109 `RTWC`** - a Town Center - owned by player 3 at (133,22). So the gold
arrives only after Green's Town Center is destroyed, which is by design and matches the
location `ATT3_GREEN_TC`.

The Red equivalent is **t49**, same shape: `destroy_object 852`, `HasAttila3RedGold()`, tribute
3000 gold from player 2.

## The likely cause

The tribute takes the gold **from the enemy**, and neither enemy has it. Starting gold, read
from the scenario:

| player | tribe | starting gold | tribute asks |
| --- | --- | --- | --- |
| P0 | Attila (the player) | 0 | - |
| P1 | Constantinople | 50000 | - |
| **P2** | **Marcianopolis (Red)** | **600** | **3000** |
| **P3** | **Philippopolis (Green)** | **500** | **3000** |
| P8 | - | 10000 | - |

Green starts with 500 against a 3000 tribute; Red with 600. An AI accumulates over time, so the
purse at the moment the Town Center falls is not necessarily the starting figure - but it is not
reliably 3000 either, and by the time a player has destroyed the Town Center that economy has
usually been wrecked.

*Not engine-verified:* exactly what AoE2 does when a tribute exceeds the source player's
balance - transfer nothing, transfer what is there, or transfer the full amount regardless. The
report says nothing was received, which is consistent with the first two and not the third. This
is the thing to settle first, because it decides whether the fix is a quantity change or
something else entirely.

## Options

1. **Lower the quantity** to something both enemies can cover.
2. **Tribute from a player who has it** - P1 Constantinople holds 50000 - though that changes
   the fiction of taking the defeated town's treasury.
3. **Give the gold rather than move it**, if a grant effect exists that does not debit a source.

## Also noticed

`t49`, the Red Gold grant, is named **"Trigger 49"**. Its sibling is `AP Give Green TC Gold`.
Cosmetic, but it is the kind of thing that makes the next person think the trigger is unrelated
scaffolding.

## Comments
