# 15: Joan 2 "Defeat Burgundians at the Bridge" accepts a military that needs Orleans first

**Reported:** 2026-10-20, playtesting

**Status:** needs-triage

## Report

The Maid of Orleans: Defeat Burgundians at the Bridge can be completed in logic with just
`has_military`, but `has_military` needs the player to have reached Orleans first.

## Audit (from code)

Rule (`rules/joan_rules/joan_2.py:16-19, 31`):

```
can_cross          = HasAny(Trade Carts, Dock)
can_conquer_bridge = Has(Trade Carts) | has_military()
```

`has_military()` → `can_field` → `has_base()` and buildings to train from. In Joan 2 every one of
those comes from the **Orleans item alone** (`logic/joan/joan_2.py:32-42`): `has_base`, `has_vils`,
and the standing Town Center, Mill, Archery Range, Barracks, Stable, Blacksmith and Market are all
`has_orleans = Has(Orleans)`.

The Orleans item only gives the player that base once they get there. Getting there is the crossing
(`can_cross`, which is also the rule for Bring Joan to Orleans). Logic doesn't model the trip, so:

- the bridge is in logic with Orleans + an army, with no crossing;
- more broadly, **everything Joan 2 builds on the Orleans base** (economy, military, the castle
  objectives, Victory) is in logic without `can_cross`.

## Likely shape of a fix

Make the Orleans state `Has(Orleans) & can_cross` in `Joan2StartingState`, so the base, villagers
and buildings all wait for the crossing. Then decide what the bridge's military route should be:

- the army reachable after crossing, which may be circular if the bridge *is* the crossing; or
- the starting force (Joan 2 opens with Knights, a Two-Handed Swordsman and Scout Cavalry,
  `ScenarioStartupUnits.py`).

The reporter knows the map's geography better than the code does.
