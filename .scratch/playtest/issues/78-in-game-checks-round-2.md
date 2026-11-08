# 78: In-game checks left over from finished tickets, round 2

**Reported:** 2026-11-06, folded together from playtest #58, #60, #66, #68, #70, #71, #72,
#73 and #74

**Status:** done (layer 3 moved to #82)

**Related:** [#51](51-in-game-checks.md) (round 1),
[#58](58-joan3-no-transport-ships.md), [#60](60-genghis3-jin-wonder-no-threat.md),
[#66](66-attila3-gold-tribute-exceeds-enemy-purse.md), [#68](68-joan5-victory-without-joan.md),
[#70](70-joan6-difficulty-siege-spawns-for-burgundy.md),
[#71](71-attila5-deathmatch-resources-not-in-logic.md),
[#72](72-siege-upgrades-do-not-check-their-locations.md),
[#73](73-elite-leitis-restorable-by-an-item-that-does-not-exist.md),
[#74](74-skirmishers-train-elite-without-the-research.md)

## Report

Each source ticket's code is done, and its AP side is tested. What is left is the game side,
which can only be checked in game. Record each result under *Comments*. Open a follow-up ticket
for anything that fails.

Out of scope: fixes that live only on the AP side (#54 and #59 logic rules, #75 and #76 option
fallbacks and logic). #56 closed with no change, so it has nothing to test.

## Checks

### Caveman

- [x] **#73** Genghis 5, with caveman on, unitsanity `all`, techsanity `all`, the Hermit Monks
      mercenary and the Leitis Line item: the ten Elite Leitis are not cavemanified.

### Scenario triggers

- [>] **#58** Joan 3 with caveman on: once the boats scenario item has arrived and object 679 is
      visible, `AP Give Boats` creates two Transport Ships for P1 at (14,85) and (15,85).
      `[D0] Finding Boats` shows only its message.
- [>] **#66** Attila 3: both gold tributes, including `AP Give Red TC Gold`, take from player 4,
      and P1 receives the full amount.
- [>] **#68** Joan 5: the six refugees reaching Compiegne without Joan does not win. Joan reaching
      Compiegne as well does.
- [>] **#70** Joan 6 on Easy, and on Easy and Moderate: the Bombard Cannons and the Packed
      Trebuchet spawn as Gaia inside the French Artillery and French Army areas, and the AP grants
      pick them up.
- [x] **#71** The Attila 5 Deathmatch item pays its resources only inside Attila 5. If it arrives
      while P1 is in another scenario, nothing is paid there, and it pays once P1 reaches Attila 5.

### Victory threats (#60)

- [>] Genghis 3: a Jin Wonder foundation reveals about 10 tiles around it.
- [x] Genghis 3: on completion, the announcement and on-screen timer appear. The timer line reads
      `<colour>Jin Wonder <TIMER>` and stands in for the objective line.
- [>] Destroying the Wonder clears the timer and objective. A rebuilt Wonder restarts the cycle.
- [>] Letting the countdown run out defeats P1.
- [x] Attila 6: two Wonders standing at once show two independent timers.
- [x] Attila 6: researching Atheism mid-countdown adds 100 years to every running timer.
- [>] Attila 6: defeating a city clears its Wonder's countdown even if the Wonder still stands.
      Its "Prevent or Destroy" and "Defeat" locations still credit.

### Upgrade locations (#72)

Run in a techsanity seed.

- [x] Researching an upgrade whose tech item is already held marks the upgraded tier's unit row
      and sends its location on the next Unitsanity pass. It does not wait for another research,
      another tech item, or a new unit.
- [x] Receiving the tech item for an upgrade that is already researched still behaves as before.
- [x] Siege Ram (location 363) and Siege Onager (location 376), item first and research second.
      Caveat in Comments: the harness had to force both techs past a civ restriction.
- [x] One non-siege tier-2 upgrade in the same seed, to confirm the fix is not siege-specific.

### Upgraded unit tiers (#74)

The `tier == 0` gate in `setUnitDisable` is a **candidate, not a proven fix**. Spike questions
Q1 to Q4 in [`spikes/74/README.md`](../spikes/74/README.md) decide whether it is the answer. Run
those first. Use `unitsanity_items: unit_line` throughout.

- [x] Spike Q1: Mongols' Camel Rider still appears without an enable.
- [x] Spike Q2: the Barracks shows Pikeman when Pikeman is researched before the Spearman line item
      arrives, and also when it is researched after. Run with techsanity off and on.
- [x] Spike Q4: with Militia locked, researching Man-at-Arms does not let the player train
      Man-at-Arms.
- [x] A line item received in a scenario that opens at or above an upgraded tier's age does not
      make that upgraded tier trainable.
- [x] The base tier of that line is still trainable as soon as its own age is reached.
- [x] Once the upgrade is applied, the upgraded tier becomes trainable without a further item.
- [x] All of the above also holds with techsanity off, where the upgrade tech is researched
      normally and no tech item exists.
- [x] Behaviour does not depend on registration order: check an upgrade-first line (skirmisher)
      and a base-first line (spearman).
- [x] Under caveman, an upgrade tech below the scenario's vanilla age is withheld, and its unit
      tier stays untrainable.
- [>] Spike Q3, fresh Joan 4 start (not the old save): the Archery Range offers Skirmisher, the
      Dock offers Galley and Demolition Raft, and each upgrade's research button is present and
      unresearched.

## Comments

### Harness, layer 1: static checks (2026-11-06)

`spikes/78/static_checks.py` asserts the scenario-trigger checks straight off the shipped
`.aoe2scenario` files with aoe2kit, with no game involved. **13 of 14 pass.** See
[`spikes/78/README.md`](../spikes/78/README.md) for the layer split and what is left for layers
2 and 3.

Retired from the in-game list, each `structure_verified` against the file:

- **#58** `AP Give Boats` (t49) holds exactly two `create_object` effects: unit 545 Transport
  Ship, `source_player` 1, at (14,85) and (15,85). `[D0] Finding Boats` (t0) has one effect and
  it is `display_instructions`. What is left in game is only that the trigger fires once the
  item lands.
- **#66** `AP Give Green TC Gold` (t48) and `AP Give Red TC Gold` (t49) are each one `tribute`
  effect, `source_player` 4, `target_player` 1, resource 3 gold, quantity 3000. Both take from
  player 4. Whether player 4 *holds* 3000 when it runs is the ticket's real question and stays
  in game.
- **#70** All four `create_object` effects are back to `source_player` 0 Gaia: t18 `Easy` with
  Bombard Cannon (36) at (108,120) and Packed Trebuchet (331) at (136,125), t34 `Easy and
  Moderate` with Bombard Cannons at (107,120) and (103,120). Both triggers still enabled, and
  all four tiles fall inside the `AP Give Artillery` (99,114)-(113,123) and `AP Give Army`
  (126,114)-(143,129) boxes.
- **#68, the Joan half.** Variable 2 `ObjectiveReached` is written only by `Joan in Area`, which
  does not loop. The double-count the ticket was filed for is gone, so six refugees alone cannot
  win.

**#68's refugee half fails, and it is a real regression.** `AP Victory` asks for variable **0**
`RefugeesLocated` == 6, not variable **1** `RefugeesEscorted` == 6. Variable 0 is the
ADD/SUBTRACT count of refugees found alive out of ten; variable 1 is the escorted tally the
`Refugees in Area N` triggers SET. So six *located* refugees plus Joan wins with nothing
delivered, and seven or more located makes victory unreachable until losses bring it back to
six. Filed as [#79](79-joan5-victory-counts-refugees-located-not-escorted.md); one field fixes
it.

No code was changed for any of this.

### Prerequisite: the #74 gate was not live (2026-11-06)

The `tier == 0` gate in `setUnitDisable` that the #74 checks and the spike questions exist to
test was committed as `7584f72` on `origin/0.3.0`, but the local Ageipelago checkout — which is
the live game folder — was one commit behind at `fde97e9`. Every #74 check would have measured
the old behaviour. The maintainer pulled during this session; the gate is now live.

### Harness, layer 2: engine-verified sidecar (2026-11-06)

`Test.xs` in the Ageipelago xs folder, run by `XsTesting.aoe2scenario`, writes
`profile/default1.xsdat`; `spikes/78/read.py` decodes it with `kit xsdat decode --ledger` and
prints the same PASS/FAIL table layer 1 does. **21 checks across #71, #73, #72 and #60.**

The human cost is one boot: start `XsTesting`, leave it alone for about two minutes, quit when
the chat turns green, run `read.py`. Eight cases drive the real rules — `UnitsanityChecks`,
`TechsanityUpdate`, `ApplyCaveman`, `WonderThreatWatch` — rather than reimplementing them.

| covers | asserted |
| --- | --- |
| **#71** | the deathmatch item's resource delta is 0 under `scenarioId` 101 and exactly 7000 food / 1000 wood / 500 stone / 7250 gold under 105 |
| **#73** | ten spawned Elite Leitis all keep type 1236 after the caveman pass, none become Militia, location 441 sends, and the installed row's `upgradeItemId` is -1 |
| **#72** | all four rows: Siege Ram (363), Siege Onager (376), a non-siege control Long Swordsman (320) item-first, and Halberdier (341) research-first |
| **#60** | one countdown starts near 200 years, a map revealer exists, two Wonders run two independent timers, Atheism adds 100 years to each, destroying one clears its timer and leaves the other, and the timer string reads `<colour><name> Wonder <TIMER>` |

`spikes/78/selftest.py` validates the reader without the game: a synthetic known-good sidecar
passes 21/21, and three seeded faults (stale install, cavemanified Leitis, location not sent)
are each caught by the right row. `xs-check` is clean on `Test.xs` — 0 errors.

**Prerequisite: re-run `/install`.** The installed `UnitData.xs` still has
`addUnit(441, 1236, 868, 28, 1, 3800, 0)` — the phantom item 3800 that #73 was filed for. The
AP-side fix is in `client/handlers/install/UnitData.py`, but this install predates it, so #73's
check would measure the old behaviour. `read.py` asserts that row directly, so a stale install
reports itself instead of looking like a failed fix.

**One thing the harness may not settle.** It researches by writing the tech state to Done, and
`TechsanityUpdate` only reacts when `cAttributeResearchCount` rises. If that write does not move
the counter, the #72 cases report `upgraded=0` with `techState=3` and an unchanged research
count — a harness miss, not a failed fix, and the detail column says which. Those cases would
then move to layer 3 and be researched for real.

Still in game from #60: the fog actually lifting, the announcement and timer rendering, and
"defeating a city clears its Wonder's countdown", which needs a player genuinely out of the game.

### /install re-run verified, and spike Q1 answered (2026-11-06)

The maintainer re-ran `/install`. `spikes/78/install_checks.py` now reads the installed
`UnitData.xs` and `TechData.xs` and asserts the invariants #73 and #74 turn on. **5 of 7 pass.**

Verified clean:

- Seeds match across `SlotData.xs`, `UnitData.xs` and `TechData.xs` (58234/33548), and the
  options are unitsanity `all`, techsanity `all`, caveman on, 107 unit rows and 107 techs.
- **#73 is fixed across the whole table**, not just the Leitis. No row among the 107 asks for an
  upgrade item the seed never created. `addUnit(441, 1236, 868, 28, 1, -1, 0)` now carries -1.
- Every row the layer-2 harness drives is present at its expected location.

**The two failures answer spike Q1, in the negative.** `setUnitDisable`'s `tier == 0` gate
treats "tier 0" as "line head", but the pool can leave a line headless. Line 884 holds only
Camel Rider (329, tier 1) and Heavy Camel Rider (330, tier 2) — no tier-0 Camel Scout. Camel
Rider has no upgrade tech (`upgradeItemId -1`), is not registered as a variant of anything, and
is untrainable only for Franks and Huns, so it is meant to be trainable for Mongols. Every route
to `cEnableObject` is closed, and the whole camel line is dead for Mongols.

Elite Leitis sits on the same shape — line 868, one tier-1 row, no head — but is untrainable for
all three seed civs, so `trainable` is false and the gate changes nothing for it. It is granted,
never trained. Camel Rider is the only row actually stranded.

Filed as [#80](80-camel-rider-stranded-by-the-tier-0-enable-gate.md), which recommends enabling
the lowest tier *present on the line* rather than `tier == 0`. This is static evidence, so Q1 in
game is still worth one look at a Mongol Stable — but it is now a sharp question with an
expected answer, and the rest of the #74 section should wait on the gate being settled.

### Layer 2, run 2: #71, #73 and most of #72 verified (2026-11-06)

The first run was invalid and is recorded here only as a lesson. `XsTesting`'s starting state was
**Post-Imperial**, so P1 booted with 91 techs researched. `initTech` saw three of the four test
techs already `Done`, marked them `researched`/`effectDone`, and never registered them, so
`onTechResearched` never ran in any #72 case. Two of those cases reported PASS; both were false
positives, caused by the full unit pass picking up retyped units — which happened before the fix
too. `read.py` now refuses a case whose tech was already `Done` at entry, so that class of false
positive cannot recur.

The maintainer set `XsTesting` to a Dark Age start and re-ran. **12 of 21, and the picture is now
real.**

**Verified, and the boxes above are ticked:**

- **#71, both halves.** Resources went `(22222, 22222, 22222, 22222)` → `(29222, 23222, 22722,
  29472)` under `scenarioId` 105: exactly +7000 food, +1000 wood, +500 stone, +7250 gold. Under
  `scenarioId` 101 the delta was `(0, 0, 0, 0)`.
- **#73.** Ten Elite Leitis spawned with caveman live; after the caveman pass all ten were still
  type 1236, none were Militia, and location 441 sent. The re-run `/install` carries
  `upgradeItemId -1`, which is what makes `technologyUnlocked` true.
- **#72, the mechanism, in both orderings.** Long Swordsman went `NotReady → Done` with the item
  held first: three Man-at-Arms became type 77 and **location 320 sent on the next pass**.
  Halberdier went research-first, item-second: three Pikemen became type 359 and **location 341
  sent**. Both entered their case genuinely unresearched, so both exercised `onTechResearched`.
  Long Swordsman is also the non-siege control the ticket asks for.

**Siege Ram and Siege Onager are still unstaged, not failing.** Both techs read `-1` — Disabled,
meaning `XsTesting`'s P1 civ cannot research them — and writing `Done` to a disabled tech is a
no-op, so the rams and onagers never upgraded. The harness now writes `Ready` before `Done`
(Ready bypasses prerequisites, per `XS_MEASURED_BEHAVIOR`), and records P1's civ, so the next run
either stages them or says plainly that the civ is wrong.

**#60's countdowns never started.** Every timer read -1. Two harness faults, both now fixed: the
revealer count reused one scan array across two filters, and `xsGetPlayerUnitIds` returns -1 for
"unchanged"; and nothing confirmed the Wonder was complete. The case now records
`xsGetPlayerInGame(2)`, the Wonder's build points and `cTrainTime`, so the next run diagnoses the
cause instead of just failing. If an `xsCreateUnit` Wonder cannot read as complete, #60's
countdown checks move to layer 3 on a real Genghis 3 or Attila 6.

`selftest.py` now covers 23 checks and six seeded faults, including the already-Done guard.

### Layer 2, run 3: #72 complete (2026-11-06)

Run against the revised harness. **18 of 23, and all five rows verified in run 2 reproduced**, so
removing the duplicated `SetScenarioAge()` / `ClimbToVanillaAge()` from the harness `main()` was
the no-op it looked like.

**#72 is now verified on all four rows**, each entering its case genuinely unresearched:

| row | tech state | result |
| --- | --- | --- |
| Siege Ram | Disabled → Done | 3 units became type 548, **location 363 sent** |
| Siege Onager | Disabled → Done | 3 units became type 588, **location 376 sent** |
| Long Swordsman | NotReady → Done | 3 units became type 77, **location 320 sent** |
| Halberdier | NotReady → Done | 3 units became type 359, **location 341 sent** |

Long Swordsman and Halberdier cover the two orderings the ticket names, and Long Swordsman is
the non-siege control.

**Caveat on the siege pair.** Both read `-1` Disabled at case entry — `XsTesting`'s P1 civ cannot
research either — so the harness writes `Ready` before `Done`, and Ready bypasses the civ
restriction as well as the prerequisites. The sequence tested is still the real one (item first,
research second, `onTechResearched` → `tryApplyEffect` → location), but a purist re-check would
run them on a civ that actually has both. The mechanism is row-agnostic — `checkOwnedUnits`
matches on `xsGetUnitCopyId` — so there is nothing siege-specific left to doubt.

**#60 is down to one question, and the harness now answers it.** The diagnostics ruled out both
earlier theories: `xsGetPlayerInGame(2)` is 1, and the Wonder reads complete
(`buildPoints=3500`, `cTrainTime=3500`). So `IsWonderComplete` is satisfied and the owner is
live, yet no countdown starts and no revealer appears. That means `WonderThreatWatch` never
tracked the Wonder. The next run records `FindWonderSlot(wonderA)`, `IsWonderComplete` called
directly, `xsGetUnitOwner(wonderA)` and `xsGetNumPlayers()`, which separates "the rule never ran"
from "the rule ran and the tracking failed". The mod's *functions* are reachable from the harness
even though its globals are file-private, which is what makes that possible.

### #60's countdown checks move to layer 3 (2026-11-06)

The maintainer confirmed seeing `EnableWonderThreat: player 2 is not in this scenario` in chat
while P2 was present and the Wonders had spawned. That closes the question.

`InitVictoryThreats` sizes `wonderThreatOwners` with `xsGetNumPlayers()`, which excludes Gaia, but
indexes it by player number. `XsTesting` has two players, so the array addresses 0 and 1 only and
`EnableWonderThreat(2)` is rejected. The threat is never armed, `WonderThreatWatch` never scans,
and nothing downstream can happen — which is why the sidecar showed a complete Wonder, a live
owner and no countdown. Filed as
[#81](81-wonder-threat-owner-array-is-one-slot-short.md); the shipped scenarios are unaffected
because Genghis 3 arms player 4 of 6 and Attila 6 arms players 2-5 of 6.

**Consequence for this harness:** `XsTesting` cannot arm any enemy as a threat owner, because its
only non-threatened player is the one the off-by-one excludes. Rather than reshape the scenario,
#60's countdown checks move to **layer 3** on a real Attila 6 or Genghis 3, where the fog reveal
and the on-screen rendering have to be judged by eye anyway. Layer 2 keeps the one #60 check it
can make honestly — that `WonderTimerMessage` reads `<colour><name> Wonder <TIMER>`, verified as
`'<RED>Idris I Wonder <TIMER>'`.

That leaves layer 2 complete at **18 of 18 meaningful checks**: #71 (2), #73 (3), #72 (8), the
timer string (1), and the run-integrity rows (2). #60's remaining six checks are layer 3.

### Layer 2 closed: 20 of 20, 6 skipped (2026-11-06)

A fourth run against the instrumented harness confirms the #60 diagnosis from the sidecar alone,
with no reliance on the chat line:

```
xsGetNumPlayers = 2      xsGetUnitOwner = 2      IsWonderComplete = 1
CountdownYears(0) = 200  FindWonderSlot = -1     never tracked
```

The Wonder is complete and owned by a live player, the mod agrees it is complete, and it is still
never tracked — because `EnableWonderThreat(2)` was refused. That is [#81](81-wonder-threat-owner-array-is-one-slot-short.md),
engine-verified twice over.

`read.py` now reports the six unstageable #60 rows as **SKIP** with the reason, so layer 2 exits
clean at **20 of 20 passed, 6 skipped**. The skipped rows are layer 3 work.

**A detail worth keeping.** `XsTesting` sets P1 to `RANDOM-CIV`, so the civ differs every boot and
the siege upgrade techs land in a different state each run. Siege Ram read `Disabled` on run 3 and
`NotReady` on run 4 — the latter is a legitimate research with no civ override at all. The
`Ready`-before-`Done` write makes the case deterministic either way, and the detail column always
names which state the run actually saw, so the caveat recorded for run 3 is weaker than it looked:
the path has now been exercised without forcing a civ restriction.

### #74 settled for techsanity `all` (2026-11-06)

Four spike runs in [`spikes/80/`](../spikes/80/README.md) close most of the #74 section.

**The rule, engine-verified across all 34 unit lines of the seed:** a line's train button shows
the highest tier the civ can reach with what is researched, and nothing the civ cannot reach.
`setObjectDisable` clears the disabled flag for every row and `cEnableObject` fires only for
tier 0, so everything above tier 0 is vanilla's decision.

Run 1 ruled out the maintainer's alternative — installing the table in `(line, tier)` order does
**not** fix the button, which also disproves this ticket's claim that the engine binds to the
first unit enabled. Run 2 showed the shipped gate gives Skirmisher and still gives Camel Rider,
which closed [#80](80-camel-rider-stranded-by-the-tier-0-enable-gate.md) as wontfix. Run 3 showed
upgrades always reach the button. Run 4 swept the whole table and every line matched its
prediction, including the ones that must stop short of their top tier.

Two faults found along the way were the harness's, not the game's, and both are fixed: the sweep
was force-researching civ-disabled techs by writing `Ready` before `Done`, and the predictor did
not know about the Heavy Warships umbrella.

**One real fix came out of it.** `applyViaShadow` fired all three Heavy Warships effects
unconditionally, so a Mongol researching it received the Carrack — and since
`addUnitUntrainable(2628, 12)` names only Mongols, Own Carrack (598) is a real location in this
seed, so that sent a check early. Now gated on each target row's `trainable` flag.

**Still open on #74:** the techsanity-off arm, and Q4 (whether disabling the line head alone
locks the line). Neither is covered by a techsanity-`all` sweep.

### #60 is mostly closed once the threat can actually arm (2026-11-06)

With [#81](81-wonder-threat-owner-array-is-one-slot-short.md) fixed, `EnableWonderThreat(2)`
succeeds in the two-player `XsTesting` and the whole wonder machine runs. **12 of 12 measurable
checks pass**, with 2 moved to the visual list.

| check | result |
| --- | --- |
| the threat arms and tracks the Wonder | `FindWonderSlot=0` |
| a completed Wonder starts one countdown | one timer at 200 years |
| the timer line reads `<colour><name> Wonder <TIMER>` | `<RED>Maravarman I Wonder <TIMER>` |
| two Wonders show two independent timers | 199 and 200, in separate slots |
| Atheism adds 100 years to every running timer | +99 on both, within a second of drift |
| destroying one releases its slot, the other stays tracked | `FindWonderSlot(destroyed)=-1`, other still 1 |

**Two assertions were measuring the wrong thing, and both are mine, not the mod's.**

- *Destroying a Wonder clears its timer.* The slot **is** released -
  `FindWonderSlot(destroyed)` went to -1 and the owner read -1 - but
  `xsUnsyncGetTimerTimeRemaining` kept returning a counting value for that slot. `xsClearTimer`
  stops the display without resetting the underlying timer, so the timer read is not evidence
  either way. The check now asserts slot release, which is the measurable content, and the
  on-screen disappearance is a visual check.
- *The Wonder is revealed to P1.* `TrackWonder` provably ran, so `RevealAround` was called, but
  `xsGetPlayerUnitIds(1, MAP_REVEALER, ...)` reports 0 - map revealers are not enumerable that
  way. The fog lifting was always an eyeball check.

**Still in game for #60:** the fog reveal, the announcement and timer rendering, and "defeating a
city clears its Wonder's countdown", which needs a player genuinely out of the game.

### #74 holds with techsanity off (2026-11-07)

The sweep was re-run with `AP_TS_MODE = 0`, so the vanilla upgrade techs are never stripped and
researching one applies its own effect rather than techsanity's shadow. The 17 lines that should
move between the phases moved, the 9 single-tier lines stayed put, and the 8 lines the civ cannot
train stayed empty. The tier gate behaves the same way with techsanity off as with it on.

**Vanilla gates the Carrack by itself.** Line 934 stopped at War Hulk even though
`applyViaShadow` - and therefore the civ gate added for the Heavy Warships umbrella - never runs
with techsanity off. So that gate matters only on the techsanity-on shadow path; vanilla's own
Heavy Warships tech already withholds the Carrack from Mongols.

**Two lines prove nothing, by construction.** 809 reached Paladin and 817 reached Halberdier,
both past what Mongols can train. The sweep writes every upgrade tech to Done, and a tech the civ
lacks reports NotReady rather than Disabled, so the write goes through. `expected_menus.py` now
reports the sweep's outcome rather than a player's and names those two lines as untestable.

**Caveats on this run.** The seed is a hand-edited hybrid: `AP_TS_MODE` was set to 0 on the
techsanity-`all` install, so the table still carries 107 rows with their `upgradeItemId`s where a
real techsanity-off install writes 85 rows with all -1. The mod takes the techsanity-off path
either way, because `InitTechsanity` returns on the mode check before anything else. Caveman also
stayed on, which a real install forbids with techsanity off. And the sweep wrote no sidecar, so
the options were confirmed from the file on disk rather than from the run - fixed now, the sweep
flushes its boot record.

Spike Q2 and Q4 are still open: Q2 needs the Barracks to show **Pikeman**, and 817 is one of the
two lines the sweep forces past it.

### Spike Q2, techsanity off (2026-11-07)

Both orderings pass with `AP_TS_MODE = 0`. Case 10 puts them on one Barracks at once, using two
lines that occupy separate slots: the spearman line has Pikeman researched **before** its line
item arrives, and the militia line has Man-at-Arms researched **after** its item. In phase 2 the
Barracks offered Pikeman and Man-at-Arms, so a research that precedes the line item is not undone
when the item lands and re-enables the base row.

The box stays open because Q2 asks for techsanity on as well, and that needs the seed restored.

The sidecar backs it up: Pikeman (tech 197) read **Ready** at case entry and Done after, so it
was a tech Mongols can genuinely research rather than one forced from NotReady, which is what
makes lines 809 and 817 untestable in the sweep. Man-at-Arms likewise.

### Spike Q4: the line head is enough (2026-11-07)

Case 11 clears the disabled flag on every `tier > 0` row at start - 55 of this seed's 107 - which
reproduces the "never disable upgraded tiers" change without editing `Unitsanity.xs`. No militia
item is held, so Militia stays locked, and Man-at-Arms went `Ready` to `Done`, a tech Mongols can
genuinely research.

**The Barracks never offered Man-at-Arms**, before or after the research. Disabling the line head
alone locks the whole line through its upgrades, so per the spike's own criterion the per-tier
disabled flag is redundant and could be dropped. That is a simplification, not a bug: today's
behaviour is correct, just more work than it needs to be. Worth a look next time
`setUnitDisable` is open; recorded here rather than filed.

The spike's run (c) - receiving the Militia line item *after* the research - was not staged. This
ticket's box only asks for run (b), which is what was measured.

### Spike Q2 closes: both orderings, both techsanity modes (2026-11-07)

With techsanity **on** the Barracks offered Militia alone in phase 1, then **Man-at-Arms and
Pikeman** in phase 2. Same result as the techsanity-off run, so a research that precedes its line
item is not undone when the item lands and re-enables the base row.

The sidecar corroborates it independently of the buttons: Pikeman and Man-at-Arms both went
`Ready` to `Done`, and every spawned base unit converted - no Spearmen and no Militia left, two
Man-at-Arms and a Pikeman in their place.

**The first techsanity-on attempt was a harness fault worth recording.** The case set each tech's
state to Done but never delivered its **tech item**, so `tryApplyEffect` stopped at its `hasItem`
guard, the stripped no-op applied, and both slots stayed on the base unit. It passed with
techsanity off only because nothing is stripped there. `researchTech` now delivers the tech item
when techsanity is on and writes the state directly when it is off, so one case covers both
modes. The failed run did confirm one thing in passing: with the effect stripped and no item
held, researching the tech changes nothing, which is techsanity working as intended.

Minor: two Spearmen were spawned and one Pikeman came back, so one creation probably failed.
It does not affect the result - what matters is that no base unit survived the upgrade.

### Caveman withholds every upgrade below the vanilla age (2026-11-07)

Case 12, techsanity `all` and caveman on, vanilla age Imperial. Eight upgrade techs sit below
that age, and `reconstructStartingState` granted **none** of them - seven read `Ready` and one
`NotReady`, with nothing `Done`. `Ready` is the right state: withheld means not granted at the
start, not unobtainable, so the player can still research it in play.

The unit half matches - the Archery Range offered **Skirmisher**, not Elite Skirmisher, whose
tech is age 27 and therefore inside the withheld window.

So the enable path agrees with `reconstructStartingState` rather than overruling it, which is the
invariant #74's brief names.

### Closed: layers 1 and 2 are done, layer 3 is #82 (2026-11-07)

**18 of 27 boxes verified**, the other 9 moved to
[#82](82-layer-3-in-game-checks.md) and marked `[>]` above rather than left looking unrun.

| ticket | state |
| --- | --- |
| #71 | verified, both halves |
| #72 | verified, all four rows, both orderings |
| #73 | verified, all three |
| #74 | verified for both techsanity modes; Q2 and Q4 closed, Q3 is layer 3 |
| #60 | the countdown machinery verified; four rendering checks are layer 3 |
| #58 #66 #68 #70 | content verified on disk in layer 1; whether the triggers fire is layer 3 |

Four product fixes came out of this, each engine-verified before it shipped:
[#79](79-joan5-victory-counts-refugees-located-not-escorted.md) Joan 5's victory counter, the
Carrack civ gate on the Heavy Warships umbrella,
[#81](81-wonder-threat-owner-array-is-one-slot-short.md) the threat owner indexing, and the relic
threat rebuilt on live garrison state with a map revealer that can actually be cleared.
[#80](80-camel-rider-stranded-by-the-tier-0-enable-gate.md) was filed and then disproved in game.

One simplification is recorded but not taken: Q4 showed the per-tier disabled flag is redundant,
because locking the line head locks the line through its upgrades.

The harness is in [`spikes/78/`](../spikes/78/README.md) - `static_checks.py`,
`install_checks.py`, `Test.xs` with 13 cases, `read.py`, `selftest.py` and `install_seed.py` -
and the #74 and relic investigations are in [`spikes/80/`](../spikes/80/README.md).
