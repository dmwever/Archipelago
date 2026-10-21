# 07: Own Shepherd is in logic where no scenario with villagers has sheep

**Reported:** 2026-10-19, playtesting

**Status:** needs-triage

## Report

Own Shepherd is in logic even though the only scenario that currently has villagers has no sheep.

## Audit (from code)

The global rule is `UnitLogic.can_do_job_anywhere` (`logic/unit_logic.py`): an Or over scenarios of
`is_unlocked() & scenario.units.can_do_job(job)`, and the profession item.

`ScenarioUnitLogic.can_do_job` (`logic/scenarios/ScenarioUnitLogic.py:130-139`) is
`job_available(job) & job_requirement(job)`:

- `job_available` comes from `ScenarioStartingState.job_available` (`logic/ScenarioLogic.py:35`),
  which defaults to `True_()` for every job. No scenario overrides it.
- `job_requirement` returns `True_()` for every job except Builder, because `job.building` is
  always `None` (`locations/VillagerJobs.py:19`). So the building branch never runs.

So every Own <Job> location except Builder resolves to "some unlocked scenario + the profession
item". It asks neither for villagers (`has_vils`) nor for the resource.

The resource knowledge exists but logic doesn't use it:

- `locations/connections/VillagerJobResources.py` `JOB_TO_SCENARIOS` lists which scenarios have
  sheep, hunt, berries, gold or stone. It is read only by `UnitPool.job_possible`, which decides
  whether the location exists at all.
- `ScenarioResourceLogic._herd` (`logic/scenarios/ScenarioResourceLogic.py:129-134`) already has
  the right shape for herding: `herd_count`, a food dropsite, `has_vils`, and `starting_sheep`.

Same gap for Hunter, Forager, Gold Miner and Stone Miner (resource-limited per `JOB_TO_SCENARIOS`).
Lumberjack, Farmer, Fisherman, Repairer and Herder also never ask for villagers, so they too are in
logic from any unlocked scenario.

## Likely shape of a fix

Make `can_do_job` ask for `has_vils()`, plus a per-job resource condition: either reuse the
economy questions (`can_herd`, `can_hunt`, `can_forage`, ...) or gate on `JOB_TO_SCENARIOS`.
