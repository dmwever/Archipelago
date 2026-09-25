from ..Buildings import Age2BuildingData
from ..VillagerJobs import Age2VillagerJobData


JOB_TO_BUILDING: dict[str, Age2BuildingData] = {
    "Farmer": Age2BuildingData.FARM,
    "Herder": Age2BuildingData.PASTURE,
}


for _job in Age2VillagerJobData:
    _job.building = JOB_TO_BUILDING.get(_job.job_name)


assert not [name for name in JOB_TO_BUILDING
            if name not in [job.job_name for job in Age2VillagerJobData]], \
    "a job requirement naming a job that does not exist"
