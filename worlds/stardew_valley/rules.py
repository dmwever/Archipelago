import itertools
from typing import Dict, List

from BaseClasses import MultiWorld
from worlds.generic import Rules as MultiWorldRules
from . import options, locations
from .bundles import Bundle
from .data.entrance_data import dig_to_mines_floor, SVEntrance
from .data.museum_data import all_museum_items, all_mineral_items, all_artifact_items, \
    dwarf_scrolls, skeleton_front, \
    skeleton_middle, skeleton_back, all_museum_items_by_name
from .data.region_data import SVRegion
from .locations import LocationTags
from .logic import StardewLogic, And, tool_prices, week_days
from .options import StardewOptions


def set_rules(multi_world: MultiWorld, player: int, world_options: StardewOptions, logic: StardewLogic,
              current_bundles: Dict[str, Bundle]):
    all_location_names = list(location.name for location in multi_world.get_locations(player))

    for floor in range(5, 120 + 5, 5):
        MultiWorldRules.set_rule(multi_world.get_entrance(dig_to_mines_floor(floor), player),
                                 logic.can_mine_to_floor(floor).simplify())

    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.enter_tide_pools, player),
                             logic.received("Beach Bridge").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.enter_quarry, player),
                             logic.received("Bridge Repair").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.enter_secret_woods, player),
                             logic.has_tool("Axe", "Iron").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.forest_to_sewers, player),
                             logic.has_rusty_key().simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.town_to_sewers, player),
                             logic.has_rusty_key().simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.take_bus_to_desert, player),
                             logic.received("Bus Repair").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.enter_skull_cavern, player),
                             logic.received("Skull Key").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.mine_to_skull_cavern_floor_100, player),
                             logic.can_mine_perfectly_in_the_skull_cavern().simplify())

    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.use_desert_obelisk, player),
                             logic.received("Desert Obelisk").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.use_island_obelisk, player),
                             logic.received("Island Obelisk").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.use_farm_obelisk, player),
                             logic.received("Farm Obelisk").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.talk_to_traveling_merchant, player),
                             logic.has_traveling_merchant())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.enter_greenhouse, player),
                             logic.received("Greenhouse"))

    set_ginger_island_rules(logic, multi_world, player, world_options)

    # Those checks do not exist if ToolProgression is vanilla
    if world_options[options.ToolProgression] != options.ToolProgression.option_vanilla:
        MultiWorldRules.add_rule(multi_world.get_location("Purchase Fiberglass Rod", player),
                                 (logic.has_skill_level("Fishing", 2) & logic.can_spend_money(1800)).simplify())
        MultiWorldRules.add_rule(multi_world.get_location("Purchase Iridium Rod", player),
                                 (logic.has_skill_level("Fishing", 6) & logic.can_spend_money(7500)).simplify())

        materials = [None, "Copper", "Iron", "Gold", "Iridium"]
        tool = ["Hoe", "Pickaxe", "Axe", "Watering Can", "Trash Can"]
        for (previous, material), tool in itertools.product(zip(materials[:4], materials[1:]), tool):
            if previous is None:
                MultiWorldRules.add_rule(multi_world.get_location(f"{material} {tool} Upgrade", player),
                                         (logic.has(f"{material} Ore") &
                                          logic.can_spend_money(tool_prices[material])).simplify())
            else:
                MultiWorldRules.add_rule(multi_world.get_location(f"{material} {tool} Upgrade", player),
                                         (logic.has(f"{material} Ore") & logic.has_tool(tool, previous) &
                                          logic.can_spend_money(tool_prices[material])).simplify())

    # Skills
    if world_options[options.SkillProgression] != options.SkillProgression.option_vanilla:
        for i in range(1, 11):
            MultiWorldRules.set_rule(multi_world.get_location(f"Level {i} Farming", player),
                                     logic.can_earn_skill_level("Farming", i).simplify())
            MultiWorldRules.set_rule(multi_world.get_location(f"Level {i} Fishing", player),
                                     logic.can_earn_skill_level("Fishing", i).simplify())
            MultiWorldRules.set_rule(multi_world.get_location(f"Level {i} Foraging", player),
                                     logic.can_earn_skill_level("Foraging", i).simplify())
            MultiWorldRules.set_rule(multi_world.get_location(f"Level {i} Mining", player),
                                     logic.can_earn_skill_level("Mining", i).simplify())
            MultiWorldRules.set_rule(multi_world.get_location(f"Level {i} Combat", player),
                                     logic.can_earn_skill_level("Combat", i).simplify())

    # Bundles
    for bundle in current_bundles.values():
        location = multi_world.get_location(bundle.get_name_with_bundle(), player)
        rules = logic.can_complete_bundle(bundle.requirements, bundle.number_required)
        simplified_rules = rules.simplify()
        MultiWorldRules.set_rule(location, simplified_rules)
    MultiWorldRules.add_rule(multi_world.get_location("Complete Crafts Room", player),
                             And(logic.can_reach_location(bundle.name)
                                 for bundle in locations.locations_by_tag[LocationTags.CRAFTS_ROOM_BUNDLE]).simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Complete Pantry", player),
                             And(logic.can_reach_location(bundle.name)
                                 for bundle in locations.locations_by_tag[LocationTags.PANTRY_BUNDLE]).simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Complete Fish Tank", player),
                             And(logic.can_reach_location(bundle.name)
                                 for bundle in locations.locations_by_tag[LocationTags.FISH_TANK_BUNDLE]).simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Complete Boiler Room", player),
                             And(logic.can_reach_location(bundle.name)
                                 for bundle in locations.locations_by_tag[LocationTags.BOILER_ROOM_BUNDLE]).simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Complete Bulletin Board", player),
                             And(logic.can_reach_location(bundle.name)
                                 for bundle
                                 in locations.locations_by_tag[LocationTags.BULLETIN_BOARD_BUNDLE]).simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Complete Vault", player),
                             And(logic.can_reach_location(bundle.name)
                                 for bundle in locations.locations_by_tag[LocationTags.VAULT_BUNDLE]).simplify())

    # Buildings
    if world_options[options.BuildingProgression] != options.BuildingProgression.option_vanilla:
        for building in locations.locations_by_tag[LocationTags.BUILDING_BLUEPRINT]:
            MultiWorldRules.set_rule(multi_world.get_location(building.name, player),
                                     logic.building_rules[building.name.replace(" Blueprint", "")].simplify())

    set_story_quests_rules(all_location_names, logic, multi_world, player)
    set_special_order_rules(all_location_names, logic, multi_world, player, world_options)
    set_help_wanted_quests_rules(logic, multi_world, player, world_options)
    set_fishsanity_rules(all_location_names, logic, multi_world, player)
    set_museumsanity_rules(all_location_names, logic, multi_world, player, world_options)
    set_friendsanity_rules(all_location_names, logic, multi_world, player)
    set_backpack_rules(logic, multi_world, player, world_options)

    MultiWorldRules.add_rule(multi_world.get_location("Old Master Cannoli", player),
                             logic.has("Sweet Gem Berry").simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Galaxy Sword Shrine", player),
                             logic.has("Prismatic Shard").simplify())

    set_traveling_merchant_rules(logic, multi_world, player)
    set_arcade_machine_rules(logic, multi_world, player, world_options)


