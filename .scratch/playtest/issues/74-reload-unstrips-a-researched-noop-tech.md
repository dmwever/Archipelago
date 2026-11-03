# 74: Reloading un-strips any tech researched as a noop, granting its real effect free

**Reported:** 2026-11-03, playtesting

**Status:** needs-triage

**Related:** [#67](67-demolition-raft-upgrade.md) (the noop strip),
[#06](06-reload-misses-scenario-items.md) (the other reload gap)

## Report

In Joan 4, Skirmishers were spawning as Elite Skirmishers without the technology researched,
after a load.

## The ordering that does it

`InitTechsanity()` runs on every scenario start, including a load:

```xs
reconstructStartingState(apVanillaAge);

for (j = 0; < techCount) {
    vector tech = getTech(j);
    if (structGetBool(tech, "isLocation") && civCanResearch(tech)
     && structGetBool(tech, "researched") == false) {
        initTech(tech);
    }
}
```

and `initTech` reads the **live** tech state:

```xs
int state = xsGetTechState(id, 1);
if (state == cTechStateInvalid) {
    return;
}
if (state == cTechStateDone) {
    structSetBool(tech, "researched", true);
    structSetBool(tech, "effectDone", true);
    return;                      // <-- no stripTech, no AddLocation
}
stripTech(tech);
AddLocation(structGetInt(tech, "itemId"));
```

**A tech that reads Done when techsanity initialises is never stripped.** Its real effect stays
live for the rest of the session, and it is marked `effectDone` so nothing later touches it.

## Why a reload changes the answer

Stripping does not disable a tech - it swaps the effect for a noop
(see [#67](67-demolition-raft-upgrade.md)):

```xs
void stripTech(vector tech) {
    xsEffectAmount(cModifyTech, structGetInt(tech, "id"), cAttrSetEffect, 1.0 * NOOP_EFFECT, 1);
}
```

So the research button stays on the building, still costs its resources, and completes normally -
it just does nothing. That leaves the engine's tech state at **Done**.

Put the two together:

1. Fresh start. Elite Skirmisher is not Done, so `initTech` strips it to a noop and registers
   its location.
2. The player researches it at the Archery Range. It costs food and gold, finishes, and visibly
   does nothing. Tech state is now **Done**.
3. Save and load.
4. `InitTechsanity` runs again. `initTech` now sees **Done**, sets `researched` and `effectDone`,
   and **returns without stripping**.
5. The tech's real effect is live. Skirmishers upgrade to Elite, with no AP item ever received.

## Not specific to Joan 4 or to Skirmishers

Nothing in the path mentions either. Any tech that is both strippable and researchable before the
item arrives takes the same route, so this is a general "research the noop, reload, keep the
effect" exploit. Joan 4 and Elite Skirmisher are simply where it surfaced - Elite Skirmisher is
a Castle-age tech and Joan 4 opens in Castle, so it is available from the first minute and costs
little.

## A second effect in the same branch

`AddLocation(...)` sits only in the strip branch, so a tech that is Done at init gets **no
location registered** for that session. For a tech genuinely researched before the save that may
be harmless, but it is the same `if` deciding two unrelated things and is worth separating.

## What to check before fixing

Whether the engine restores a scenario's tech states on load from the save, or re-derives them
from the scenario file. The chain above assumes the former. A probe writing
`xsGetTechState(3652, 1)` at the top of `InitTechsanity` on a fresh start and again after a
reload settles it in one pair of runs.

The fix shape, once confirmed: `initTech` should decide whether to strip from AP state - does
the player hold the item - rather than from the live engine state, which a reload makes
untrustworthy.

## Comments
