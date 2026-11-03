# 63: The pavilion is invulnerable but still targetable

**Reported:** 2026-10-31, playtesting

**Status:** ready-for-agent

## Report

The camps are currently attackable by opponents. They are invincible, so nothing comes of it,
but enemies still target them. There should be a flag that stops them being targeted at all.

## What the code sets today

`APavilion.xs`, `SetupPavilion()`:

```xs
void SetupPavilion() {
    xsSetUnitName(pavilionId, "APavilion");
    xsEffectAmount(cSetUnitAttribute, pavilionId, cInvulnerabilityLevel,
                   PAVILION_INVULNERABILITY, PAVILION_OWNER);
    xsSetUnitProperty(pavilionId, cUnitDeletable, PAVILION_DELETABLE);
}
```

Invulnerability and deletability only. Nothing touches whether the thing can be picked as a
target, which is why enemy units walk over and swing at it forever.

`cSetUnitAttribute` has no attribute for this - the dat attribute enum runs `hit_points`,
`line_of_sight`, `garrison_capacity`, `unit_size_*`, `movement_speed`, `armor`, `attack`,
`max_range`, `work_rate` and so on up to `regeneration_rate`, with nothing about targeting. So
the attribute route is a dead end.

## The flag exists, on the other API

The unit **property** list has three that bear on this, all get and set, all driven through
`xsSetUnitProperty`:

| constant | |
| --- | --- |
| **`cUnitTargetable`** | the one this ticket is about |
| `cUnitAttackable` | neighbouring, may be the better or the additional one |
| `cUnitSelectable` | whether the player can click it - **leave alone**, the pavilion needs selecting for the victory button and the mercenary seats |

Signature:

```
bool xsSetUnitProperty(int unitId, int property, float value, int typeOrForce)
```

`SetupPavilion` already calls it for `cUnitDeletable`, so the call shape is established in this
file and the addition is one line beside it.

## What is not established

Which of `cUnitTargetable` and `cUnitAttackable` actually stops an enemy choosing the pavilion,
and whether one implies the other. The knowledge base lists both as settable unit properties and
says no more; neither is engine-verified here. A throwaway spike in `Test.xs` that sets one,
then the other, then both, and watches whether enemies still swing, would settle it in one run -
and the existing `XsTesting.aoe2scenario` harness is already set up for exactly that.

Also unknown: whether an untargetable building still blocks pathing, and whether the AI gets
stuck trying to path around something it can no longer attack.

## Scope

`SetupPavilion()` is the only place that needs the change, and it covers every scenario, since
every pavilion is created through `InitPavilion`.

## Comments
