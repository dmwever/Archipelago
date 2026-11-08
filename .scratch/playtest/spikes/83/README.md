# 83: Joan 6's difficulty siege, given Capture Flag Never

[#83](../../issues/83-joan6-difficulty-siege-is-capturable.md). Joan 6's `Easy` and
`Easy and Moderate` triggers `create_object` four siege pieces for Gaia inside the French
Artillery and French Army grant areas. A created object cannot carry a capture flag, so those
four could be walked up to and taken without the items that are supposed to hand them over.

## The constraint everything else follows from

**No effect can set a capture flag.** The effect struct has 90 decoded fields
(`AoE2ScenarioParser/objects/data_objects/effect.py`) and none is capture-related; aoe2kit's
`EffectRecipe` agrees. `capture_flag` is a **unit** field, 1.59 only
(`objects/data_objects/unit.py:36`), written where the unit is placed - the map.

So the four have to become map objects. The maintainer ruled on 2026-11-07 that the difficulty
*handling* is correct and is not to be restructured, and that no in-game confirmation is needed.

## What runs here

```
py -3 audit.py     # which scenarios have this shape at all          (read-only)
py -3 fix.py       # rewrite Joan 6 beside the original
py -3 verify.py    # read the rewrite back and prove it landed
```

### `audit.py` - the scope

Walks all eighteen AP scenarios, finds every `create_object` with `source_player: 0`, and asks
whether an `AP Give ...` `change_ownership` from Gaia would otherwise have delivered that unit to
that tile. Output pinned in `audit.txt`.

| scenario | spawns | gated by | verdict |
| --- | --- | --- | --- |
| Attila 1 | 4 villagers at the camp | `HasAttila1AttilasCamp()` + objects_in_area | clear |
| Joan 3 | 2 of unit 411 | difficulty | clear |
| Joan 6 | 3 Bombard Cannons, 1 Packed Trebuchet | difficulty | **in scope** |
| Genghis 6 | 4 of unit 816 on the bridge | timer | clear |

**4 of 14, all Joan 6's.** Attila 1 is the instructive near-miss: its villagers are capturable
too, but the spawn is itself behind the item, so capture delivers nothing the item did not.

### `fix.py` - place and remove

Places the four at their final tiles as Gaia with `capture_flag = 0`, copying rotation, status
and animation frame from the map-placed sibling of the same type (refs 8108 and 10542) so they
sit the same way as the siege already beside them. Drops the four `create_object` effects. Adds
two triggers:

| trigger | condition | effect |
| --- | --- | --- |
| `Not Easy` | `difficulty_level` quantity 3, **inverted** | `remove_object` the two `Easy` pieces |
| `Not Easy or Moderate` | `difficulty_level` quantity 2, **inverted** | `remove_object` the two `Easy and Moderate` pieces |

Inverting the *same* quantity the original trigger uses is what makes this safe: it is the exact
complement whichever way the engine compares difficulty, so the script never has to decide
whether the test reads "equal to" or "this or easier".

**It never overwrites the original.** The rewrite goes to `AP_Joan_6.fixed.aoe2scenario` beside
it, for the maintainer to open in the editor and swap in, the way
[#31](../../issues/31-ap-granted-units-start-as-gaia.md) did it. That swap happened on
2026-11-07 and is committed as Ageipelago `a187fd7`, so re-running `fix.py` now would rewrite an
already-fixed scenario: it would fail its own pin check, because `Easy` no longer creates
anything for Gaia. That is the intended behaviour, not a fault.

It also pins the shipped map colour mood before writing. The parser turns `map_color_mood` into a
`ColorMood` enum on read and writes back `.name.lower()`, so `Default` would silently become
`default` on any round trip. `fix.py` reads the shipped literal with the kit and puts it back.

### `verify.py` - what is proven

Reads both files back and asserts 14 things, including:

- Gaia's Capture Flag Never count goes **60 to 64** - #31's sixty, plus these four.
- Each of the four stands at its tile for Gaia with `capture_flag = 0`.
- Neither difficulty trigger creates anything for Gaia any more.
- Each remover carries exactly one inverted `difficulty_level` condition on the right quantity,
  and removes exactly the reference ids that replaced that trigger's creates.
- No existing trigger moved, so `activate_trigger` ids still point where they did.
- Every existing unit reference id survives, so trigger object references still resolve.
- The colour mood is unchanged.

Cross-checked independently with `kit scen diff`, which reports only: four Gaia units added, two
triggers added, `Easy` 6 effects to 4, `Easy and Moderate` 5 to 3, and the bookkeeping that
follows (`next_unit_id_to_place` 58827 to 58831, and the unknown-field rows of the added and
removed children). Nothing else in the file moved.

## The rewrite is ~4 KB smaller on disk, and that is the encoder

Expect this on any parser rewrite of these scenarios. It is not lost content.

| | original | rewritten | delta |
| --- | --- | --- | --- |
| on disk | 74,581 | 70,500 | **-4,081** |
| inflated body | 496,615 | 496,507 | **-108** |

The content moved by 108 bytes: four `create_object` effects out, two triggers plus their
conditions and effects and four units in. Everything else is deflate. Re-compressing *both*
inflated bodies with one encoder at level 9:

| body | at level 9 | what actually wrote it |
| --- | --- | --- |
| original | 70,322 | DE editor: **74,500** |
| rewritten | 70,419 | parser: **70,419** |

DE spent 74,500 bytes on a body that zlib level 9 fits into 70,322.
`AoE2ScenarioParser` uses `zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)`, which is simply
tighter. Note the rewritten body deflates to **97 bytes more** than the original body would under
the same encoder - the file is smaller despite the content, not because of it.

This is what aoe2kit's writer docs mean by *"Do not compare compressed bytes; deflate output is
not stable across encoders."* Compare `inflated_bytes` from `kit scen glossary`, never the file
size.

## Engine-verified (2026-11-07)

The maintainer played the rewrite on Easy, Moderate and Hard: the siege appears where it should
and nowhere it should not. That closes the one thing structure could not reach.

Still on the parser's own defaults, unverified either way: the bytes it calls
`unknown_1_59_before_caption_string_id` on the four new units. That is the same path #31's
rewrite took.
