# 06: Status lines survive an age advance

**What to build:** The engine clears every written description when an age advances, so without
this the whole feature quietly stops working the moment the player reaches Feudal. The age module
triggers one full re-apply after the advance, covering technologies, units, buildings and the age
advances themselves. Saving and reloading does not clear descriptions, so resume needs no hook of
its own.

**Blocked by:** 04, 05 (so the re-apply covers every kind of line that exists).

**Status:** done

- [x] After advancing an age, every status line that was there before is there again
- [x] The re-apply runs once per advance, not on a timer, and adds no per-tick work
- [x] Saving and reloading leaves the lines in place with no further work
- [x] The xs lints from the xs folder against the entry point

## Rulings

- 2026-11-13: No new rule. `ShuffleAgesUpdate` becomes `AgesUpdate`, armed in every seed rather than
  only under `shuffle_ages`, and the re-apply hangs off the age count it already keeps.
- 2026-11-13: No per-age bookkeeping. Any advance re-applies every line, and nothing tracks which
  ages have been decorated.

## Comments

- 2026-11-13: The re-apply is `RefreshDescriptions()`, unchanged — the same call the init pass and
  `ConnectAP` already make. That is what makes the first acceptance line true by construction rather
  than by coverage: the re-apply is literally the init pass, so whatever the init pass decorated it
  decorates again, and nothing had to learn which kinds of line exist. 06 adds no function to
  `Descriptions.xs` and touches no module but `Ages.xs`.
- 2026-11-13: A first pass added an `AgeAdvanceDescriptions` rule of its own, with a `decoratedAge`
  it advanced one age at a time off `ageReached(decoratedAge + 1)`, a `highestAgeReached()` baseline
  and a bool that deferred the sweep by one firing. Thirty-eight lines for what is twelve. The
  maintainer called it: `ShuffleAgesUpdate` was already the age watcher — it loops the three ages
  every second, already counts how many are reached, and already calls `xsDisableSelf` at the seed's
  max age. All it was missing is that `InitAges` armed it inside the `AP_SHUFFLE_AGES` branch, so
  unshuffled seeds had no age watcher at all while the engine still cleared their descriptions on
  every advance. Arming it above that early return and renaming it `AgesUpdate` is the whole hook.
  Nothing else referenced the old name, in XS or in any `.aoe2scenario` binary.
- 2026-11-13: The transition is `reached > agesSeen`, one int against a count the rule already
  computes, so there is no second traversal of the ages and no per-age state. `agesSeen` starts at 0
  rather than at the age the scenario starts in, which is deliberate: a scenario that opens above
  Dark Age takes one sweep on the rule's first firing, and that is exactly the case where
  `ClimbToVanillaAge` has just forced age techs to done during `InitAges` and may have cleared the
  lines the init pass went on to write a few calls later. A scenario that opens in Dark Age reaches
  nothing on that firing and sweeps zero times. So the baseline that looked like a bug in the first
  pass is the one that needs no `highestAgeReached()` at all.
- 2026-11-13: The body is safe in unshuffled seeds, but not for the reason a first reading gives.
  Only `AP_Check_Location` is behind `ageRegistered(age)`; the `has_castle` / `has_imperial` chaining
  sits beside that guard, not under it, so arming the rule everywhere does expose two branches that
  only shuffled seeds used to reach. Traced rather than eyeballed: the two flags are written in
  exactly one place, `UnlockAge`'s else branch; `UnlockAge` is called from exactly one place,
  `GiveItem`'s 25-29 age band; and with `shuffle_ages` off `create_items` sends every
  `Age2AgeData` item to `push_precollected` instead of the pool, because `AgePool.locations` is empty.
  Precollected ages never reach the game either: the startup files are buildings, techs and units,
  one handler each, and there is no age file and no `GiveStartupAges`. So no age item is ever
  received, the flags stay false for the whole game and both branches are unreachable.
- 2026-11-13: And they are harmless even if that chain is ever broken, which is what makes this worth
  arming rather than guarding. `UnlockAge` returns early above `apMaxAge`, so a capped age stays
  locked; below the cap an unshuffled seed never called `lockAge` on the age in the first place, so
  the `STATE_ENABLE` it would apply lands on an already-enabled tech and changes nothing. A guard on
  `AP_SHUFFLE_AGES` around the chaining was written and taken back out: it would protect against
  nothing and would put the option back inside a rule that no longer belongs to it.
- 2026-11-13: `AgesUpdate` now writes a freshly checked age's line twice on the firing that sees the
  advance — once through the loop's `RefreshAgeStatusLine` and once through the sweep. Left alone.
  The two answer different events that happen to coincide here, and the per-age call is what keeps 05
  correct if the sweep ever moves; the cost is one duplicate description write per age per game.
- 2026-11-13: The honest cost, since the acceptance line says no per-tick work. Three
  `xsGetTechState` reads per second while ages remain — the reads the rule already made — and then
  nothing, because the self-disable it already had still fires at `apMaxAge`. A seed capped below
  Imperial retires sooner, and a scenario already at its cap retires on its first firing. The sweep
  itself, four hundred objects against a linear lookup, runs once per advance, which is what the line
  is protecting. Unshuffled seeds gain this rule where before they ran none, which is the one real
  addition and is the correctness fix the ticket is for.
- 2026-11-13: Save and load needed nothing, and both paths were checked rather than the one the
  ticket names. If XS state survives the reload, the rule and `agesSeen` survive with it. If it does
  not, `InitAP`'s `apArrayProbe` check catches it, re-runs `InitAges`, and `agesSeen` returns to 0,
  so the first firing after the reload re-sweeps any scenario above Dark Age.
- 2026-11-13: Unverified in game, as 04 and 05 still are. One thing a playtest settles that reading
  cannot: whether the engine's clear lands before the XS pass in the update that completes the age
  tech. If it lands after, a sweep on that firing is wiped and `agesSeen` has already moved on, so
  the lines stay gone for that age. A first pass carried a one-firing deferral against exactly that
  and it was taken out as speculative — at one second of rule granularity the two coinciding needs the
  firing to land in the same update as the tech completing. What to look at is a tooltip either side
  of each of the three advances; if a line is missing right after one advance and present after the
  next, that ordering is the reason.
