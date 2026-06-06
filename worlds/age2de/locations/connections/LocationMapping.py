from ..Buildings import Age2BuildingData

from ..Locations import Age2ScenarioLocationData


location_name_list: list[str] = []
location_name_to_id: dict[str, int] = {}
location_id_to_name: dict[int, str] = {}

for location in Age2ScenarioLocationData:
    location_name_list.append(location.global_name())
    location_name_to_id[location.global_name()] = location.id
    location_id_to_name[location.id] = location.global_name()

for building in Age2BuildingData:
    location_name_list.append(building.location_name)
    location_name_to_id[building.location_name] = building.id
    location_id_to_name[building.id] = building.location_name
    