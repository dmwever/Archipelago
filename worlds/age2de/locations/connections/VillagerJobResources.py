from ..Scenarios import Age2ScenarioData as S
from ..VillagerJobs import Age2VillagerJobData


ATTILA = (S.AP_ATTILA_1, S.AP_ATTILA_2, S.AP_ATTILA_3, S.AP_ATTILA_4, S.AP_ATTILA_5, S.AP_ATTILA_6)

JOB_TO_SCENARIOS: dict[str, frozenset] = {
    "Oyster Gatherer": frozenset(),
    "Shepherd": frozenset({S.AP_ATTILA_3, S.AP_ATTILA_4, S.AP_ATTILA_5, S.AP_ATTILA_6,
                           S.AP_JOAN_2, S.AP_JOAN_3, S.AP_JOAN_4}),
    "Hunter": frozenset(ATTILA) | frozenset({S.AP_JOAN_1, S.AP_JOAN_2, S.AP_JOAN_3}),
    "Forager": frozenset(ATTILA) | frozenset({S.AP_JOAN_2, S.AP_JOAN_3, S.AP_JOAN_4, S.AP_JOAN_6}),
    "Gold Miner": frozenset(ATTILA) | frozenset({S.AP_JOAN_2, S.AP_JOAN_3, S.AP_JOAN_4,
                                                 S.AP_JOAN_5, S.AP_JOAN_6}),
    "Stone Miner": frozenset(ATTILA) | frozenset({S.AP_JOAN_2, S.AP_JOAN_3, S.AP_JOAN_4,
                                                  S.AP_JOAN_5, S.AP_JOAN_6}),
}


assert not [name for name in JOB_TO_SCENARIOS
            if name not in [job.job_name for job in Age2VillagerJobData]],     "a job resource naming a job that does not exist"
