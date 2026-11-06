# 77: A mercenary that is a way to a non-unit check is classified by nothing

**Reported:** 2026-11-06, found while implementing [#53](53-granted-units-need-access.md)

**Status:** wontfix (superseded 2026-11-06: every mercenary is progression)

**Related:** [#53](53-granted-units-need-access.md) (the rulings this follows from)

## Report

`Age2World.needs_mercenary` decides whether a mercenary is progression, and it is two halves: the
hand-authored `in_logic` flag for the mercenaries that are a way to a check in every seed, and a
pool-derived half for the ones that are a way to a check only in some. The pool half asks exactly
one question - is a roster unit a unit or hero check in this seed - so the only setting it can
react to is unitsanity. Every other way a setting can turn a mercenary into a route is invisible
to it.

**Buildings are the live case.** Mercenaries grant buildings as well as units: Hermit Monks
declares `starts_with_building[MONASTERY]`, Chinese Engineers and Bombard Cannons declare the
Siege Workshop. Under `shuffle_buildings: Military` the Monastery is a check that Hermit Monks is a
way to reach. Measured at unitsanity 0 with Base+Economy+Tech+Military+Castle shuffled, Hermit
Monks is named by 102 spots while the pool half claims nothing at all, because no unit is a check.
It is classified correctly today only because Hermit Monks is on the always-list. A mercenary whose
only conditional route is a building, a tech or an age has no mechanism representing it, and would
be silently under-claimed.

**Free triggers are the mirror case.** The pool half subtracts
`startup ∪ AUTHORED_TRIGGER_UNITS` before asking its question. That list records which units a
trigger hands over, but not whether the trigger costs anything, so it cannot tell Genghis 1's
opening riders - `obtains_unit[CAVALRY_ARCHER] = True_()`, free - from Joan 6's Champion, which
costs `AP_JOAN_6_ARMY`. Two consequences, pulling opposite ways:

- Naiman and Tayichi'ud are correctly not progression, but for the wrong reason. Their units are
  free, so the tribes are a way to nothing; the subtraction catches them by accident.
- A Single Longswordsman is a way to Own Champion from Unitsanity Line up, and the pool half
  cannot see it, because Champion sits in `AUTHORED_TRIGGER_UNITS`. #53 carries it on the flag
  instead and accepts the resulting over-claim in unitsanity-off seeds.

## What this needs

Classification happens in `create_item`, before any rule exists, so none of this may be answered by
reading a rule. Rules come after items; that ordering is Archipelago's and is not up for
negotiation here. The inputs have to be static data plus the pool, which already knows which
buildings are checks - `pool.buildings.locations` is read in `create_items` today.

1. Static data for the buildings a scenario's trigger leaves standing, the counterpart of the
   mercenary roster, so the pool half can ask the building question the same way it asks the unit
   question.
2. Static data for which granted units and buildings the scenario hands over **for free**, so the
   subtraction stops conflating a free trigger with one behind an item. This replaces the
   `AUTHORED_TRIGGER_UNITS` subtraction in `needs_mercenary`; that list keeps its own job, pinning
   `set(obtains_unit) == set(trigger_units)`.
3. A test pinning both against the logic. A test may read rules freely, so the authored "free" set
   can be compared against the grants that resolve to `True_()`, and the authored building set
   against `starts_with_building`. That is what keeps hand-authored data from drifting from the
   rules it mirrors, and it is the reason this is worth doing as data rather than as a third flag.
4. `in_logic` stays, and keeps the routes that are not a check of a granted thing at all -
   objectives, defeat rules, `has_vils`. Those are underivable from pool data in any ordering.

**Acceptance criteria**

- [ ] a mercenary that is a way to a building check is claimed in the seeds where that check exists
- [ ] Naiman and Tayichi'ud are not progression because their grants are free, not because their
      units appear in `AUTHORED_TRIGGER_UNITS`
- [ ] A Single Longswordsman is claimed from Unitsanity Line up and not in unitsanity-off seeds,
      and comes off `in_logic`
- [ ] `needs_mercenary` no longer reads `AUTHORED_TRIGGER_UNITS`
- [ ] the authored free-grant and standing-building data are pinned against the logic by a test
- [ ] `TestMercenariesTheSeedNeeds` holds with no outlier at every option shape it measures

**Out of scope**

- Moving classification after `set_rules`, or building logic before `create_items`. Rules come
  after items
- Re-opening the #53 rulings on what counts as being in logic. A mercenary is in logic where it is
  a way to a check; that is settled

## Rulings

- 2026-11-06 - Every mercenary is progression. `Mercenary.in_logic`, `Age2World.needs_mercenary`
  and the pool half are deleted, and `Mercenary` leaves `PseudoClassification.progression_if_needed`
  for plain `ItemClassification.progression`. This ticket, and #53's three 2026-11-06 rulings on
  what `in_logic` carries, are superseded.

## Comments

> *This was generated by AI while implementing #53.*

The measurements behind this are in #53's `in_logic after the grants were authored` comment.
Option shapes measured there: unitsanity 0 / Line / All, techsanity 1 and 3, caveman on, and
`shuffle_buildings` Base+Economy+Tech+Military+Castle. Not measured, and worth covering when this
is picked up: `shuffle_villager`, `shuffle_ages`, `goal`, `market_trade`, `partner_trade`,
`local_start`, `existing_techs`.

> *This was generated by AI during triage.* 2026-11-06.

**Closed as superseded.** The maintainer ruled that every mercenary is progression, which removes
the question this ticket asks. There is no longer a classification to derive, so neither half of
`needs_mercenary` survives and no static data is authored.

Triage got far enough to find that the building half would have been dead code. All three
mercenaries that gate a `starts_with_building` entry stay in logic for reasons no building data
reaches: Hermit Monks' Monk carries the relic-gold routes through `standing_monk()`, two of which
take a *built* Monastery (`ScenarioRoutesLogic.py:163-190`), so the route holds with no Monastery
check at all; Chinese Engineers is `has_vils` (`genghis_3.py:37`); Bombard Cannons is named
directly in Into China's defeat rules (`genghis_3.py:50-52`). The free-grant half was the half
that moved anything, and the blanket ruling covers it.

Two facts worth keeping, since they outlive this ticket:

- `can_field` is training-only, so a granted unit never feeds military strength. The routes a
  granted unit opens are unit and hero locations, `standing_monk()`, and villagers through
  `has_vils` and the jobs.
- `UnitPool.mercenary_exclusive_location` implemented no exclusivity. It asked only whether a unit
  or its line is a location in this seed; the exclusivity was the subtraction in `needs_mercenary`.
  With that caller gone, the name is the last trace of a distinction that no longer exists.

**What landed in the working tree:** `Mercenary.in_logic` and its eight call sites, the
`classification_for` override and `needs_mercenary` in `__init__.py`, and `TestMercenaryLogicFlag`
and `TestMercenariesTheSeedNeeds` are gone; `TestMercenaryClassification` pins the ruling instead.
`AUTHORED_TRIGGER_UNITS` is untouched and keeps `set(obtains_unit) == set(trigger_units)`, so
ADR 0005 stands.

**Not done:** 21 items moved from `useful` to `progression`, so progression density rises in every
seed. The fill gate has not been replayed against the corpus in `fuzz/bench/README.md`.
