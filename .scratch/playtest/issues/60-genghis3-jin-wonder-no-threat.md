# 60: The Jin Wonder in Genghis 3 is no threat, because custom victory turns it off

**Reported:** 2026-10-31, playtesting

**Status:** needs-triage

## Report

The Jin Wonder in Genghis 3 does not threaten the player. It is not a win condition.

## What the scenario does with it

The Jin (player 4) are the only ones who build a Wonder here, and no Wonder is placed on the map
at start. Exactly one trigger reacts to it, in **both** the vanilla scenario and the Ageipelago
one:

| trigger | |
| --- | --- |
| `t3 [D1] Jin talk smack` | **IF** player 4 owns 1 of unit **276 Wonder** |
| | **DO** `display_instructions` - a Jin taunt |

That is the whole of it. There is no countdown trigger, no defeat trigger and no AP location
tied to the Wonder, and vanilla has none either. So the AP conversion did not delete a threat
trigger; there was never one to delete.

## Where the threat came from, and where it went

In vanilla the threat is not a trigger at all - it is the **global victory mode**. Comparing
`GlobalVictory` between the stock `4_Genghis_3` (extracted from `cam4.aoe2campaign`) and the
Ageipelago scenario:

| field | vanilla | Ageipelago |
| --- | --- | --- |
| `mode` | **0** | **4** |
| `all_custom_conditions_required` | 0 | **1** |
| `explored_percent_of_map_required` | 0 | **100** |
| `conquest_required` | 0 | 0 |

Under vanilla's mode 0 the standard victory conditions are live, which is what makes a completed
enemy Wonder start a countdown. Ageipelago runs custom victory instead, so the scenario ends only
on its own `declare_victory`, and the standard Wonder condition never applies.

This is **deliberate and project-wide**, not a Genghis 3 slip. All 18 AP scenarios carry
`mode=4, all_custom=1, explored=100`, which matches the commit `aa5dcff "Cleans scenario
resources/victory cons"`. AP needs the scenario to end on `AP Victory`, so standard victory had
to go.

*Not engine-verified:* that mode 0 enables the Wonder countdown and mode 4 suppresses it is read
from the mode difference and the absence of any other mechanism, not from a run.

## The gap

Losing standard victory cost Genghis 3 its only Wonder threat, and nothing replaced it. The
project does model Wonders as objectives elsewhere, so the pattern exists:

| scenario | locations |
| --- | --- |
| Attila 3 | `ATT3_THREATEN_WONDER`, `ATT3_DESTROY_WONDER` |
| Attila 6 | five `Prevent or Destroy <colour>'s Wonder` locations |
| **Genghis 3** | **none** |

Genghis 3's eight locations are Victory, four Defeat-the-X, and three Find-the-X. The Jin Wonder
appears in none of them, and `Genghis3Rules` does not mention it.

## Options

1. **Accept it.** The Jin Wonder becomes flavour, and `[D1] Jin talk smack` is a taunt with
   nothing behind it. Nothing in logic needs changing, because nothing in logic references it.
2. **Restore the threat with custom triggers**, the way Attila 3 and 6 carry theirs: a timer
   started by the Jin owning a Wonder, ending in a defeat unless it is destroyed. That is a
   scenario change, and it would want a matching AP location and rule if the player is expected
   to deal with it.

Worth deciding alongside whether the other 17 scenarios lost anything to the same victory-mode
change - this ticket only checked the Wonder in Genghis 3.

## Comments
