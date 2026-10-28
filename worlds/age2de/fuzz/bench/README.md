# age2de benchmark

Measure each code version **once**, store its results, compare against what is stored. Never re-run
an old version to get a baseline.

The fixed seed set is the 100 YAMLs in `../fuzz_output_3b3762449/yamls/` (full shuffle, all
three campaigns; see `../_full_shuffle.yaml`). It rolls `partner_trade` too - 34 seeds `none`, 38
`allies`, 28 `allies_and_enemies` - so a trade ruling needs no separate set. Always run at `-j 6`. This is a laptop and it may
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
| `replay_d311c37f7.jsonl` | commit `d311c37f7` | 100/100 ok - the #27 baseline, measured in a detached worktree. `replay_issue30-standing-camp-free` was not usable: #26's dock rulings (`223061da3`) and `d311c37f7` both land between it and #27. |
| `replay_issue27-market-guards.jsonl` | #27, on `d311c37f7` | 100/100 ok - the #27 fill gate, against `replay_d311c37f7`. **Spheres and sphere 1 identical on all 100 seeds.** Times void: the run shared the laptop with the pre-commit test subset, which reads as all 100 seeds slower (32.1s -> 45.8s median) with every fill unchanged. |
| `replay_45bd16a3e.jsonl` | commit `45bd16a3e` | 100/100 ok - the #38 baseline, measured in a detached worktree with `host.yaml` copied in. Logic unchanged by `85f476ec`..`f963fcfa` (tickets only). Times void: the run shared the laptop with the pre-commit test subset. |
| `replay_issue42-paid-advance.jsonl` | #42 with #38, on `81a33fe0` (uncommitted) | 100/100 ok - the #42 fill gate (#38's work in the tree), against `replay_45bd16a3e`. Spheres 42 up, 31 down, 27 same; sphere 1 10 up, 30 down, 60 same (biggest drop 493843265, 29 -> 12). Times void: the run shared the laptop with test runs and two review agents. Even so, **slower on all 100 seeds** (8.8s -> 21.6s median), too uniform to be only contention, so remeasure on an idle laptop. |
| `replay_issue42-paid-advance-idle.jsonl` | #42 with #38, after #42's dead-code cuts (uncommitted) | 100/100 ok - the idle remeasure. Spheres and sphere 1 **identical on all 100 seeds** to `replay_issue42-paid-advance`, so the cuts changed no logic. Laptop idle, so times valid: **8.8s -> 15.9s median, 8.4s -> 22.6s mean against `replay_45bd16a3e`, slower on all 100 seeds**. That baseline's own times are void (shared laptop), which can only flatter it, so the real slowdown is at least this. |
| `replay_issue42-questions.jsonl` | #42 with #38, `has_building` and `can_advance` as scenario questions (uncommitted) | 100/100 ok - **#42's fill gate of record**, against `replay_45bd16a3e`. Spheres and sphere 1 identical on all 100 seeds to `replay_issue42-paid-advance-idle`, so the questions changed no logic. Laptop idle: **8.8s -> 7.3s median, 8.4s -> 7.2s mean, faster on 90 of 100 seeds**. The slowdown above was #38's (seed 448174193: 13.7s at `45bd16a3e`, 67.5s at `81a33fe0`): `has_building`, rebuilt as a `Named` on every call, ran 505k times in `set_rules`. |
| `replay_issue39-economy-capital.jsonl` | #39, on `05e6c1ba5` with the route wiring uncommitted | 100/100 ok - #39's fill gate, against `replay_issue42-questions`. Spheres 33 up, 44 down, 23 same; sphere 1 37 up, 27 down, 36 same (biggest drop 819534951, 60 -> 17). **Times void**: every seed read about 4.5x slower (7.3s -> 33.1s median), but the machine itself ran about 2x slower than when the baseline was stored. Back to back, single seeds, on the same machine against `f61e8ef66` (the commit before #39): 907521578 3.2s -> 3.55s, 972021640 12.6s -> 14.4s, so #39 costs about 10-15%. |
| `replay_issue40-second-tc.jsonl` | #40, on `b53b749ec` (uncommitted) | 100/100 ok - #40's fill gate, against `replay_issue39-economy-capital`. Spheres 31 up, 38 down, 31 same; sphere 1 17 up, 14 down, 69 same (biggest drop 96525717, 13 -> 4). **Times void**: the baseline's own times are void (see its row), so 33.1s -> 10.6s median says nothing about #40. |
| `replay_issue47-town-center-paid.jsonl` | #47, on `203cb8a80` (uncommitted) | 100/100 ok - #47's fill gate, against `replay_issue40-second-tc`. Spheres 5 up, 1 down, 94 same; sphere 1 1 up, 6 down, 93 same (biggest drop 79223273, 8 -> 6). Times void: the run shared the laptop with the pre-commit test subset and two review agents. |

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
