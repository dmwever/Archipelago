# 83: Joan 6's difficulty siege is spawned capturable, so the AP items can be walked past

**Reported:** 2026-11-07, by the maintainer while playing `PT82_J6S` for
[#82](82-layer-3-in-game-checks.md)

**Status:** done

**Related:** [#31](31-ap-granted-units-start-as-gaia.md) (set every handed-over Gaia object to
Capture Flag Never), [#70](70-joan6-difficulty-siege-spawns-for-burgundy.md) (made these spawn as
Gaia in the first place), [#82](82-layer-3-in-game-checks.md) (the fork that surfaced it)

## Report

Joan 6's `Easy` and `Easy and Moderate` triggers each `create_object` extra siege for Gaia inside
the French Artillery and French Army grant areas. A `create_object` effect has no capture-flag
field, so those units get the engine default and can be taken by walking a unit up to them.

The French Artillery and French Army **items** are therefore not required for that siege on Easy
or Moderate: the player reaches the area, stands next to a Bombard Cannon, and owns it without
the item ever arriving.

## Established

**`create_object` cannot carry a capture flag.** Its whole field list is
`object_list_unit_id, source_player, location_x, location_y, facet, disable_sound`
(`AoE2ScenarioParser/datasets/effects.py:62`). `capture_flag` is a **unit** field, written per
placed object, and is 1.59-only (`objects/data_objects/unit.py:36`). There is no effect that sets
it at runtime and no object attribute that stands in for it - `HERO_STATUS`'s "Cannot be
Converted" is monk conversion, not Gaia proximity capture.

**The same scenario already does it the right way for its map-placed siege.** Reading
`AP_Joan_6.aoe2scenario` with the vendored parser, Gaia holds 4877 objects, and exactly **60**
carry `capture_flag = 0` (Never) - #31's "the army, the artillery and La Hire". Among them:

| ref | unit | tile | capture_flag |
| --- | --- | --- | --- |
| 8108 | Bombard Cannon | (104.5, 120.5) | 0 |
| 8110 | Bombard Cannon | (106.5, 120.5) | 0 |
| 8111 | Bombard Cannon | (105.5, 120.5) | 0 |
| 10542 | Packed Trebuchet | (137.5, 119.5) | 0 |

**The spawned ones sit in the same line.** `Easy` creates a Bombard Cannon at (108,120) and a
Packed Trebuchet at (136,125); `Easy and Moderate` creates Bombard Cannons at (107,120) and
(103,120) - all `source_player: 0`. So on Easy the artillery row at y=120 runs x=103, 104, 105,
106, 107, 108, where 104-106 cannot be captured and 103, 107, 108 can. One row, two rules.

**The kit cannot see this field.** `aoe2kit`'s `UnitStruct` decodes through `caption_string` and
stops; `capture_flag` is not in it. The reading above used the vendored `AoE2ScenarioParser`.
That is a gap in the kit, not in the file.

**Nothing can set a capture flag at run time.** The effect struct has 90 decoded fields
(`objects/data_objects/effect.py`) and none of them is capture-related; the kit's `EffectRecipe`
agrees. So the flag can only be written where it lives: on a unit placed in the **map**. The one
unproven lever is `MODIFY_ATTRIBUTE` on `HERO_STATUS`, whose flag 2 is "Cannot be Converted" -
that is monk conversion, and whether it also blocks Gaia proximity capture is not something the
files can answer.

**Only Joan 6 is affected.** `audit.py` here walks all eighteen AP scenarios, finds every
`create_object` with `source_player: 0`, and asks whether an `AP Give ...` `change_ownership`
from Gaia would otherwise have delivered that unit to that tile. Output in `audit.txt`:

| scenario | spawns | gated by | verdict |
| --- | --- | --- | --- |
| Attila 1 | 4 villagers at the camp | `HasAttila1AttilasCamp()` + objects_in_area | **clear** - the item already gates whether they exist at all, so capture delivers nothing extra |
| Joan 3 | 2 of unit 411 | difficulty | **clear** - no AP handover covers those tiles |
| Joan 6 | 3 Bombard Cannons, 1 Packed Trebuchet | difficulty | **in scope** - all four land inside `AP Give Artillery` / `AP Give Army` |
| Genghis 6 | 4 of unit 816 on the bridge | timer | **clear** - no AP handover covers those tiles |

4 of 14 Gaia `create_object` effects are in scope, and all four are Joan 6's. Attila 1 is the
instructive near-miss: its villagers are capturable too, but the spawn itself is behind the item,
so there is nothing to walk past.

## Rulings

- **2026-11-07** - No in-game confirmation needed; the capture flag is the defect.
- **2026-11-07** - The difficulty handling is correct and stays as it is. The `Easy` and
  `Easy and Moderate` triggers are not to be restructured. #70's difficulty check passes.
- **2026-11-07** - Fix shape: **place and remove**. The four go on the map at their final tiles
  as Gaia with Capture Flag Never, the `create_object` effects go, and two new triggers with
  inverted `difficulty_level` conditions take them away again where they do not belong.

## Candidate fixes

Every one of these has to get the four units onto the **map**, because that is the only place a
capture flag can be written. What differs is what the difficulty triggers then do with them, and
none of these changes a difficulty condition.

1. **Park and teleport.** Place the four on the map as Gaia with `capture_flag = 0`, out of the
   way, and change each `create_object` into a `teleport_object` that brings it to the tile it
   used to be created at. The triggers keep their shape, their condition and their effect count;
   only the effect type changes. Cost: on Hard and Hardest the four sit parked wherever they were
   put, as Gaia, instead of not existing.
2. **Place and remove.** Place the four at their final tiles as Gaia with `capture_flag = 0` and
   drop the `create_object` effects, then remove them again on the difficulties that should not
   have them. This needs a new trigger with an inverted `difficulty_level` condition - the
   condition type supports `inverted`, and Joan 6 already carries one - but it does add trigger
   structure around difficulty, which the ruling above warns off.
3. **Modify the attribute and hope.** Keep `create_object` and add a `MODIFY_ATTRIBUTE` setting
   `HERO_STATUS` to 2 on the created units. Unproven: flag 2 is documented as monk conversion,
   and whether it stops Gaia proximity capture cannot be settled from the files.

Option 1 is the smallest change that satisfies #31's contract - *"Every object below is owned by
Gaia on the map, with Capture Flag Never (0) ... handed over by their scenario item"* - without
touching difficulty.

## Acceptance criteria

- [x] The in-game confirmation. Waived, then done anyway: played on Easy, Moderate
      and Hard, 2026-11-07.
- [x] Every `create_object` with `source_player: 0` across the eighteen AP scenarios is listed,
      with whether an `AP Give ...` effect also hands that unit over. `audit.py` / `audit.txt`
      in [`spikes/83/`](../spikes/83/); 4 of 14, all Joan 6's.
- [x] A ruling on which candidate fix applies, recorded under *Rulings*. **Place and remove.**
- [x] Joan 6 is rewritten by a one-off script in `.scratch/playtest/spikes/83/`, written beside
      the original for the maintainer to check in the editor and swap in, the way #31 did it.
      `fix.py` writes `AP_Joan_6.fixed.aoe2scenario`; it refuses to overwrite the original.
- [x] The four rewritten units read back with `capture_flag = 0`, taking the scenario's Never
      count from 60 to 64. `verify.py`: 14 of 14.
- [x] The rewrite behaves in game on Easy, Moderate and Hard.
- [x] `AP_Joan_6.fixed.aoe2scenario` is swapped in over `AP_Joan_6.aoe2scenario`, committed in
      Ageipelago `a187fd7`.

## Comments

### The rewrite is built (2026-11-07)

[`spikes/83/`](../spikes/83/README.md) - `audit.py` (scope), `fix.py` (the rewrite),
`verify.py` (the proof), `audit.txt`, `README.md`.

`fix.py` writes `AP_Joan_6.fixed.aoe2scenario` beside the original and refuses to overwrite it.
It places the four at their final tiles as Gaia with `capture_flag = 0`, copying rotation, status
and animation frame from the map-placed sibling of the same type (refs 8108 and 10542); drops the
four `create_object` effects; and adds `Not Easy` and `Not Easy or Moderate`, each one inverted
`difficulty_level` condition and one `remove_object` on the reference ids that replaced that
trigger's creates.

**Inverting the same quantity the original trigger uses** is what makes this safe. `Easy` tests
quantity 3 and `Easy and Moderate` tests quantity 2; whichever way the engine compares those,
`inverted = 1` on the same value is the exact complement, so nothing here has to decide whether
the test means "equal to" or "this difficulty or easier".

`verify.py`: **14 of 14.** Never count 60 to 64, each piece at its tile with flag 0, neither
difficulty trigger creating for Gaia any more, each remover carrying the right inverted condition
and exactly the right reference ids, no existing trigger moved, every existing unit reference id
surviving, and the colour mood unchanged.

Cross-checked with `kit scen diff`, an independent reader: four Gaia units added, two triggers
added, `Easy` 6 effects to 4, `Easy and Moderate` 5 to 3, plus the bookkeeping that follows
(`next_unit_id_to_place` 58827 to 58831, unknown-field rows of added and removed children).
Nothing else in the file moved.

**One parser artefact caught and suppressed.** `AoE2ScenarioParser` turns `map_color_mood` into a
`ColorMood` enum on read and writes back `.name.lower()`, so `Default` becomes `default` on any
round trip through it - a change nobody asked for, in a file nobody else touched. `fix.py` now
reads the shipped literal with the kit and puts it back, and `verify.py` asserts it. Worth
knowing for any future parser rewrite of these scenarios, #31's included.

**Still `structure_verified`, not `engine_verified`.** Nobody has watched a Bombard Cannon refuse
capture, and nobody has started Joan 6 on Hard to watch the removers fire. The in-game
confirmation was waived; that waiver is what this rests on. What is left is the editor check and
the swap.

### It works in game (2026-11-07)

Played on Easy, Moderate and Hard. The siege appears where it should and nowhere it should not,
so the inverted `difficulty_level` removers are right in both directions. That is the
`engine_verified` the structural work could not reach.

### Why the rewrite is 4 KB smaller, and why that is nothing (2026-11-07)

Worth recording because it will come up on every parser rewrite of these scenarios, #31's
included.

| | original | rewritten | delta |
| --- | --- | --- | --- |
| on disk | 74,581 | 70,500 | **-4,081** |
| inflated body | 496,615 | 496,507 | **-108** |

The content moved by 108 bytes, which is exactly the four effects out against the two triggers
and four units in. The rest is the deflate encoder. Re-compressing both inflated bodies with one
encoder at level 9 gives 70,322 for the original body and 70,419 for the rewritten one - DE's
editor spent 74,500 bytes on a body zlib level 9 fits into 70,322, and the rewritten body is
actually **97 bytes harder** to compress than the original. The file is smaller despite its
content, not because of it.

`AoE2ScenarioParser` deflates with `zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)`. Compare
`inflated_bytes` from `kit scen glossary`, never the file size; aoe2kit's writer docs say the
same.

### Closed (2026-11-07)

The maintainer swapped the rewrite in and committed it as Ageipelago `a187fd7`,
*"Att 6 fix bonus troops, Att 3 give gold from p2"* (the Joan 6 file is the "bonus troops" half
of that message). `AP_Joan_6.aoe2scenario` is now 70,500 bytes and carries `Not Easy` and
`Not Easy or Moderate`. Played on Easy, Moderate and Hard; the siege appears where it should and
nowhere it should not. Every box ticked.
