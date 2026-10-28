from ...items.Items import CATEGORY_TO_ITEMS, Age2ItemData, SeedResources
from ..Ages import Age2AgeData
from ..Buildings import Age2BuildingData

BASE_SEEDS: tuple[Age2ItemData, ...] = (
    Age2ItemData.TOWN_CENTER_WOOD,
    Age2ItemData.TOWN_CENTER_STONE,
    Age2ItemData.STARTING_VILLAGER_FOOD,
)

SEEDED_BUILDINGS: dict[Age2BuildingData, Age2ItemData] = {
    Age2BuildingData.LUMBER_CAMP: Age2ItemData.LUMBER_CAMP_WOOD,
    Age2BuildingData.MULE_CART: Age2ItemData.MULE_CART_RESOURCES,
    Age2BuildingData.DOCK: Age2ItemData.DOCK_WOOD,
    Age2BuildingData.MARKET: Age2ItemData.MARKET_WOOD,
}

SEEDED_AGES: dict[Age2AgeData, Age2ItemData] = {
    Age2AgeData.FEUDAL: Age2ItemData.FEUDAL_AGE_FOOD,
}

for _age, _item in SEEDED_AGES.items():
    _age.seed_item = _item
    _item.type.seeds = _age

for _item in BASE_SEEDS:
    _item.type.seeds = Age2BuildingData.TOWN_CENTER

for _building, _item in SEEDED_BUILDINGS.items():
    _building.seed_item = _item
    _item.type.seeds = _building

assert not [
    item for item in CATEGORY_TO_ITEMS[SeedResources]
    if item.type.seeds is None
], "a seed item seeds no building"

assert len(set(SEEDED_BUILDINGS.values())) == len(SEEDED_BUILDINGS), (
    "one seed item funds two buildings"
)

assert not set(BASE_SEEDS) & set(SEEDED_BUILDINGS.values()), (
    "a base seed item also funds a building"
)

assert not [
    building for building, item in SEEDED_BUILDINGS.items()
    if building.item.type.needed_resources[item.type.type] != item.type.amount
], "a seed item does not carry its building's cost in that resource"