def set_ginger_island_rules(logic, multi_world, player, world_options: StardewOptions):
    if world_options[options.ExcludeGingerIsland] == options.ExcludeGingerIsland.option_true:
        return

    MultiWorldRules.add_rule(multi_world.get_location("Repair Boat Hull", player),
                             logic.has("Hardwood").simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Repair Boat Anchor", player),
                             logic.has("Iridium Bar").simplify())
    MultiWorldRules.add_rule(multi_world.get_location("Repair Ticket Machine", player),
                             logic.has("Battery Pack").simplify())

    boat_repaired = logic.received("Boat Repair").simplify()
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.fish_shop_to_boat_tunnel, player),
                             boat_repaired)
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.boat_to_ginger_island, player),
                             boat_repaired)
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.island_south_to_west, player),
                             logic.received("Island West Turtle").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.island_south_to_north, player),
                             logic.received("Island North Turtle").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.island_west_to_islandfarmhouse, player),
                             logic.received("Island Farmhouse").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.island_north_to_dig_site, player),
                             logic.received("Dig Site Bridge").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.talk_to_island_trader, player),
                             logic.received("Island Trader").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.island_south_to_southeast, player),
                             logic.received("Island Resort").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.island_west_to_qi_walnut_room, player),
                             logic.received("Qi Walnut Room").simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.climb_to_volcano_5, player),
                             logic.can_mine_perfectly().simplify())
    MultiWorldRules.set_rule(multi_world.get_entrance(SVEntrance.climb_to_volcano_10, player),
                             logic.can_mine_perfectly().simplify())
    parrots = [SVEntrance.parrot_express_docks_to_volcano, SVEntrance.parrot_express_jungle_to_volcano,
               SVEntrance.parrot_express_dig_site_to_volcano, SVEntrance.parrot_express_docks_to_dig_site,
               SVEntrance.parrot_express_jungle_to_dig_site, SVEntrance.parrot_express_volcano_to_dig_site,
               SVEntrance.parrot_express_docks_to_jungle, SVEntrance.parrot_express_dig_site_to_jungle,
               SVEntrance.parrot_express_volcano_to_jungle, SVEntrance.parrot_express_jungle_to_docks,
               SVEntrance.parrot_express_dig_site_to_docks, SVEntrance.parrot_express_volcano_to_docks]
    for parrot in parrots:
        MultiWorldRules.set_rule(multi_world.get_entrance(parrot, player), logic.received("Parrot Express").simplify())


