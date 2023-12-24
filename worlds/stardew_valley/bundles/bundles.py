from random import Random
from typing import List

from .bundle_room import BundleRoom
from ..data.bundle_data import pantry_vanilla, crafts_room_vanilla, fish_tank_vanilla, boiler_room_vanilla, bulletin_board_vanilla, vault_vanilla, \
    pantry_thematic, crafts_room_thematic, fish_tank_thematic, boiler_room_thematic, bulletin_board_thematic, vault_thematic, pantry_remixed, \
    crafts_room_remixed, fish_tank_remixed, boiler_room_remixed, bulletin_board_remixed, vault_remixed, all_bundle_items_except_money, \
    abandoned_joja_mart_thematic, abandoned_joja_mart_vanilla, abandoned_joja_mart_remixed
from ..logic.logic import StardewLogic
from ..multi_world_adapter import PlayerMultiWorldAdapter
from ..options import BundleRandomization, StardewValleyOptions, ExcludeGingerIsland


def get_all_bundles(random: Random, logic: StardewLogic, world: PlayerMultiWorldAdapter) -> List[BundleRoom]:
    if world.options.bundle_randomization == BundleRandomization.option_vanilla:
        return get_vanilla_bundles(random, world.options)
    elif world.options.bundle_randomization == BundleRandomization.option_thematic:
        return get_thematic_bundles(random, world.options)
    elif world.options.bundle_randomization == BundleRandomization.option_remixed:
        return get_remixed_bundles(random, world.options)
    elif world.options.bundle_randomization == BundleRandomization.option_shuffled:
        return get_shuffled_bundles(random, logic, world)

    raise NotImplementedError


def get_vanilla_bundles(random: Random, options: StardewValleyOptions) -> List[BundleRoom]:
    allow_island = options.exclude_ginger_island == ExcludeGingerIsland.option_false
    pantry = pantry_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    crafts_room = crafts_room_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    fish_tank = fish_tank_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    boiler_room = boiler_room_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    bulletin_board = bulletin_board_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    vault = vault_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    abandoned_joja_mart = abandoned_joja_mart_vanilla.create_bundle_room(options.bundle_price, random, allow_island)
    return [pantry, crafts_room, fish_tank, boiler_room, bulletin_board, vault, abandoned_joja_mart]


def get_thematic_bundles(random: Random, options: StardewValleyOptions) -> List[BundleRoom]:
    allow_island = options.exclude_ginger_island == ExcludeGingerIsland.option_false
    pantry = pantry_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    crafts_room = crafts_room_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    fish_tank = fish_tank_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    boiler_room = boiler_room_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    bulletin_board = bulletin_board_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    vault = vault_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    abandoned_joja_mart = abandoned_joja_mart_thematic.create_bundle_room(options.bundle_price, random, allow_island)
    return [pantry, crafts_room, fish_tank, boiler_room, bulletin_board, vault, abandoned_joja_mart]


def get_remixed_bundles(random: Random, options: StardewValleyOptions) -> List[BundleRoom]:
    allow_island = options.exclude_ginger_island == ExcludeGingerIsland.option_false
    pantry = pantry_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    crafts_room = crafts_room_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    fish_tank = fish_tank_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    boiler_room = boiler_room_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    bulletin_board = bulletin_board_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    vault = vault_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    abandoned_joja_mart = abandoned_joja_mart_remixed.create_bundle_room(options.bundle_price, random, allow_island)
    return [pantry, crafts_room, fish_tank, boiler_room, bulletin_board, vault, abandoned_joja_mart]


def get_shuffled_bundles(random: Random, logic: StardewLogic, world: PlayerMultiWorldAdapter) -> List[BundleRoom]:
    allow_island = world.options.exclude_ginger_island == ExcludeGingerIsland.option_false
    valid_bundle_items = [bundle_item for bundle_item in all_bundle_items_except_money if allow_island or not bundle_item.requires_island]

    rooms = [room for room in get_remixed_bundles(random, world.options) if room.name != "Vault"]
    required_items = 0
    for room in rooms:
        for bundle in room.bundles:
            required_items += len(bundle.items)
        random.shuffle(room.bundles)
    random.shuffle(rooms)

    chosen_bundle_items = random.sample(valid_bundle_items, required_items)
    sorted_bundle_items = sorted(chosen_bundle_items, key=lambda x: logic.has(x.item_name).get_difficulty(world))
    for room in rooms:
        for bundle in room.bundles:
            num_items = len(bundle.items)
            bundle.items = sorted_bundle_items[:num_items]
            sorted_bundle_items = sorted_bundle_items[num_items:]

    vault = vault_remixed.create_bundle_room(world.options.bundle_price, random, allow_island)
    return [*rooms, vault]
