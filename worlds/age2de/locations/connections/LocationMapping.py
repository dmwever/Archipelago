from ..Ages import SHUFFLED_AGES
from ..Buildings import Age2BuildingData
from ..Heroes import Age2HeroData
from ..Techs import Age2TechData
from ..UnitLines import Age2UnitLineData
from ..Units import Age2UnitData
from ..VillagerJobs import Age2VillagerJobData

from ..Locations import Age2ScenarioLocationData

location_name_list: list[str] = []
location_name_to_id: dict[str, int] = {}
location_id_to_name: dict[int, str] = {}

for location in Age2ScenarioLocationData:
    location_name_list.append(location.global_name())
    location_name_to_id[location.global_name()] = location.id
    location_id_to_name[location.id] = location.global_name()

for age in SHUFFLED_AGES:
    location_name_list.append(age.location_name)
    location_name_to_id[age.location_name] = age.id
    location_id_to_name[age.id] = age.location_name

for building in Age2BuildingData:
    location_name_list.append(building.location_name)
    location_name_to_id[building.location_name] = building.id
    location_id_to_name[building.id] = building.location_name
    
for tech in Age2TechData:
    location_name_list.append(tech.location_name)
    location_name_to_id[tech.location_name] = tech.id
    location_id_to_name[tech.id] = tech.location_name

# The whole unit namespace, not just the seed's - the datapackage is static while
# create_regions picks. A unit no civilization can train still needs a name here.
for unit in Age2UnitData:
    location_name_list.append(unit.location_name)
    location_name_to_id[unit.location_name] = unit.id
    location_id_to_name[unit.id] = unit.location_name

for line in Age2UnitLineData:
    location_name_list.append(line.location_name)
    location_name_to_id[line.location_name] = line.id
    location_id_to_name[line.id] = line.location_name

for job in Age2VillagerJobData:
    location_name_list.append(job.location_name)
    location_name_to_id[job.location_name] = job.id
    location_id_to_name[job.id] = job.location_name

for hero in Age2HeroData:
    location_name_list.append(hero.location_name)
    location_name_to_id[hero.location_name] = hero.id
    location_id_to_name[hero.id] = hero.location_name

assert len(location_name_to_id) == len(location_name_list), "duplicate location name"
