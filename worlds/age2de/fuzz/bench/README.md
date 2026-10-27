# age2de benchmark

Measure each code version **once**, store its results, compare against what is stored. Never re-run
an old version to get a baseline.

The fixed seed set is the 100 YAMLs in `../fuzz_output_3b3762449/yamls/` (full shuffle, all
three campaigns; see `../_full_shuffle.yaml`). Always run at `-j 6`. This is a laptop and it may
sleep mid-run: if it did, ignore that run's times (spheres, sphere 1 and order sizes are still
valid).

**Changing the seed set retires every run stored against it.** A run is only comparable with runs
on the same seeds, so a new set starts the table from nothing and needs its own baseline measured
before anything can be gated against it. Do it rarely, and only when the set cannot see something
it has to: #30 is the case that forced this one, and `## Retired sets` below records what went.

From `worlds/age2de/fuzz/bench/`:

    # 1. Measure the current checkout on the fixed seeds. Resumable: rerun to finish a stopped run.
    python replay.py ../../../.. ../fuzz_output_3b3762449/yamls ../fuzz_output_3b3762449/replay_<commit>.jsonl 6

    # 2. Compare against any stored run.
    python compare.py ../fuzz_output_3b3762449/replay_<old>.jsonl ../fuzz_output_3b3762449/replay_<new>.jsonl ../fuzz_output_3b3762449/timings.jsonl

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

## Stored runs

All on the current set, `../fuzz_output_3b3762449/yamls/`.

| file | code | notes |
| --- | --- | --- |
| `replay_cd39b473f.jsonl` | commit `cd39b473f` | 100/100 ok - the set's baseline, the parent of #30, measured in a detached worktree. First attempt scored 95/100; those 5 were the `host.yaml` race described above, dropped and rerun. |
| `replay_issue30-standing-camp-free.jsonl` | #30, commit `11c1dd008` | 100/100 ok - the #30 fill gate, against `replay_cd39b473f`. Spheres 93 of 100 unchanged (5 up, 2 down), sphere 1 94 unchanged (3 up, 3 down). **Slower on 93 of 100 seeds** (24.8s -> 29.6s median), which 53 -> 66 routes per scenario through the same fixpoint would explain; the baseline ran while the laptop was busy, so if anything that understates it. |

## Retired sets

A retired set is one nothing new should be gated against: its runs are only comparable with each
other. Kept on disk where its runs still back an open ticket, in git history otherwise. What is
worth keeping either way is why it went.

- **`fuzz_output_6f09d7ec6_enemy_trade`** - 100 seeds, full shuffle, **Genghis Khan held out** so
  that runs compared like with like. Carried the gates for #23, #24, #26, #28, #29 and #30's first
  pass, all 100/100 ok. Retired 2026-10-26: holding Genghis out meant Genghis 4 never generated,
  and #30 - which frees a standing Mining Camp and Monastery, both of them Genghis 4's - came out
  flat on all 100 seeds. A gate blind to the scenario a ticket touches is not a gate. Kept rather
  than dropped, under its enemy-trade name, because `replay_3b376244.jsonl` and
  `replay_issue26-dock-guards.jsonl` are #26's gate and #27 still leans on that work. Do not
  baseline new work against it.
- **`fuzz_output_lock_items`** - 63 generations behind the gates for #05, #17, #18, #19 and #22.
  Not retired on purpose: the whole of `fuzz_output_*` was gitignored then, so it was never
  committed and did not survive. That is what `fuzz/.gitignore` now prevents, tracking every
  `replay_*.jsonl`, `timings*.jsonl`, `report.json` and the `yamls/` a run was measured on, so a
  retired set is recoverable rather than lost.

A new seed set (new fuzz run) uses `timing_hook.py` with `../fuzz.py`, which saves every YAML for
reuse; `summarize.py` reads that run's `timings.jsonl`:

    PYTHONPATH="../../../..;.;.." python ../fuzz.py -r 100 -j 6 -g age2de -n 1 -m ../_full_shuffle.yaml -t 90 --skip-output --hook timing_hook:Hook
