from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Item, ItemClassification, Location, Region
from worlds.age2de.Options import Goal

from ..locations.Scenarios import Age2ScenarioData, scenario_names

from ..items.Items import Age2ItemData
from ..items.Events import Event
from ..locations.Locations import TYPE_TO_LOCATIONS, VICTORY_LOCATIONS, Age2LocationData, Age2LocationType
from worlds.generic.Rules import CollectionRule, set_rule

if TYPE_CHECKING:
    from .. import Age2World

def set_rules(world: Age2World) -> None:
    for key, value in VICTORY_LOCATIONS.items():
        region = world.get_region(value.scenario.scenario_name)
        victory_loc = Location(world.player, "Complete " + value.scenario.scenario_name, None, region)
        victory_loc.place_locked_item(Item(value.scenario.scenario_name + ": Unlock Next Scenario", ItemClassification.progression, None, world.player))
        region.add_event("Complete " + value.scenario.scenario_name, value.scenario.scenario_name + ": Unlock Next Scenario", show_in_spoiler=False)

    # Attila Scenarios
    att1 = world.get_entrance(Age2ScenarioData.AP_ATTILA_1.scenario_name)
    set_rule(att1, lambda state: state.can_reach_region("Menu", player= world.player)
             and state.has_all(["Attila the Hun Campaign"], world.player))
    
    att2 = world.get_entrance(Age2ScenarioData.AP_ATTILA_2.scenario_name)
    set_rule(att2, lambda state: state.has(Age2LocationData.ATT1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario", world.player)
             and state.has("Progressive Attila Scenario", world.player))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_1.scenario_name), att2)
    
    att3 = world.get_entrance(Age2ScenarioData.AP_ATTILA_3.scenario_name)
    set_rule(att3, lambda state: state.has(Age2LocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario", world.player)
             and state.has("Progressive Attila Scenario", world.player, 2))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_2.scenario_name), att3)
    
    att4 = world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name)
    set_rule(att4, lambda state: state.has(Age2LocationData.ATT3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario", world.player)
             and state.has("Progressive Attila Scenario", world.player, 3))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_3.scenario_name), att4)
    
    att5 = world.get_entrance(Age2ScenarioData.AP_ATTILA_5.scenario_name)
    set_rule(att5, lambda state: state.has(Age2LocationData.ATT4_VICTORY.scenario.scenario_name + ": Unlock Next Scenario", world.player)
             and state.has("Progressive Attila Scenario", world.player, 4))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_4.scenario_name), att5)
    
    att6 = world.get_entrance(Age2ScenarioData.AP_ATTILA_6.scenario_name)
    set_rule(att6, lambda state: state.has(Age2LocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario", world.player)
             and state.has("Progressive Attila Scenario", world.player, 5))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_5.scenario_name), att6)
    
    # starting tc rules

    def can_build_tc(state: CollectionState) -> bool:
        return state.has_all([Age2ItemData.TOWN_CENTER_STONE.item_name, Age2ItemData.TOWN_CENTER_WOOD.item_name], world.player)
    
    # scenario-specific rules

    def has_attila_1_attila_camp(state: CollectionState) -> bool:
        return state.has(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name, world.player)

    def has_attila_1_bleda_camp(state: CollectionState) -> bool:
        return state.has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name, world.player)

    def has_attila_2_vils(state: CollectionState) -> bool:
        return state.has(Age2ItemData.AP_ATTILA_2_VILLAGERS.item_name, world.player)

    def has_attila_3_gold(state: CollectionState) -> bool:
        return state.has_all([Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name, Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name], world.player)
    
    set_rule(world.get_location(Age2LocationData.ATT1_VICTORY.global_name()), lambda state: ((has_attila_1_attila_camp(state) and can_build_tc(state)) or has_attila_1_bleda_camp(state)))
    set_rule(world.get_location("Complete " + Age2LocationData.ATT1_VICTORY.scenario.scenario_name), lambda state: ((has_attila_1_attila_camp(state) and can_build_tc(state)) or has_attila_1_bleda_camp(state)))
    set_rule(world.get_location(Age2LocationData.ATT1_CAPTURE_HORSES_CAMP.global_name()), has_attila_1_bleda_camp)
    set_rule(world.get_location(Age2LocationData.ATT2_VICTORY.global_name()), lambda state: (has_attila_2_vils(state) and can_build_tc(state)))
    set_rule(world.get_location("Complete " + Age2LocationData.ATT2_VICTORY.scenario.scenario_name), lambda state: (has_attila_2_vils(state) and can_build_tc(state)))
    set_rule(world.get_location(Age2LocationData.ATT2_BUILD_TC.global_name()), lambda state: (has_attila_2_vils(state) and can_build_tc(state)))
    set_rule(world.get_location(Age2LocationData.ATT3_BLUE_DOCK_NORTH.global_name()), has_attila_3_gold)
    set_rule(world.get_location(Age2LocationData.ATT3_BLUE_DOCKS_SOUTH.global_name()), has_attila_3_gold)
    set_rule(world.get_location(Age2LocationData.ATT3_DESTROY_WONDER.global_name()), has_attila_3_gold)
    set_rule(world.get_location(Age2LocationData.ATT3_THREATEN_WONDER.global_name()), has_attila_3_gold)
