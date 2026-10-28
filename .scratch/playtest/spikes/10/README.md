# 10: test harness

Harness for the acceptance criteria of [#10](../../issues/10-caveman-sweep-delayed.md), on the
`XsTesting` setup from #33 and #35.

Three runs, grouped by setup. **Run A** is built; B and C follow.

## Run A — caveman timing

Covers acceptance criteria 1-6 and 11.

**Script:** `Test.xs` in the Ageipelago xs folder (gitignored), run by `XsTesting.aoe2scenario`.
It does not go through `InitAP`, so no client and no seeded scenario are needed: it calls
`initializeStructsScript()`, `InitLocations()`, `InitUnitsanity()`, `InitCaveman()`,
`InitProfessions()` and sets `startupGranted = 1` itself, then drives the real
`UnitsanityChecks` rule.

The installed seed supplies the options it needs: `AP_US_MODE = 2`, `AP_US_CAVEMAN = 1`,
`AP_US_VILLAGER = 2`, 107 unit rows. No item is granted at boot, so every unit row starts locked
and every non-exempt unit cavemanifies to Militia.

**Run:** start `XsTesting` at any speed and leave it alone. The chat shows the boot line and
then one line at the end. When it says *run A done, file closed*, quit the scenario so the file
flushes. Copy `profile/default1.xsdat` to `spikes/10/runA.xsdat`. It takes about 50 game seconds.

**Decode:** `python decode.py runA.xsdat` — it runs `kit xsdat decode` with `ledgerA.json` and
prints the timeline. The ledger is 8005 fixed assertions; all of them passing means the file is
structurally whole and the footer is present.

### What it does, by game second

| Second | Stage | What happens |
| --- | --- | --- |
| 1, 2 | boot probe | creates a P1 Villager, so a failed `xsCreateUnit` shows up before anything depends on it |
| 5 | S1 create | creates a P2 Knight (38) |
| 6 | S1 convert | `xsSetUnitOwner` hands it to P1 — the converted Knight of the report |
| 11 | S2 create | creates a P2 Spearman (93) |
| 12 | S2 convert | hands it to P1; the harness then waits for its cavemanify |
| — | S2 item | on the tick **after** that cavemanify, `UnlockUnitItem(300)` unlocks the Archer row, which forces a full pass |
| 1-26 | S3 muster | creates 2 P1 Villagers a second from second 18 to 26, so the unit count moves every second the way a pavilion muster does |
| 20, 21 | S3 convert | creates a P2 Scout (448) and hands it to P1 in the middle of that |
| 28, 29 | S4 net zero | creates a P2 Skirmisher (7), then in one tick hands it to P1 **and** removes a Villager, so the total count does not move |
| 34 | S5 immunity | creates a P1 Mangonel (280) and calls `MarkUnitCavemanImmune`, the pavilion route's protection |
| 41 | S6 clear | sets the Militia row's `owned` back to 0 |
| 42 | S6 research | `xsResearchTechnology(22, true, true, 1)` — a full pass should re-own the row |
| 47 | flush | writes the file and disables itself |

### How to read the output

- **WATCH** lines are written only when something about a watched unit changes: its object id,
  its caveman ledger entry, or its exists / listed / untracked state. The tick number is the
  harness's own `highFrequency` tick counter.
  - `original=-1` means the ledger has no row for it. `original=0` is `CAVEMAN_REMOVED`, which is
    what `transformUnit` writes — **that is the cavemanify**, and its tick is the measurement.
  - A removed unit keeps reading `exists` and `listed` with its old object id for about 2 s
    (#35), so do not read the object id as the signal.
- **ROW** lines are written when a unit row's `owned` flag or its location's sent flag changes.
  The Knight row (38, location 312) going owned at any point is a **failure** of criterion 3.
- **RATE** lines carry the number of harness ticks in the previous game second, which is the
  clock everything else is measured against.

### Pass conditions

| Criterion | Pass |
| --- | --- |
| 1, busy ticks | S3's Scout reaches `original=0` within one game second of its convert event |
| 2, net zero | S4's Skirmisher reaches `original=0` within one game second of its convert event |
| 3, converted Knight | the Knight row never appears in a ROW line with `owned=1`; the Militia row does, within 2 s |
| 4, item after cavemanify | the Spearman row never goes owned, including after the EVENT item line |
| 5, item climb-back | the Archer row unlocks without disturbing the rows above |
| 6, research full pass | the Militia row goes back to `owned=1` after the EVENT research line |
| 11, mercenary immunity | the Mangonel never reaches `original=0`, and the Mangonel row goes owned |

### Known limits

- Rule order within a tick is not guaranteed. `AP10Harness` is declared after the include of
  `AP.xs`, so it should run after `UnitsanityChecks`, but every tick figure carries ±1 tick.
- The harness converts with `xsSetUnitOwner` rather than a Monk. #35 measured both landing at the
  same sorted place in the list, so they are the same case for this rule.
- A real pavilion muster is not simulated; S3 reproduces only its effect on the unit count.
  Criterion 1's wording names the muster, so it still wants a live check.

## Run A results

> From one in-game run on 2026-10-27 (`runA.xsdat`, 8005 of 8005 ledger checks, footer present,
> 142 records). Game speed left at the scenario default; 35.3 harness ticks per game second on
> average (18 to 49), so one tick is about 28 ms of game time.

**Every unit was cavemanified on the tick after it joined P1, in all three cases, and no unit
ever sent the location of what it used to be.**

| Stage | Event | Cavemanified | Location checked |
| --- | --- | --- | --- |
| S1 converted Knight, quiet map | convert at tick 175 | tick 176 (+1, ~28 ms) | Militia row at tick 177 (+2, ~56 ms) |
| S3 converted Scout, count moving | convert at tick 668 | tick 669 (+1) | — (row went owned through the Militia) |
| S4 converted Skirmisher, net zero | convert at tick 929 | tick 930 (+1) | — |
| S5 immune Mangonel | created at tick 1129 | never, over 13 s | Mangonel row at tick 1130 (+1) |

- **Criterion 2, net zero, is directly confirmed.** At second 29 the harness converted the
  Skirmisher and removed an anchor Villager in the same tick. `p1Units` reads 29 at second 28,
  29 and 30 — the total never moved — and the Skirmisher was still cavemanified on the next tick.
  This is the case the old rule never noticed at all.
- **Criterion 3 is confirmed with room to spare.** The Knight row never appears in a ROW line
  after its baseline, so it never went owned and location 312 was never sent. The Militia row
  went owned 2 ticks (~56 ms) after the convert, against a 2 s budget.
- **Criterion 4 is confirmed.** The harness fired `UnlockUnitItem(300)` at tick 360, exactly one
  tick after the Spearman's cavemanify at tick 359. The Spearman row never went owned, so the
  full pass that item triggered did not check the removed unit.
- **Criterion 6 is confirmed, with a negative control.** The Militia row was cleared at tick 1407
  and stayed at `owned=0` for 40 ticks of ordinary play — proof the normal per-tick pass really
  does look only at new units. The research at tick 1448 put it back to `owned=1` on tick 1449.
- **Criterion 11 is confirmed for the mechanism.** `MarkUnitCavemanImmune` is what
  `MercenarySpawn.xs:77` calls. The Mangonel never entered the caveman ledger (`original=-1`
  throughout) and still had its own location checked one tick after arrival.

### Incidental measurements

- **A removed unit drops out faster than #35 recorded.** The cavemanified originals read
  `gone/unlisted` 2 to 3 ticks (~60 to 85 ms) after `xsRemoveUnit`, not the "still there on the
  next tick, gone by 2 s" of #35's once-a-second sampling. Both are consistent; this run just has
  28 ms resolution. It means the untracked list holds an id for only a few ticks, so the 256 cap
  is in no danger at this scale.
- **Buildings are in P1's list**, as #35 found: `p1Units` reads 5 before the harness creates
  anything, and the Villager row only goes owned one tick after the first anchor Villager.

### Not covered by run A

- **Criterion 5, item climb-back, was not exercised.** The harness grants item 300 to force a
  full pass, but P1 owns no unit of the Archer line, so nothing had to climb. Needs a stage that
  cavemanifies a unit of a line, then grants that line's item and watches it come back up.
- Criterion 1 names a real pavilion muster. S3 reproduces only its effect on the unit count
  (2 Villagers a second, `p1Units` 10 to 29), which the rule handled.

## Run B — professions, and the climb-back

Covers acceptance criteria 5, 8, 9 and 10. Criterion 5 is folded in here because run A granted
an item for a line P1 owned nothing of, so nothing had to climb.

Same `Test.xs` slot, same decode path: `python decode.py runB.xsdat B`, against `ledgerB.json`.
The run A harness is kept beside it as `TestA.xs` so either can be put back.

The boot is wider than run A's: it mirrors `InitAP`'s order with `InitBuildsanity()`,
`InitAges()` and `InitTechsanity()` added, because the climb needs the tech table —
`technologyUnlocked` reads `TechItemReceived(upgradeItemId)` when techsanity is on, and this
seed has `AP_TS_MODE = 3`.

### What it does, by game second

| Second | Stage | What happens |
| --- | --- | --- |
| 1, 2 | anchors | two P1 Villagers, so the Villager row is owned before anything else |
| 5 | climb 0 | creates a P1 **Long Swordsman (77)**. Nothing is unlocked, so `cavemanTarget` finds no tier of line 815 available and falls back to Militia |
| 10 | climb 1 | `UnlockUnitItem(315)` unlocks rows 74, 75 and 77 — all three share that one item |
| 14 | climb 2 | `UnlockTech(73)` grants tech item 3673, the Man-at-Arms upgrade |
| 18 | climb 3 | `UnlockTech(63)` grants tech item 3663, the Long Swordsman upgrade |
| 28 | shepherd | creates a P2 **Shepherd (592)** |
| 29 | shepherd | hands it to P1 while the Shepherd profession is missing |
| 34-42 | gate | 2 Villagers a second plus a Militia created and removed each second — a busy stretch with no arrival in a locked villager job |
| 44 | held | `UnlockUnitItem(710)` grants the Shepherd profession |
| 46 | held | creates a P1 Shepherd, which should now survive |
| 52 | flush | writes the file |

### What each stage should show

- **Climb (criterion 5).** The COUNT line is the signal. Expected progression:
  `longSword 1` for one tick, then `militia 1` from second 5; still `militia 1` after the unit
  item at second 10, because 75 and 77 each need their upgrade tech; `manAtArms 1` after second
  14; `longSword 1` after second 18 — **and it stops there**, at the original unit, with nothing
  climbing past it for the remaining 30 seconds.
  - The step at second 10 is a deliberate negative: a unit item alone must not be enough.
- **Shepherd missing (criterion 8).** On the tick after the convert, the Shepherd should be gone
  and untracked, `shepherds` back to 0, `villagers` up by one. The Shepherd row (592,
  location 578) must **never** appear in a ROW line with `owned=1` — not on the arrival tick and
  not while the evicted unit is still listed.
- **The gate (criterion 10).** GATE lines are written only when
  `anyUnitWithLockedProfession` changes. Through seconds 34-42 it must stay `0`, which is what
  stops the rule calling `EvictProfessions` at all. A base Villager is tier 0, so it is not a
  profession type; only an arrival in a locked *job* opens the gate.
- **Shepherd held (criterion 9).** After second 44 the Shepherd row goes `locked=0`. The
  Shepherd created at second 46 should survive, and the row should go `owned=1` within the 2 s
  `PROFESSION_SWEEP_SECONDS` window — that path is `CheckProfessionLocations`, not
  `checkOwnedUnits`.

### Note on replaying run A

Run B's ROW record carries a `locked` flag in a field run A left at zero, so a run A file
decoded with the current script shows `locked=0` on every row. Ignore that column for run A.

## Run B results

> From one in-game run on 2026-10-27 (`runB.xsdat`, 8005 of 8005 ledger checks, footer present,
> 168 records). 6 to 11 harness ticks per game second — see *Tick rate* below before reading
> that as a regression.

**All four criteria pass.**

### Criterion 5, the climb-back

The Long Swordsman went down to Militia and back up in exactly the three steps the design
predicts, each on the tick after its item:

| Second | Granted | Counts after | Row marked owned |
| --- | --- | --- | --- |
| 5 | — | `longSword 1` for one tick, then `militia 1` | Militia, tick 39 |
| 10 | unit item 315 | **no change** — still `militia 1` | — |
| 14 | tech item 3673 | `manAtArms 1` by tick 109 | Man-at-Arms, tick 108 |
| 18 | tech item 3663 | `longSword 1` by tick 143 | Long Swordsman, tick 142 |

- **Second 10 is the load-bearing negative.** Unlocking rows 74, 75 and 77 with their shared unit
  item moved nothing, because `technologyUnlocked` still wanted 3673 and 3663. A jump straight
  back to Long Swordsman there would have meant the upgrade items were not being consulted.
- **It stopped at its original unit.** `longSword` stayed at 1 and `manAtArms` at 0 from second
  18 through second 52. Nothing climbed past where the unit started.
- Each intermediate form checked its own location as it passed through — Militia, then
  Man-at-Arms, then Long Swordsman. That is correct: P1 really did own each of them.

### Criterion 8, Shepherd with the profession missing

The P2 Shepherd was handed to P1 on tick 240. By tick 241 — the first sample after — it was
already **untracked**, and `villagers` had gone from 2 to 3. So `evictProfession` removed it and
put a base Villager in its place on the arrival tick itself. It read `gone/unlisted` by tick 243.

**The Shepherd row (592, location 578) never went owned.** It appears in exactly two ROW lines
in the whole run: `owned=0 locked=1` at second 0, and `owned=1 locked=0` at second 46, after the
profession item. Nothing in between, including the two ticks where the evicted unit was still
listed.

### Criterion 9, Shepherd with the profession held

After `UnlockUnitItem(710)` at second 44, the row went `locked=0`. The Shepherd created at
second 46 **survived** — tick 405 shows it `exists/listed` and not untracked — and the row went
`owned=1` on that same tick, against a 2 s budget. `shepherds` stayed at 1 through second 52.

Both paths cover this unit, not just the timer: 592 has a unit row, so `checkOwnedUnits` marks it
on the new-unit path as well as `CheckProfessionLocations` on its 2 s sweep.

### Criterion 10, the eviction gate

`anyUnitWithLockedProfession` was sampled on every one of 454 ticks and **changed value once**,
at tick 1, to 0. It never left 0.

That covers the busy stretch at seconds 34 to 42, where P1 went from 9 to 28 units with two
Villagers added and a Militia created and removed every second. A base Villager is tier 0, so it
is not a profession type; only an arrival in a locked job opens the gate. The rule therefore
never called `EvictProfessions` across that stretch.

The sample is taken over the **full** unit list, while the rule passes it only the new units, so
false over the full list is the stronger claim.

**One wrinkle worth recording:** the gate's one true moment, at second 29, is invisible here.
`UnitsanityChecks` runs before `AP10Harness` within a tick, so by the time the harness sampled,
`EvictProfessions` had already run and untracked the Shepherd — and
`anyUnitWithLockedProfession` skips untracked ids. The eviction itself is the evidence the gate
opened. This also settles the rule-order question run A left at ±1 tick: the mod's rule goes
first.

### Tick rate

Run B ran at 6 to 11 ticks per game second against run A's 18 to 49. **That is harness cost, not
the mod.** This harness adds five unallocated `xsGetPlayerUnitIds` calls per tick for the type
counts, plus `anyUnitWithLockedProfession` over the full list — the per-unit struct reads #33
measured as the expensive part. The rule under test still acted on the tick after every event.

Run C measures the mod's own cost with a minimal observer, by #33's method. Nothing in run B
should be read as a tick-rate result.

## Run C — caveman off, and the tick rate

Covers acceptance criteria 7 and 12. Both fit one run because `InitCaveman()` can be called
partway through: the boot deliberately **skips** it, so `cavemanReady` stays false and
`ApplyCaveman` returns immediately — that is caveman mode off, without reinstalling the seed.

`python decode.py runC.xsdat C`, against `ledgerC.json`. It prints the timeline and then a phase
table with the retained percentages.

Two rules this time, so the meter stays cheap:

- **`AP10Meter`** (`highFrequency`) only counts ticks, plus the churn and the row sampling when
  those modes are on. During the tick-rate phases both are off, so it is a bare counter.
- **`AP10Driver`** (once a second) does all the staging and writing.

Run B's harness cost 6-11 ticks a second because it sampled heavily every tick. This one must
not, or it measures itself instead of the rule.

### What it does, by game second

| Second | Stage | What happens |
| --- | --- | --- |
| 5-20 | criterion 7 | 3 Villagers created a second so the count moves, and every 2 seconds one probe unit of a fresh locked line — Knight, Spearman, Scout, Skirmisher, Mangonel, 128, 279, 281 |
| 22-28 | fill | 26 Villagers a second, to about 210 P1 units |
| 30 | caveman on | `InitCaveman()` — the probe units cavemanify here, in one burst |
| 32 | quiet | row sampling off, so the meter is a bare counter from here |
| 34-43 | baseline 1 | `UnitsanityChecks` **disabled**, idle |
| 44-53 | phase 2 | rule **enabled**, idle |
| 54-63 | baseline 3 | rule disabled, **churn on**: 2 Militia created and 2 removed every tick |
| 64-73 | phase 4 | rule enabled, churn on — this is "a fight" at about 210 units |
| 74-83 | baseline 5 | rule disabled, idle again, to show drift |
| 84-93 | phase 6 | rule enabled, idle again |
| 94 | flush | writes the file |

### What each half should show

- **Criterion 7, caveman off.** Each probe unit's row should go `owned` on the tick after its
  creation, while the unit count is moving every second. With nothing to cavemanify,
  `unitsTransformed` stays false, so `checkOwnedUnits` runs on the same tick the unit is found —
  no extra tick of delay. The ROW record carries the within-second tick index, and so does the
  create event, so the delta is readable directly.
- **Criterion 12, tick rate.** Each enabled phase is compared against the disabled baselines with
  the same churn setting. The pass is the rule not moving the rate outside the baselines' own
  spread. Watch the churn pair (3 against 4) in particular: that is the case the redesign
  actually added work to, because churn makes 2 new unit ids every tick.

### Known limits

- **The caveman ledger is nearly empty during the phases.** The churn units are Militia, whose
  caveman target is Militia, so nothing transforms and nothing is recorded. #33 measured the
  ledger scan as the dominant cost of the old full pass; under this design only new units search
  it, 2 a tick, so the ledger matters far less — but this run does not prove that at 200 entries.
  #33's table is still the reference for ledger cost.
- **The first second after each phase switch includes a catch-up tick.** While the rule is
  disabled `lastUnitScan` goes stale, so the tick it comes back sees every unit as new. That
  second is left in the numbers rather than trimmed; the min column shows it.

## Run C results

> From one in-game run on 2026-10-27 (`runC.xsdat`, 8005 of 8005 ledger checks, footer present,
> 246 records). The driver missed two seconds (48 and 91), so two windows have nine samples
> rather than ten.

### Criterion 7, caveman off — pass

All eight probe lines had their location checked **on the tick after the unit was created**,
while the unit count moved every second (3 Villagers a second, P1 climbing from 5 to about 60):

| Second | Probe | Row owned |
| --- | --- | --- |
| 5 | Knight 38 | tick 1 of that second |
| 8 | Spearman 93 | tick 1 |
| 10 | Scout 448 | tick 1 |
| 12 | Skirmisher 7 | tick 1 |
| 14 | Mangonel 280 | tick 1 |
| 16 | 128 | tick 1 |
| 18 | 279 | tick 1 |
| 20 | 281 | tick 1 |

The driver creates each probe on tick 0 of its second, so every one of these is a one-tick
delay, about 37 ms. With nothing to cavemanify, `unitsTransformed` stays false and
`checkOwnedUnits` runs on the same tick the unit is found — one tick sooner than run A's
cavemanified units, which is what the design predicts. **#34 is answered.**

### Criterion 12, tick rate — not resolved

Firings per game second, by window:

| Window | Rule | Churn | P1 units | Samples | Mean | Spread |
| --- | --- | --- | --- | --- | --- | --- |
| base 1 | off | off | 251 | 9 | 21.67 | 21-23 |
| phase 2 | **on** | off | 251 | 8 | 19.00 | 19-19 |
| base 3 | off | **on** | 291-319 | 9 | 19.44 | 19-21 |
| phase 4 | **on** | **on** | 319 | 9 | 17.67 | 17-19 |
| base 5 | off | off | 315 | 9 | 20.56 | 19-22 |
| phase 6 | **on** | off | 315 | 8 | 19.75 | 19-20 |

**The useful result is that churn costs nothing.** Phase 4 against base 3 retains 90.9%; phase 2
against base 1 retains 87.7%. Making two new unit ids every tick did not cost more than sitting
idle. So the remaining per-tick cost is **not** the new-unit work this ticket added — it is the
fixed O(n) `collectNewUnits` walk over the id list, plus `CheckProfessionLocations` sweeping
every unit on its 2 s timer, which is unchanged behaviour.

**Against #33's benchmark this is the design working.** #33 measured a full pass on every
`highFrequency` tick as keeping only 56% of the tick rate with an empty ledger. This keeps 88 to
96%.

**But the criterion asks for "outside a baseline's noise", and this run cannot answer that.**
- The two rule-off idle baselines differ from each other by 5% (21.67 against 20.56) at a
  comparable unit count, so baseline drift alone is about 5%.
- The measured rule cost lands between 3.9% (phase 6 against base 5) and 12.3% (phase 2 against
  base 1) for the same idle case. Those two should agree and do not.
- At about 20 firings a second, one firing is 5%. The counts are integers, so the quantisation
  is the same size as the effect being measured.

**What a conclusive re-run needs:**
- **Longer windows.** 30 s instead of 10 s takes quantisation from ±5% to under ±2%.
- **A higher tick rate.** 20 firings a second is the floor of what this method can resolve.
  Fewer units, or a faster game speed, buys resolution.
- **A constant unit count.** The churn ring holds 64 ids and removes the one 64 creations back,
  so at 2 a tick it does not start removing for 32 ticks. Base 3 therefore ran at 291 to 319
  units while phase 4 ran at a steady 319, which biases that pair against the rule. Pre-fill the
  ring before the first churn window.

One oddity worth a second look: both rule-on idle windows are dead flat (19 every second in
phase 2, 19-20 in phase 6) while every rule-off window varies by 2 to 3. That reads more like a
ceiling than a cost, and is worth understanding before trusting any percentage from this method.

## Run D — the criterion 12 re-run

Run C could not separate the rule's cost from baseline drift. This run is built to, and to say so
if it still cannot.

`python decode.py runD.xsdat D`. It prints the timeline, a window table, then the interleaved
comparisons.

**It is long: about 228 game seconds.** Run it at a fast game speed.

### What changed from run C

- **Interleaved, not sequential.** Fourteen 15-second windows alternating off / on inside each
  group, so linear drift cancels instead of accumulating. Run C had one baseline per phase and
  its two idle baselines disagreed by 5%.
- **A constant unit count.** The churn ring is filled from second 12, six seconds before the
  first measured window, so every churn window runs at the same population. In run C base 3 ran
  at 291 to 319 units while phase 4 sat at 319, which biased that pair against the rule.
- **The first two seconds of every window are dropped**, which removes the catch-up tick that
  follows re-enabling the rule.
- **Window totals, not means of per-second integers.** 15 s at about 20 firings a second is
  roughly 300 counts a window.
- **A calibration load.** Windows 12 and 14 run with the rule **off** and a dummy workload on:
  200 `structGetInt(unit, "owned")` reads per tick, the per-unit read #33 identified as the
  expensive part of a pass. If the meter cannot see that either, the method is at fault rather
  than the rule, and no percentage from this method means anything.

### Window plan

| Windows | Rule | Churn | Load | Purpose |
| --- | --- | --- | --- | --- |
| 1, 3, 5 | off | on | — | churn baselines |
| 2, 4, 6 | **on** | on | — | the criterion's case: about 205 units, 2 new ids a tick |
| 7, 9 | off | off | — | idle baselines |
| 8, 10 | **on** | off | — | idle, no new units at all |
| 11, 13 | off | off | — | calibration baselines |
| 12, 14 | off | off | **on** | calibration: a known cost, rule off |

Setup runs to second 17: bulk to about 141 units by second 10, `InitCaveman()` at 11, churn from
12 so the ring is full and the population steady at about 205 by 18.

### How to read it

- **Three independent churn measurements** (windows 2, 4, 6) and **two idle** (8, 10). If the
  rule has a real cost they should agree with each other. In run C the two idle figures were
  12.3% and 3.9%, which is what made that run inconclusive.
- **The calibration pair** (12, 14) should agree with each other too, and should show a cost
  clearly larger than the measurement's scatter. That is the proof the meter resolves anything
  at this tick rate.
- Verified against simulated data before the run: with an 8% cost injected the summary recovered
  7.7, 8.7 and 9.6%, and with 15% injected it recovered 15.3% twice, under drift.

## Run D results

> From one in-game run on 2026-10-27 (`runD.xsdat`, 9605 of 9605 ledger checks, footer present,
> 469 records). About 25 firings a game second at 205 units, against run C's 20.

**The method is sound this time, and the answer is that the rule does have a measurable cost.**

### The calibration says the meter works

| Window | What | Retained | Cost |
| --- | --- | --- | --- |
| 12 | 200 struct reads a tick, rule off | 62.1% | **37.9%** |
| 14 | the same, repeated | 61.4% | **38.6%** |

The two agree to 0.7 points. A known workload is detected, and reproduced. That retires run C's
worry that the dead-flat tick counts were a ceiling rather than a cost — this meter resolves
cost, and resolves it consistently.

### Baseline noise

The four rule-off, churn-off, load-off windows had means of 24.79, 25.08, 24.71 and 25.07
firings a second. **Window-to-window noise is 1.5%**, against run C's 5%. The interleaving and
the constant population did their job.

### The rule's cost

| Windows | Case | Measured | Mean |
| --- | --- | --- | --- |
| 8, 10 | idle, no new units at all | 5.2%, 5.6% | **5.4%** |
| 4, 6 | a fight: about 205 units, 2 new ids a tick | 8.6%, 7.4% | **8.0%** |
| 2 | the same, first measured window | 12.4% | discarded |

Window 2 is discarded because the run had not settled: its baseline, window 1, averaged 22.79
against 24.79 and 24.31 for the other two churn baselines, and window 2's own series climbs
from 20 to 22 across its 13 samples. Windows 4 and 6 are flat and agree to 1.2 points.

**Criterion 12 as worded does not pass.** It asks that the rule not move the tick rate outside a
baseline's noise. Baseline noise is 1.5% and the rule costs about 8% in the criterion's own
scenario — roughly five times the noise, measured consistently across two windows.

### What the cost is made of

- **5.4% is fixed, paid on every tick whether or not anything changed.** That is
  `xsGetPlayerUnitIds`, the O(n) `collectNewUnits` walk over 205 ids,
  `pruneUntrackedUnits`, `xsPlayerAttribute`, and `CheckProfessionLocations` over every unit on
  its 2 s timer.
- **Churn adds only 2.6 points on top** for two new unit ids every tick. The new-unit work this
  ticket introduced is the cheap part, exactly as the design intended.
- There is no easy win in the fixed part. Skipping the walk when the list size is unchanged is
  precisely the net-zero bug this ticket exists to fix.

### For the maintainer to rule on

8% is a real cost. The comparison that matters is #33's: a full pass on every `highFrequency`
tick keeps only 56% of the rate, a 44% cost, with an empty ledger. This design costs 8% in the
same conditions, about five and a half times cheaper, and buys a one-tick response where the old
rule could withhold a cavemanify indefinitely.

So the question is not whether the redesign is better — runs A to C settle that — but whether 8%
of the `highFrequency` tick rate at 205 units is a price worth paying, or whether the criterion
should be reworded against #33's 44% rather than against baseline noise.

### Correction: the 44% comparison was the wrong benchmark

The first write-up of run D compared its 8% against "#33's 44%". That figure is real but it is
the wrong thing to compare against.

- **44% is #33's row 2**: `ApplyCaveman` alone, 200 units, **empty ledger**, on every tick
  (56.4% retained). Nobody proposed shipping that. It was a design option, and it was rejected.
- **The old design's real cost** is #33's rows 7 and 8: the same work once a second. #33 says
  those two phases **sit at the noise floor** and run 2 even ranked them the wrong way round, so
  the 92.7% and 89.1% in its table are not reliable. #33 derives the cost from the per-call
  figures instead: 11 calls of ~130 ms per 10 game seconds is **~14% of game time** for a
  full-ledger sweep, plus **~2%** for the checks.
- **At a realistic ledger** the old cost is lower. The maintainer ruled 400 entries out of reach;
  at 200 entries a call is ~49-55 ms, so 11 calls is **~5.5%**, plus ~2% for the checks — call it
  **7 to 8% of game time**.

**So the old and the new designs cost about the same.** The old one paid it as a stall once a
second. The new one spreads it over every tick. The new one is never starved.

Two cautions on reading the two runs together:

- **The units differ.** #33 measures extra game milliseconds per call, then converts to a share
  of game time. Run D measures a drop in firings per game second. Both are proxies for sim-thread
  cost, and they are close enough to compare at one significant figure, but they are not the same
  measurement.
- **Run D's caveman ledger was near empty.** Its churn units are Militia, which never
  cavemanify, so nothing is recorded. That matters much less than it did for the old design: on
  a normal tick the new rule searches the ledger only for the new units, two a tick, not for all
  205. Ledger size drives the old design's cost and barely touches the new one's. That is the
  real improvement, and run D does not measure it — #33's row 4 against row 2 is where it shows.

**Revised ruling for the maintainer.** The question is not "is 8% worth paying for the fix". The
old design cost about the same when it ran. The question is whether a steady 8% every tick is
preferable to an equal total paid as a ~130 ms stall once a second, with starvation when the
game is busy. On the evidence, it is.

## Run E — what is worth splitting up

A spike, not an acceptance run. It answers one question: **which parts of the rule are a
single-tick stall, and how big are they?** That decides whether sharding the work beats
throttling the rule.

Run D showed the rule adds about 3.5 ms to a 40 ms tick. That is too small to be worth smoothing.
The suspected stalls are elsewhere: a **full pass**, and `CheckProfessionLocations` sweeping every
unit on its 2 s timer. Neither has ever been measured.

`python decode.py runE.xsdat E`. About 228 game seconds. Run at a fast game speed.

### Method

#33's unit: **extra game milliseconds for each firing**. Slow work advances more game time per
firing, so the difference between a phase and its neighbouring baselines is the cost of one call.

A full pass normally happens once, when an item arrives. To put it on the tick-rate meter it has
to repeat, so `AP10Meter` sets `unitsDirty = true` on every tick of a FULL PASS window. The rule
then does a full pass every tick, and the per-firing difference is the cost of one.

Windows are 15 s, interleaved against `normal` windows in the same group, as in run D.

### Window plan

| Windows | Rule | Mode | Ledger | Measures |
| --- | --- | --- | --- | --- |
| 1, 3 | on | normal | empty | baseline |
| 2, 4 | on | **FULL PASS** | empty | one full pass, empty ledger |
| 5 | on | fill | — | swaps 150 Villagers for 150 Knights; they cavemanify to Militia and fill the ledger. The unit count stays at about 205, so ledger size is the only thing that changes |
| 6, 8 | on | normal | ~150 | baseline |
| 7, 9 | on | **FULL PASS** | ~150 | one full pass at a realistic ledger |
| 10, 12, 14 | off | normal | ~150 | baseline |
| 11 | off | **list fetch** | ~150 | `xsGetPlayerUnitIds` alone — the part of the per-tick cost that **cannot** be split |
| 13 | off | **prof sweep** | ~150 | `CheckProfessionLocations` over 205 units — the part that can |

### What each answer means

- **Full pass, empty against ~150 ledger.** The difference is the ledger scan. #33 measured that
  as ~85% of the old design's cost. Under the new design only new units search the ledger on a
  normal tick, so this shows what is left of that problem on the one path that still walks
  everything.
- **List fetch against prof sweep.** This is the decision. The fetch cannot be sharded — the call
  returns the whole list or nothing. The profession sweep can be, trivially, because its contract
  is already "within 2 seconds" and spreading 205 units over the ~50 ticks in that window changes
  no semantics. If the fetch is most of the per-tick floor, sharding buys little. If the sweep is
  large, it is the best target in the rule.

Verified against simulated data before the run: with 35 ms, 65 ms, 2 ms and 12 ms injected, the
summary recovered 34.3/33.9, 63.6/64.3, 1.9 and 11.3.

## Run E results

> From one in-game run on 2026-10-27 (`runE.xsdat`, 9605 of 9605 ledger checks, footer present,
> 477 records). Baselines ran 40 to 48 firings a game second.

| What | Measured | Repeat |
| --- | --- | --- |
| **Full pass**, empty ledger | 40.6 ms | 52.0 ms |
| **Full pass**, ~150-entry ledger | 85.0 ms | 64.9 ms |
| `xsGetPlayerUnitIds` alone, 205 units | **2.06 ms** | — |
| `CheckProfessionLocations`, 205 units | **0.65 ms** | — |

### The sharding target does not exist

`CheckProfessionLocations` over 205 units costs **0.65 ms**. The rule-off baselines either side of
it scatter by 3.8 firings a second, about 8%, so 0.65 ms is **below the noise floor**. There is
nothing there to split up.

Worse for the idea: the one part that **cannot** be sharded, the `xsGetPlayerUnitIds` call, costs
**2.06 ms** — three times more than the part that can. Sharding the per-tick work cannot reach
the majority of the per-tick cost. A throttle can, because skipping a tick skips the fetch too.

**Caveat on the 0.65 ms.** `CheckProfessionLocations` tests `isProfessionType(typeId)` for each
unit and does nothing more unless it matches. P1's units in this run are Villagers and Militia.
A base Villager is tier 0, so it is **not** a profession type, and no unit matched. The function
took its cheap path on all 205. In a real game the villagers in jobs would match and would each
cost a struct read. That is tens of units, not 205, so it stays small — but this run measures
the floor, not the real figure.

### The real stall is the full pass

A full pass costs **40 to 52 ms with an empty ledger and 65 to 85 ms at ~150 entries.** The two
repeats of each disagree by about 30%, so treat the magnitude as solid and the precision as poor.
Taking means, that is **~46 ms empty and ~75 ms at ~150 entries**.

That is twenty times the ~3.5 ms the rule costs on a normal tick, dropped into one tick, every
time an item arrives or a research finishes.

**The ledger is ~29 ms of it** (75 minus 46). #33 predicted 30 ms for the same step — ~20 ms per
call at an empty ledger against ~50 ms at 200 entries. Two independent runs, two harnesses, one
answer.

**The residual points at a cost this ticket added.** #33 puts `ApplyCaveman` at ~20 ms and
`checkOwnedUnits` at ~15 ms, so ~35 ms of the ~46 ms is accounted for. The remaining ~11 ms is
most likely `anyUnitWithLockedProfession`, which on a full pass walks all 205 units to answer a
yes or no question. It is new in this ticket and it is only ever asked so the rule can decide
whether to call `EvictProfessions`.

### What to do instead of sharding

1. **Short-circuit `anyUnitWithLockedProfession`.** If no profession unit row is locked, no unit
   can be in a locked job, so the walk can be skipped outright. A flag kept by `refreshUnitLocks`
   would do it. Removes ~11 ms from every full pass, and most of that cost is paid in games where
   the answer is always no. Smallest change, clear win.
2. **Make `originalTypeOf` O(1).** Removes the ~29 ms ledger scan from the full pass. #33 named
   this and #10's brief puts it out of scope, so it is its own ticket.
3. **Shard the full pass across ticks** — the idea that started this, applied to the one place it
   pays. Harder than it looks: the stop-after-cavemanify guard has to stop the tick and resume at
   the right shard. Only worth it if 1 and 2 leave the stall too large.
4. **Drop the throttle.** It was already the weaker idea, and these numbers confirm it: it would
   trade a 3.5 ms per-tick cost for the same cost less often, and leave the 46 to 85 ms stall
   untouched.
