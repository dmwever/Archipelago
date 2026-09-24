from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Location, MultiWorld, Region

from ..generation.UnitPool import UnitLocation, UnitPool
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData

if TYPE_CHECKING:
    from .. import Age2World

class UnitEntranceKind:
    train = "train"              # you built something that turns them out
    startup = "startup"          # the scenario handed it over before you touched anything
    trigger = "trigger"          # a trigger hands it over during play
    conversion = "conversion"    # you took someone else's - a placeholder, closed by UnitRules

class UnitEntrance(Entrance):
    def __init__(self, player: int, name: str, parent: Region, kind: str,
                 via: Age2BuildingData | Age2ScenarioData) -> None:
        super().__init__(player, name, parent)
        self.kind = kind
        self.via = via


class UnitRegion(Region):
    def __init__(self, name: str, player: int, multiworld: MultiWorld,
                 target: UnitLocation, unit_locations: list[UnitLocation]) -> None:
        super().__init__(name, player, multiworld)
        self.target = target
        self.unit_locations = unit_locations


class UnitRegions:
    def __init__(self, world: 'Age2World',
                 building_regions: dict[Age2BuildingData, Region],
                 scenario_regions: dict[Age2ScenarioData, Region]) -> None:
        self.world = world
        self.pool: UnitPool = world.unit_pool
        self.building_regions = building_regions
        self.scenario_regions = scenario_regions
        self.regions: list[UnitRegion] = []
        self.shuffled_lines: list[Age2UnitLineData] = []
        self.shuffled_units: list[UnitLocation] = []
        self.shuffled_unit_building_items: list[Age2BuildingData] = []
        self.shuffled_villager = False

    def create(self) -> list[Region]:
        self.regions = []
        for line, locations in self.pool.line_locations.items():
            region = self.add_line_region(line, locations)
            if region is not None:
                self.regions.append(region)
        for special in self.pool.special_units:
            self.regions.append(self.add_special_region(special))
        return list(self.regions)

    def add_line_region(self, line: Age2UnitLineData,
                        locations: list[UnitLocation]) -> UnitRegion | None:
        trainable = [building for building in line.head.buildings
                     if building in self.building_regions] \
            if self.pool.is_trainable(line) else []
        granting = [scenario for scenario in self.scenario_regions
                    if self.pool.startup_grants(scenario, line)
                    or self.pool.trigger_grants(scenario, line)]
        if not trainable and not granting:
            return None

        region = UnitRegion(line.line_name, self.world.player, self.world.multiworld,
                            line, locations)
        for location in locations:
            region.locations.append(
                Location(self.world.player, location.location_name, location.id, region))
            self.record(location, trainable)

        for building in trainable:
            self.add_building_entrance(line, region, building)
        for scenario, scenario_region in self.scenario_regions.items():
            self.add_scenario_start_entrance(line.line_name, region, scenario, scenario_region)
            self.add_scenario_trigger_entrance(line.line_name, region, scenario, scenario_region)
            self.add_conversion_entrance(line.line_name, region, scenario, scenario_region)
        return region

    def add_special_region(self, special: UnitLocation) -> UnitRegion:
        label = getattr(special, "hero_name", None) or special.escort_name
        region = UnitRegion(label, self.world.player, self.world.multiworld, special, [special])
        region.locations.append(
            Location(self.world.player, special.location_name, special.id, region))
        for scenario, scenario_region in self.scenario_regions.items():
            self.add_scenario_start_entrance(label, region, scenario, scenario_region)
            self.add_scenario_trigger_entrance(label, region, scenario, scenario_region)
        return region

    def add_building_entrance(self, line: Age2UnitLineData, region: UnitRegion,
                              building: Age2BuildingData) -> None:
        self.add_entrance(self.building_regions[building], region, UnitEntranceKind.train, building,
                          f"Train {line.line_name} at {building.item.item_name}")

    def add_scenario_start_entrance(self, label: str, region: UnitRegion,
                                    scenario: Age2ScenarioData, source: Region) -> None:
        if self.pool.startup_grants(scenario, region.target):
            self.add_entrance(source, region, UnitEntranceKind.startup, scenario,
                              f"{label} at {scenario.scenario_name} Start")

    def add_scenario_trigger_entrance(self, label: str, region: UnitRegion,
                                      scenario: Age2ScenarioData, source: Region) -> None:
        if self.pool.trigger_grants(scenario, region.target):
            self.add_entrance(source, region, UnitEntranceKind.trigger, scenario,
                              f"{label} by {scenario.scenario_name} Trigger")

    def add_conversion_entrance(self, label: str, region: UnitRegion,
                                scenario: Age2ScenarioData, source: Region) -> None:
        self.add_entrance(source, region, UnitEntranceKind.conversion, scenario,
                          f"{label} by {scenario.scenario_name} Conversion")

    def add_entrance(self, source: Region, region: UnitRegion, kind: str,
                     via: Age2BuildingData | Age2ScenarioData, name: str) -> None:
        entrance = UnitEntrance(self.world.player, name, source, kind, via)
        source.exits.append(entrance)
        entrance.connect(region)

    def record(self, location: UnitLocation,
               producers: list[Age2BuildingData]) -> None:
        if self.pool.is_villager_location(location):
            self.shuffled_villager = True
            return
        if isinstance(location, Age2UnitLineData):
            self.shuffled_lines.append(location)
            self.shuffled_units += [unit for unit in location.units if self.pool.includes(unit)]
        else:
            self.shuffled_units.append(location)
            if location.line not in self.shuffled_lines:
                self.shuffled_lines.append(location.line)
        for building in producers:
            if building not in self.shuffled_unit_building_items:
                self.shuffled_unit_building_items.append(building)

    def items(self) -> list[Age2ItemData]:
        return self.pool.items(self.shuffled_lines, self.shuffled_units,
                               self.shuffled_unit_building_items, self.shuffled_villager)
