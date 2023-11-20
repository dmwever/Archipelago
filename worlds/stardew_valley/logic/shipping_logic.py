from functools import cached_property

from Utils import cache_self1
from .building_logic import BuildingLogic
from .has_logic import HasLogicMixin
from .region_logic import RegionLogicMixin
from ..locations import LocationTags, locations_by_tag
from ..options import ExcludeGingerIsland
from ..options import SpecialOrderLocations
from ..options import Mods
from ..stardew_rule import StardewRule, And
from ..strings.building_names import Building
from ..strings.region_names import Region


class ShippingLogic:
    exclude_ginger_island: ExcludeGingerIsland
    special_orders_option: SpecialOrderLocations
    mods: Mods
    has: HasLogicMixin
    region: RegionLogicMixin
    buildings: BuildingLogic

    def __init__(self, player: int, exclude_ginger_island: ExcludeGingerIsland, special_orders_option: SpecialOrderLocations,mods: Mods, has: HasLogicMixin,
                 region: RegionLogicMixin, buildings: BuildingLogic):
        self.player = player
        self.exclude_ginger_island = exclude_ginger_island
        self.special_orders_option = special_orders_option
        self.mods = mods
        self.has = has
        self.region = region
        self.buildings = buildings

    @cached_property
    def can_use_shipping_bin(self) -> StardewRule:
        return self.buildings.has_building(Building.shipping_bin)

    @cache_self1
    def can_ship(self, item: str) -> StardewRule:
        return self.can_ship_items & self.has(item)

    @cached_property
    def can_ship_items(self) -> StardewRule:
        return self.region.can_reach(Region.shipping)

    def can_ship_everything(self) -> StardewRule:
        shipsanity_prefix = "Shipsanity: "
        all_items_to_ship = []
        exclude_island = self.exclude_ginger_island == ExcludeGingerIsland.option_true
        exclude_qi = self.special_orders_option != SpecialOrderLocations.option_board_qi
        mod_list = self.mods.value
        for location in locations_by_tag[LocationTags.SHIPSANITY_FULL_SHIPMENT]:
            if exclude_island and LocationTags.GINGER_ISLAND in location.tags:
                continue
            if exclude_qi and LocationTags.REQUIRES_QI_ORDERS in location.tags:
                continue
            if location.mod_name and location.mod_name not in mod_list:
                continue
            all_items_to_ship.append(location.name[len(shipsanity_prefix):])
        return self.buildings.has_building(Building.shipping_bin) & And(*(self.has(item) for item in all_items_to_ship))