def set_story_quests_rules(all_location_names: List[str], logic, multi_world, player):
    for quest in locations.locations_by_tag[LocationTags.QUEST]:
        if quest.name in all_location_names:
            MultiWorldRules.set_rule(multi_world.get_location(quest.name, player),
                                     logic.quest_rules[quest.name].simplify())


def set_special_order_rules(all_location_names: List[str], logic, multi_world, player, world_options: StardewOptions):
    if world_options[options.SpecialOrderLocations] == options.SpecialOrderLocations.option_disabled:
        return
    board_rule = logic.received("Special Order Board") & logic.has_lived_months(4)
    for board_order in locations.locations_by_tag[LocationTags.SPECIAL_ORDER_BOARD]:
        if board_order.name in all_location_names:
            order_rule = board_rule & logic.special_order_rules[board_order.name]
            MultiWorldRules.set_rule(multi_world.get_location(board_order.name, player), order_rule.simplify())

    if world_options[options.ExcludeGingerIsland] == options.ExcludeGingerIsland.option_true:
        return
    if world_options[options.SpecialOrderLocations] == options.SpecialOrderLocations.option_board_only:
        return
    qi_rule = logic.can_reach_region(SVRegion.qi_walnut_room) & logic.has_lived_months(8)
    for qi_order in locations.locations_by_tag[LocationTags.SPECIAL_ORDER_QI]:
        if qi_order.name in all_location_names:
            order_rule = qi_rule & logic.special_order_rules[qi_order.name]
            MultiWorldRules.set_rule(multi_world.get_location(qi_order.name, player), order_rule.simplify())


def set_help_wanted_quests_rules(logic, multi_world, player, world_options):
    desired_number_help_wanted: int = world_options[options.HelpWantedLocations] // 7
    for i in range(0, desired_number_help_wanted):
        prefix = "Help Wanted:"
        delivery = "Item Delivery"
        rule = logic.received("Month End", i)
        fishing_rule = rule & logic.can_fish()
        slay_rule = rule & logic.has_any_weapon()
        item_delivery_index = (i * 4) + 1
        for j in range(item_delivery_index, item_delivery_index + 4):
            location_name = f"{prefix} {delivery} {j}"
            MultiWorldRules.set_rule(multi_world.get_location(location_name, player), rule.simplify())

        MultiWorldRules.set_rule(multi_world.get_location(f"{prefix} Gathering {i + 1}", player),
                                 rule.simplify())
        MultiWorldRules.set_rule(multi_world.get_location(f"{prefix} Fishing {i + 1}", player),
                                 fishing_rule.simplify())
        MultiWorldRules.set_rule(multi_world.get_location(f"{prefix} Slay Monsters {i + 1}", player),
                                 slay_rule.simplify())


