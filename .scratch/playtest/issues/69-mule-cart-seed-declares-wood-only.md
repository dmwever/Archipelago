# 69: Starting Mule Cart Resources gives food in game but declares wood only in logic

**Reported:** 2026-11-02, playtesting

**Status:** needs-triage

## Report

"Starting Mule Cart Resources".

## The two sides disagree about what the item contains

**The game gives both resources.** `ProgressionItems.xs`:

```xs
void MuleCartResources() {
    xsEffectAmount(cModResource, cAttributeWood, cAttributeAdd, 80.0, 1);
    xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 20.0, 1);
}
```

80 wood and 20 food - exactly the Mule Cart's cost, `{FOOD: 20, WOOD: 80}`. It is the only seed
handler that grants two resources, and the item's name is the only one that says "Resources"
rather than naming a single one.

**Logic declares one.** `items/Items.py:493`:

```python
MULE_CART_RESOURCES = 1033, "Starting Mule Cart Resources", SeedResources(Resource.WOOD, 80)
```

Compare the siblings, all single-resource and all matching their handler:

| item | declared | handler grants |
| --- | --- | --- |
| Starting Lumber Camp Wood | WOOD 100 | 100 wood |
| Starting Dock Wood | WOOD 150 | 150 wood |
| Starting Market Wood | WOOD 175 | 175 wood |
| Starting Villager Food | FOOD 150 | 150 food |
| Feudal Age Food | FOOD 500 | 500 food |
| **Starting Mule Cart Resources** | **WOOD 80** | **80 wood + 20 food** |

## What it costs

`ScenarioLogic._has_seeded_building` banks whatever the seed item does not cover:

```python
banked = {resource: amount for resource, amount in building.cost.items()
          if resource is not seed.type.type}
seeded = Has(seed.item_name) & self.logic.resources.has_amounts(banked)
```

The seed's type is WOOD, so `banked` becomes `{FOOD: 20}` and the rule is

```
Has("Starting Mule Cart Resources") & has_amount(FOOD, 20)
```

The food half is already in the player's hands the moment the item lands, so logic asks for a
food source the player demonstrably does not need. That is too strict rather than too generous -
it cannot strand a seed, but it can gate the Mule Cart behind food in a scenario where food is
hard to come by, and the Mule Cart is one of the four buildings the glossary names as able to
open an economy from nothing.

## The fix

Make `SeedResources` carry the pair, so the declaration matches the handler and `banked` comes
out empty. Whether `SeedResources` already supports more than one resource is not checked here;
if it does not, that is the work.

The alternative - drop the 20 food from `MuleCartResources()` so the handler matches the
declaration - is worse: the player would then hold a "Resources" item that cannot pay for the
building it is named after.

## Unverified

The reporter gave the item name with no symptom. The above is a code-side mismatch found from
that name; whether it matches what was seen in play is not established. If the symptom was
something else - the item not arriving, or the wrong amount - say so and this ticket needs
re-pointing.

## Comments
