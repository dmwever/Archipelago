from ..Scenarios import Age2ScenarioData
from ..VillagerJobs import Age2VillagerJobData
from .ScenarioResources import Tier

S = Age2ScenarioData   # the table below is a wall of these


ANY_TIER: tuple[Tier, ...] = tuple(Tier)

BASE_OR_OPEN: tuple[Tier, ...] = (Tier.BASE, Tier.OPEN)

JOB_TO_RESOURCE: dict[str, tuple[str, tuple[Tier, ...]]] = {
    "Shepherd": ("herd_count", BASE_OR_OPEN),
    "Hunter": ("hunt_count", ANY_TIER),
    "Forager": ("bush_count", ANY_TIER),
    "Gold Miner": ("gold_count", ANY_TIER),
    "Stone Miner": ("stone_count", ANY_TIER),
    "Fisherman": ("shore_fish_count", ANY_TIER),
    "Oyster Gatherer": ("oyster_count", ANY_TIER),
}


def scenario_has_job_resource(scenario: Age2ScenarioData,
                              job: Age2VillagerJobData) -> bool:
    if scenario.fixed_force:
        return False
    wanted = JOB_TO_RESOURCE.get(job.job_name)
    if wanted is None:
        return True
    field, tiers = wanted
    return any(getattr(scenario.resources[tier], field) for tier in tiers)


ATTILA = frozenset({S.AP_ATTILA_1, S.AP_ATTILA_2, S.AP_ATTILA_3,
                    S.AP_ATTILA_4, S.AP_ATTILA_5, S.AP_ATTILA_6})
JOAN = frozenset({S.AP_JOAN_2, S.AP_JOAN_3, S.AP_JOAN_4, S.AP_JOAN_6})
GENGHIS = frozenset({S.AP_GENGHIS_2, S.AP_GENGHIS_3, S.AP_GENGHIS_4,
                     S.AP_GENGHIS_5, S.AP_GENGHIS_6})
EVERY_SCENARIO = ATTILA | JOAN | GENGHIS
"""Joan 1 and 5 and Genghis 1 are fixed forces and belong to none of these."""

JOB_TO_SCENARIOS: dict[str, frozenset] = {
    "Oyster Gatherer": frozenset(),
    "Shepherd": frozenset({S.AP_ATTILA_3, S.AP_ATTILA_4, S.AP_ATTILA_5, S.AP_ATTILA_6,
                           S.AP_JOAN_3, S.AP_JOAN_4,
                           S.AP_GENGHIS_2, S.AP_GENGHIS_3, S.AP_GENGHIS_4, S.AP_GENGHIS_6}),
    "Hunter": ATTILA | frozenset({S.AP_JOAN_2, S.AP_JOAN_3}) | GENGHIS,
    "Forager": ATTILA | JOAN | (GENGHIS - frozenset({S.AP_GENGHIS_5})),
    "Gold Miner": EVERY_SCENARIO,
    "Stone Miner": EVERY_SCENARIO,
    "Fisherman": EVERY_SCENARIO,
}


assert not [name for name in JOB_TO_SCENARIOS
            if name not in [job.job_name for job in Age2VillagerJobData]],     "a job resource naming a job that does not exist"
