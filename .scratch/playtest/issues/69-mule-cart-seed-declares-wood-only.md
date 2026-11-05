# 69: Starting Mule Cart Resources gives food in game but declares wood only in logic

**Reported:** 2026-11-02, playtesting

**Status:** done

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

**2026-11-04:** Closed by `1dbbf775c`: `ResourcePool.is_economy_route_shuffled` now pools the
Mule Cart seed only when an enabled scenario's civ builds the Mule Cart. No shipped civ does, so
it is never pooled today.

Test: `test_seed_items.py::TestTheMuleCartSeedIsPooledOnlyForACivThatBuildsMuleCarts`.
`test_no_shipped_campaign_pools_it` fails on all three campaigns at `37c6fa8b9` (before the fix)
and passes after it; `test_franks_that_build_mule_carts_pool_it` gives the Franks mule carts and
expects the seed in the pool.

The 80-wood drop in the pinned seed-wood totals followed from the fix: `test_seed_items.py`
(780/630/455 -> 700/550/375, wood target 545 -> 625), `test_item_pool.py` (exact fit 12 -> 13,
one-of-each now iterates the pooled seeds), `test_traps.py` (wood target 220 -> 300).

**2026-11-04:** The declaration half is fixed too. `SeedResources` now carries
`resources: dict[Resource, int]`, and `Starting Mule Cart Resources` declares
`{WOOD: 80, FOOD: 20}` to match `MuleCartResources()`, so `_has_seeded_building` banks nothing
for the Mule Cart. `contributors(FOOD)` now counts its 20 food.

Test: `test_seed_items.py::TestTheMuleCartSeedCarriesItsWholeCost`.
`test_the_seed_item_with_no_food_at_all_is_a_mule_cart` and
`test_the_seed_item_carries_its_wood_and_its_food` fail at HEAD and pass with the change.
