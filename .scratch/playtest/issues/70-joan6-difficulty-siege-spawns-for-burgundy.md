# 70: Joan 6's easy-difficulty siege spawns for Burgundy instead of Gaia

**Reported:** 2026-11-02, playtesting

**Status:** ready-for-agent

**Related:** [#31](31-ap-granted-units-start-as-gaia.md)

## Report

Joan 6: 3 purple Bombard Cannons and one purple Trebuchet at the French Army and French
Artillery. Suspected a leftover from the conversion to Gaia units.

Confirmed, and the conversion moved them the opposite way from what the name suggests - these
were **Gaia in vanilla and are now Burgundy's**.

## Vanilla against Ageipelago

Two difficulty triggers create siege at the French camp. Same units, same tiles, different owner:

| trigger | unit | tile | vanilla owner | Ageipelago owner |
| --- | --- | --- | --- | --- |
| `Easy` | Bombard Cannon (36) | (108,120) | **0 Gaia** | **2 Burgundy** |
| `Easy` | Packed Trebuchet (331) | (136,125) | **0 Gaia** | **2 Burgundy** |
| `Easy and Moderate` | Bombard Cannon (36) | (107,120) | **0 Gaia** | **2 Burgundy** |
| `Easy and Moderate` | Bombard Cannon (36) | (103,120) | **0 Gaia** | **2 Burgundy** |

Vanilla trigger ids are 19 and 35; in `AP_Joan_6.aoe2scenario` they are **t18 `Easy`** and
**t34 `Easy and Moderate`**, both enabled.

Trigger player numbering here is 0 Gaia, 1 Army of France (the human), 2 Burgundy, 3 English,
4 Shrewsbury - confirmed by `AP Give Army`, which is `source_player 0 target_player 1`. Burgundy
carries colour 5, which is purple, so these are the four units reported.

## Why it matters

In vanilla this is a **difficulty bonus for the player**: on Easy and Moderate the scenario
quietly places extra siege as Gaia at the French camp, inside the areas the French Army and
French Artillery occupy, to be handed over with them. The tiles sit inside both AP grant boxes:

| grant | area | the spawns inside it |
| --- | --- | --- |
| `AP Give Artillery` | (99,114)-(113,123) | 3 Bombard Cannons at x 103, 107, 108, y 120 |
| `AP Give Army` | (126,114)-(143,129) | 1 Packed Trebuchet at (136,125) |

Owned by Burgundy they are the exact opposite: **enemy siege spawning inside the player's own
reinforcement camp**, on the easier difficulties, where the bonus was meant to help. And because
both AP grants are `source_player 0`, they will never be picked up - they stay purple and
hostile no matter what items arrive.

## The fix

Set `source_player` back to **0** on those four `create_object` effects in t18 and t34.

aoe2kit writes this with an `edit_trigger` recipe, so no editor pass is needed - hence
`ready-for-agent`. The `replace_effects` form is the one to use, since the effects already exist
and only one field changes.

## Worth sweeping

This is a `create_object` whose `source_player` moved from 0 to 2 between vanilla and here. The
same slip could sit in any other scenario touched by the same pass. A diff of every
`create_object` effect's `source_player`, vanilla against Ageipelago, across all 18 would find
the rest at the desk - AoE2ScenarioParser reads both sides, which aoe2kit cannot do for the
vanilla files.

## Comments
