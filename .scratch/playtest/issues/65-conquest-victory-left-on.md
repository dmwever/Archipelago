# 65: Conquest victory is still on in seven scenarios, so Genghis 4 ends the moment Khwarazm falls

**Reported:** 2026-10-31, playtesting

**Status:** needs-triage

**Related:** [#60](60-genghis3-jin-wonder-no-threat.md) (the same victory-mode conversion, seen
from the other side)

## Report

Genghis 4 grants instant victory on defeating Khwarazm, before the AP objectives are done.

## Measured

`GlobalVictory` for Genghis 4:

| field | vanilla `4_Genghis_4` | Ageipelago |
| --- | --- | --- |
| `conquest_required` | **1** | **1** |
| `mode` | **1** (Conquest) | **4** (custom) |
| `all_custom_conditions_required` | 0 | **1** |
| `explored_percent_of_map_required` | 0 | 100 |

Vanilla Genghis 4 is a conquest scenario, and the conversion to custom victory **kept
`conquest_required = 1`**. Genghis 4 has three enemies - Kipchaks (P1), Russians (P2) and
Khwarazm (P3) - and Khwarazm is the last of them, so the moment they fall conquest is satisfied
and the scenario ends.

## The conversion was not applied evenly

`conquest_required` was cleared in some scenarios and left in others:

| | |
| --- | --- |
| **cleared** | Attila 1 and Attila 2 - vanilla `conq=1 mode=0`, Ageipelago `conq=0` |
| **left on** | **Attila 6, Genghis 1, Genghis 4, Genghis 6, Joan 1, Joan 5, Joan 6** |
| off in both | Attila 2-5, Genghis 2, 3, 5, Joan 2, 3, 4 |

So seven of eighteen still end on conquest. Genghis 4 is the one that was played; the other six
deserve the same look, since any of them can cut a run short the same way.

AP wants the scenario to end on its own `AP Victory`, which is what `mode=4` and
`all_custom_conditions_required=1` are for. A live `conquest_required` sits underneath that and
fires first.

## A loose end

With `all_custom_conditions_required = 1` and `explored_percent_of_map_required = 100`, a strict
reading says victory needs conquest **and** a fully explored map, which would not fire instantly.
The reported behaviour says otherwise, so either `explored_percent` is not enforced under mode 4
or conquest short-circuits it. The in-game result is the ground truth here; the field semantics
are not established, and that is worth settling before deciding the fix, because it also decides
whether `explored_percent_of_map_required = 100` is doing anything at all in any of the eighteen.

## The likely fix

Set `conquest_required = 0` on the seven. aoe2kit writes this directly - the recipe `victory`
block takes `conquest_required` - so it needs no editor pass:

```json
{ "victory": { "conquest_required": 0 } }
```

Worth confirming first that no scenario relies on conquest as its intended ending, and that the
AP victory path is reachable in each of the seven.

## Comments
