# age2de benchmark

Measure each code version **once**, store its results, compare against what is stored. Never re-run
an old version to get a baseline.

The fixed seed set is the 100 YAMLs in `../fuzz_output_genghis_3b3762449/yamls/` (full shuffle, all
three campaigns; see `../_full_shuffle.yaml`). Always run at `-j 6`. This is a laptop and it may
sleep mid-run: if it did, ignore that run's times (spheres, sphere 1 and order sizes are still
valid).

**Two corpora, two lineages.** `fuzz_output_6f09d7ec6` holds the older set, fuzzed with Genghis Khan
held out. A run on one is **not** comparable with a run on the other, so a stored run's baseline has
to come from its own set. The Genghis set replaced it after #30, whose gate came out flat on all 100
of the old seeds for a structural reason: Genghis 4 is the one scenario with a standing Mining Camp
and Monastery, and the old set could never generate it. Rows below say which set each run used.

From `worlds/age2de/fuzz/bench/`:

    # 1. Measure the current checkout on the fixed seeds. Resumable: rerun to finish a stopped run.
    python replay.py ../../../.. ../fuzz_output_genghis_3b3762449/yamls ../fuzz_output_genghis_3b3762449/replay_<commit>.jsonl 6

    # 2. Compare against any stored run.
    python compare.py ../fuzz_output_genghis_3b3762449/replay_<old>.jsonl ../fuzz_output_genghis_3b3762449/replay_<new>.jsonl ../fuzz_output_genghis_3b3762449/timings.jsonl

**Measuring an old commit in a worktree: copy `host.yaml` in first.**

    cp host.yaml <worktree>/host.yaml     # before the first replay against it

`host.yaml` is gitignored, so a fresh worktree has none, and at `-j 6` all six jobs race to create
it through the same `host.yaml.tmp`. The losers die with `PermissionError [WinError 32]` or
`FileNotFoundError [WinError 2]` on that path and are recorded as `ok: false`. They are harness
contention, not fill failures, and they will read as a baseline that the branch then "fixes" - five
of them did exactly that on the first #30 Genghis baseline. The main checkout never shows this
because it has had a `host.yaml` for ages. Resume skips by seed whatever its `ok`, so drop the bad
rows before rerunning.

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
| `replay_issue30-standing-camp-free.jsonl` | #30, commit `11c1dd008` | 100/100 ok - the #30 fill gate, against `replay_issue28-joan4-french-camp`. **Spheres and sphere 1 identical on all 100 seeds**, which is expected: this seed set excludes Genghis Khan, and in each of the other four scenarios with a standing camp the Town Center is standing behind the same rule, so its free dropsite route already covered those resources. The ticket's loosening is real but invisible to this corpus - which is what prompted the Genghis set below. **Times not comparable** - the baseline's are void, and the 22.0s -> 19.4s median (96 of 100 down) is that contention lifting, not this branch running faster. |
| `replay_3b376244.jsonl` | commit `3b376244` | 100/100 ok - the #26 baseline, measured in a detached worktree. **Times void** - ran alongside a recapture and pytest. |
| `replay_issue26-dock-guards.jsonl` | #26, on top of `3b376244` | 100/100 ok - the #26 fill gate, against `replay_3b376244`. **Times void** - ran alongside pytest. Spheres and sphere 1 identical on all 100. |

Runs on the **Genghis** set, `fuzz_output_genghis_3b3762449/` - a separate lineage, never compared
against the rows above:

| file | code | notes |
| --- | --- | --- |
| `replay_cd39b473f-genghis.jsonl` | commit `cd39b473f` | 100/100 ok - the base of the Genghis set, measured in a detached worktree so the set has a baseline predating #30. First attempt scored 95/100; those 5 were the `host.yaml` race described above, dropped and rerun. |
| `replay_issue30-genghis.jsonl` | #30, commit `11c1dd008` | 100/100 ok - the #30 fill gate rerun on the Genghis set, against `replay_cd39b473f-genghis`. Unlike the old set, this one moves: spheres 93 of 100 unchanged (5 up, 2 down), sphere 1 94 unchanged (3 up, 3 down). **Slower on 93 of 100 seeds** (24.8s -> 29.6s median), which 53 -> 66 routes per scenario through the same fixpoint would explain; the baseline ran while the laptop was busy, so if anything that understates it. |

A new seed set (new fuzz run) uses `timing_hook.py` with `../fuzz.py`, which saves every YAML for
reuse; `summarize.py` reads that run's `timings.jsonl`:

    PYTHONPATH="../../../..;.;.." python ../fuzz.py -r 100 -j 6 -g age2de -n 1 -m ../_full_shuffle.yaml -t 90 --skip-output --hook timing_hook:Hook
