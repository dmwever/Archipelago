# 20: Retire the `starting_*` resource flags in favour of the scan

**Reported:** 2026-10-22, split off from [#07](07-own-shepherd-without-sheep.md) during triage

**Status:** needs-triage

## Report

The `starting_*` flags on `ScenarioStartingState` say by hand whether a scenario has a resource. The
scenario resource scan now holds the same fact as counts, so there are two sources for one fact.
`JOB_TO_SCENARIOS` shows how that goes: it drifted from the scan on most jobs.

## Audit (from code)

- Fields: `starting_gold_mine`, `starting_stone_mine`, `starting_trees`, `starting_bushes`,
  `starting_hunting`, `starting_fish`, `starting_sheep`, `starting_relics` default to `True_()`;
  `starting_oysters` and `starting_whales` default to `False_()`.
- No scenario's starting state overrides any of them. Every scenario uses the defaults.
- Only the economy (`ScenarioResourceLogic`) reads them, each ANDed beside the matching scan count
  (e.g. `_herd`: `herd_count` and `starting_sheep`). The `True_` ones do nothing; the two `False_`
  ones switch oyster and whale gathering off everywhere, whatever the scan says.
- The job rule from #07 deliberately does not read them.

## Open

- Are oysters and whales off on purpose (unscanned, untested), or should the scan decide them too?
- Trees and relics: does the scan count them? If not, what replaces the flag?

## Comments