def set_fishsanity_rules(all_location_names: List[str], logic: StardewLogic, multi_world: MultiWorld, player: int):
    fish_prefix = "Fishsanity: "
    for fish_location in locations.locations_by_tag[LocationTags.FISHSANITY]:
        if fish_location.name in all_location_names:
            fish_name = fish_location.name[len(fish_prefix):]
            MultiWorldRules.set_rule(multi_world.get_location(fish_location.name, player),
                                     logic.has(fish_name).simplify())


def set_museumsanity_rules(all_location_names: List[str], logic: StardewLogic, multi_world: MultiWorld, player: int,
                           world_options: StardewOptions):
    museum_prefix = "Museumsanity: "
    if world_options[options.Museumsanity] == options.Museumsanity.option_milestones:
        for museum_milestone in locations.locations_by_tag[LocationTags.MUSEUM_MILESTONES]:
            set_museum_milestone_rule(logic, multi_world, museum_milestone, museum_prefix, player)
    elif world_options[options.Museumsanity] != options.Museumsanity.option_none:
        set_museum_individual_donations_rules(all_location_names, logic, multi_world, museum_prefix, player)


def set_museum_individual_donations_rules(all_location_names, logic, multi_world, museum_prefix, player):
    all_donations = sorted(locations.locations_by_tag[LocationTags.MUSEUM_DONATIONS],
                           key=lambda x: all_museum_items_by_name[x.name[len(museum_prefix):]].difficulty, reverse=True)
    counter = 0
    number_donations = len(all_donations)
    for museum_location in all_donations:
        if museum_location.name in all_location_names:
            donation_name = museum_location.name[len(museum_prefix):]
            required_detectors = counter * 5 // number_donations
            rule = logic.has(donation_name) & logic.received("Traveling Merchant Metal Detector", required_detectors)
            MultiWorldRules.set_rule(multi_world.get_location(museum_location.name, player),
                                     rule.simplify())
        counter += 1


def set_museum_milestone_rule(logic: StardewLogic, multi_world: MultiWorld, museum_milestone, museum_prefix: str,
                              player: int):
    milestone_name = museum_milestone.name[len(museum_prefix):]
    donations_suffix = " Donations"
    minerals_suffix = " Minerals"
    artifacts_suffix = " Artifacts"
    metal_detector = "Traveling Merchant Metal Detector"
    rule = None
    if milestone_name.endswith(donations_suffix):
        rule = get_museum_item_count_rule(logic, donations_suffix, milestone_name, all_museum_items)
    elif milestone_name.endswith(minerals_suffix):
        rule = get_museum_item_count_rule(logic, minerals_suffix, milestone_name, all_mineral_items)
    elif milestone_name.endswith(artifacts_suffix):
        rule = get_museum_item_count_rule(logic, artifacts_suffix, milestone_name, all_artifact_items)
    elif milestone_name == "Dwarf Scrolls":
        rule = logic.has([item.name for item in dwarf_scrolls]) & logic.received(metal_detector, 4)
    elif milestone_name == "Skeleton Front":
        rule = logic.has([item.name for item in skeleton_front]) & logic.received(metal_detector, 4)
    elif milestone_name == "Skeleton Middle":
        rule = logic.has([item.name for item in skeleton_middle]) & logic.received(metal_detector, 4)
    elif milestone_name == "Skeleton Back":
        rule = logic.has([item.name for item in skeleton_back]) & logic.received(metal_detector, 4)
    elif milestone_name == "Ancient Seed":
        rule = logic.has("Ancient Seed") & logic.received(metal_detector, 4)
    if rule is None:
        return
    MultiWorldRules.set_rule(multi_world.get_location(museum_milestone.name, player), rule.simplify())


