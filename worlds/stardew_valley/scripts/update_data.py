import csv
import itertools
import os
from typing import List

from worlds.stardew_valley import LocationData
from worlds.stardew_valley.fish_data import all_fish_items
from worlds.stardew_valley.items import load_item_csv, Group, ItemData, load_resource_pack_csv, friendship_pack
from worlds.stardew_valley.locations import load_location_csv, LocationTags

RESOURCE_PACK_CODE_OFFSET = 500
world_folder = os.path.dirname(__file__)


def write_item_csv(items: List[ItemData]):
    with open(world_folder + "/../data/items.csv", 'w', newline='') as file:
        writer = csv.DictWriter(file, ['id', 'name', 'classification', 'groups'])
        writer.writeheader()
        for item in items:
            item_dict = {
                'id': item.code_without_offset,
                'name': item.name,
                'classification': item.classification.name,
                'groups': ','.join(sorted(group.name for group in item.groups))
            }
            writer.writerow(item_dict)


def write_location_csv(locations: List[LocationData]):
    with open(world_folder + "/../data/locations.csv", 'w', newline='') as file:
        write = csv.DictWriter(file, ['id', 'region', 'name', 'tags'])
        write.writeheader()
        for location in locations:
            location_dict = {
                'id': location.code_without_offset,
                'name': location.name,
                'region': location.region,
                'tags': ','.join(sorted(group.name for group in location.tags))
            }
            write.writerow(location_dict)


if __name__ == '__main__':
    loaded_items = load_item_csv()

    item_counter = itertools.count(max(item.code_without_offset
                                       for item in loaded_items
                                       if Group.RESOURCE_PACK not in item.groups
                                       and item.code_without_offset is not None) + 1)
    items_to_write = []
    for item in loaded_items:
        if item.has_any_group(Group.RESOURCE_PACK, Group.FRIENDSHIP_PACK):
            continue

        if item.code_without_offset is None:
            items_to_write.append(ItemData(next(item_counter), item.name, item.classification, item.groups))
            continue

        items_to_write.append(item)

    all_resource_packs = load_resource_pack_csv() + [friendship_pack]
    resource_pack_counter = itertools.count(RESOURCE_PACK_CODE_OFFSET)
    items_to_write.extend(item for resource_pack in all_resource_packs for item in resource_pack.as_item_data(resource_pack_counter))

    write_item_csv(items_to_write)

    loaded_locations = load_location_csv()
    location_counter = itertools.count(max(location.code_without_offset
                                           for location in loaded_locations
                                           if location.code_without_offset is not None) + 1)

    locations_to_write = []
    for location in loaded_locations:
        if location.code_without_offset is None:
            locations_to_write.append(LocationData(next(location_counter), location.region, location.name, location.tags))
            continue

        locations_to_write.append(location)

    write_location_csv(locations_to_write)
