# age2de benchmark

Measure each code version **once**, store its results, compare against what is stored. Never re-run
an old version to get a baseline.

The fixed seed set is the 100 YAMLs in `../fuzz_output_6f09d7ec6/yamls/` (full shuffle, no Genghis
Khan; see `../_full_shuffle.yaml`). Always run at `-j 6`. This is a laptop and it may sleep mid-run: if it did, ignore that run's
times (spheres, sphere 1 and order sizes are still valid).

From `worlds/age2de/fuzz/bench/`:

    # 1. Measure the current checkout on the fixed seeds. Resumable: rerun to finish a stopped run.
    python replay.py ../../../.. ../fuzz_output_6f09d7ec6/yamls ../fuzz_output_6f09d7ec6/replay_<commit>.jsonl 6

    # 2. Compare against any stored run.
    python compare.py ../fuzz_output_6f09d7ec6/replay_<old>.jsonl ../fuzz_output_6f09d7ec6/replay_<new>.jsonl ../fuzz_output_6f09d7ec6/timings.jsonl

Each result row: seed, ok, seconds, spheres, sphere0/sphere1 sizes, order_kept/order_pruned.

## The fill gate

A playtest ticket that changes the logic asks for a **fill gate**: the failure count must not rise.
Run it here, not from a path copied into the ticket.

1. **Before** is a stored run, not a fresh one. Pick the newest row below whose code predates your
   change; if none does, measure the base commit once and store it, which is step 3 for the next
   person.
2. **After** is this checkout, measured the same way: `replay.py` as above, written to
   `replay_<commit-or-branch>.jsonl` beside the others.
3. **Commit the `.jsonl`.** A run nobody stores is a run the next ticket has to repeat, which is
   how the discipline at the top of this file lapses.
4. Compare with `compare.py`. **The failure count must not rise.** If it does, stop: record which
   seeds newly fail and the fill error, and hand back. Do not loosen a rule to make the fill pass.
5. Report `ok` counts always; report times only if the laptop stayed awake for both runs.
   Rows in runs stored before 2026-10-26 carry
   `AttributeError: 'ScenarioLogic' object has no attribute 'budget'` in their `error` field even
   where `ok` is true: `replay_one.py` collected a metric off the since-removed budget, and the
   generation had already succeeded. Read `ok`. Those runs also lack `order_kept` / `order_pruned`,
   which `compare.py` now reports as "not recorded on both sides" rather than dying on.

Tickets #05, #17, #18, #19 and #22 record this gate against 63 generations in
`fuzz_output_lock_items/error/age2de/`. Those runs happened; the directory did not survive, because
the whole of `fuzz_output_*` was gitignored then. It no longer is: `fuzz/.gitignore` now tracks
every `replay_*.jsonl`, `timings*.jsonl` and `report.json` stored under one, so step 3 above is a
real commit. The fixed seed set in `yamls/` is tracked too, so a stored run can always be
reproduced and compared against from a fresh clone; everything else a run drops stays ignored.
Their records stand, and the 100 seeds here are what to use now.

## Stored runs

| file | code | notes |
| --- | --- | --- |
| `replay_c6ca31822.jsonl` | commit `c6ca31822` | |
| `replay_issue07-job-resource.jsonl` | branch | |
| `replay_per-resource-wip.jsonl` | branch | |
| `replay_per-resource-items-wip.jsonl` | branch | |
| `replay_b9dd362.jsonl` | commit `b9dd362` | 100/100 ok. **Times void** - the laptop slept, and it ran at `-j 4`. Logic results stand. |
| `replay_issue23-defence-pays.jsonl` | #23, on top of `39d7c603` | 100/100 ok - the #23 fill gate, against `b9dd362`. **Times void** - the machine was shared. |
| `replay_issue29-army-open-ground.jsonl` | #29, on top of `3c0136c3` | 100/100 ok - the #29 fill gate, against `replay_issue23-defence-pays`. **Times void** - the machine was shared; for the record the branch was slower on 91 of 100 seeds (13.6s -> 17.4s median), which one more Or'd term on every open-ground question would explain. Spheres flat, 79 of 100 unchanged. |
| `replay_issue24-seed-items.jsonl` | #24, on top of `e7547828` with the Dock fallback uncommitted | 100/100 ok - the #24 fill gate, against `replay_issue29-army-open-ground`. Times recorded (4.2s median) but not comparable: the baseline's are void. Sphere 1 median 7.5 -> 6, mean flat at 9.2; spheres 25 -> 26 median. |
| `replay_issue28-joan4-french-camp.jsonl` | #28, on top of `5e262a4db` | 100/100 ok - the #28 fill gate, against `replay_issue24-seed-items`. **Times void** - the replay ran alongside two pytest batches on the same laptop, so the 4.2s -> 22.0s median is contention, not the branch. Spheres 99 of 100 unchanged (1 up); sphere 1 identical on all 100. |
| `replay_3b376244.jsonl` | commit `3b376244` | 100/100 ok - the #26 baseline, measured in a detached worktree. **Times void** - ran alongside a recapture and pytest. |
| `replay_issue26-dock-guards.jsonl` | #26, on top of `3b376244` | 100/100 ok - the #26 fill gate, against `replay_3b376244`. **Times void** - ran alongside pytest. Spheres and sphere 1 identical on all 100. |

A new seed set (new fuzz run) uses `timing_hook.py` with `../fuzz.py`, which saves every YAML for
reuse; `summarize.py` reads that run's `timings.jsonl`:

    PYTHONPATH="../../../..;.;.." python ../fuzz.py -r 100 -j 6 -g age2de -n 1 -m ../_full_shuffle.yaml -t 90 --skip-output --hook timing_hook:Hook