def get_museum_item_count_rule(logic, suffix, milestone_name, accepted_items):
    metal_detector = "Traveling Merchant Metal Detector"
    num = int(milestone_name[:milestone_name.index(suffix)])
    required_detectors = (num - 1) * 5 // len(accepted_items)
    rule = logic.has([item.name for item in accepted_items], num) & logic.received(metal_detector, required_detectors)
    return rule


def set_backpack_rules(logic: StardewLogic, multi_world: MultiWorld, player: int, world_options):
    if world_options[options.BackpackProgression] != options.BackpackProgression.option_vanilla:
        MultiWorldRules.set_rule(multi_world.get_location("Large Pack", player),
                                 logic.can_spend_money(2000).simplify())
        MultiWorldRules.set_rule(multi_world.get_location("Deluxe Pack", player),
                                 (logic.can_spend_money(10000) & logic.received("Progressive Backpack")).simplify())


def set_traveling_merchant_rules(logic: StardewLogic, multi_world: MultiWorld, player: int):
    for day in week_days:
        item_for_day = f"Traveling Merchant: {day}"
        for i in range(1, 4):
            location_name = f"Traveling Merchant {day} Item {i}"
            MultiWorldRules.set_rule(multi_world.get_location(location_name, player),
                                     logic.received(item_for_day))


def set_arcade_machine_rules(logic: StardewLogic, multi_world: MultiWorld, player: int, world_options):
    if world_options[options.ArcadeMachineLocations] == options.ArcadeMachineLocations.option_full_shuffling:
        MultiWorldRules.add_rule(multi_world.get_entrance(SVEntrance.play_junimo_kart, player),
                                 (logic.received("Skull Key") & logic.has("Junimo Kart Small Buff")).simplify())
        MultiWorldRules.add_rule(multi_world.get_entrance(SVEntrance.reach_junimo_kart_2, player),
                                 logic.has("Junimo Kart Medium Buff").simplify())
        MultiWorldRules.add_rule(multi_world.get_entrance(SVEntrance.reach_junimo_kart_3, player),
                                 logic.has("Junimo Kart Big Buff").simplify())
        MultiWorldRules.add_rule(multi_world.get_location("Junimo Kart: Sunset Speedway (Victory)", player),
                                 logic.has("Junimo Kart Max Buff").simplify())
        MultiWorldRules.add_rule(multi_world.get_entrance(SVEntrance.play_journey_of_the_prairie_king, player),
                                 logic.has("JotPK Small Buff").simplify())
        MultiWorldRules.add_rule(multi_world.get_entrance(SVEntrance.reach_jotpk_world_2, player),
                                 logic.has("JotPK Medium Buff").simplify())
        MultiWorldRules.add_rule(multi_world.get_entrance(SVEntrance.reach_jotpk_world_3, player),
                                 logic.has("JotPK Big Buff").simplify())
        MultiWorldRules.add_rule(multi_world.get_location("Journey of the Prairie King Victory", player),
                                 logic.has("JotPK Max Buff").simplify())


def set_friendsanity_rules(all_location_names: List[str], logic: StardewLogic, multi_world: MultiWorld, player: int):
    friend_prefix = "Friendsanity: "
    friend_suffix = " <3"
    for friend_location in locations.locations_by_tag[LocationTags.FRIENDSANITY]:
        if not friend_location.name in all_location_names:
            continue
        friend_location_without_prefix = friend_location.name[len(friend_prefix):]
        friend_location_trimmed = friend_location_without_prefix[:friend_location_without_prefix.index(friend_suffix)]
        parts = friend_location_trimmed.split(" ")
        friend_name = parts[0]
        num_hearts = int(parts[1])
        MultiWorldRules.set_rule(multi_world.get_location(friend_location.name, player),
                                 logic.can_earn_relationship(friend_name, num_hearts).simplify())
