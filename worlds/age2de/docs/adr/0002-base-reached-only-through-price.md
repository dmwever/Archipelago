---
status: accepted
---

# A location reaches the base only through its price

Playtest #05 found ages in logic with an unpaid Town Center. The obvious fix was to make the age
climb ask `has_base()` directly. Instead, no location (age, tech, unit, building) and no
prerequisite asks for a base itself. A location pays its price through the easy sources
(`economy.can_pay`), and the base sits on the gathering side of those sources, so a location reaches
the base only by paying for something gathered. The reason is direction: the base (a Town Center,
villagers to train, Houses) is to stop being the only way to have an economy. Later work adds routes
to the easy sources that don't go through a base, and a location gated directly on `has_base()`
would have to be unpicked one rule at a time.

## Considered Options

- **`has_base()` in the age climb.** This was chosen first during #05's grilling and then reversed.
  It closed the gap just as well (every climbable age costs food), but it tied ages to the base for
  good.
- **A paid Town Center (`has_tc`) in the climb.** Rejected: it paid for the Town Center but skipped
  the base's other requirements, such as Joan 3's ground across the water.

## Consequences

- Prerequisites stay structural. `has_reached` (an age as a prerequisite) never pays. What depends
  on it pays its own price.
- Buildings have the same paid and structural pair as ages, techs and units (#17):
  `has_building_structurally` (standing or buildable) never pays, and `has_building` (standing or
  paid for) does. A paid form pays for every building it leans on. A structural form, and every
  question inside the economy (dropsites, market), pays for nothing. That keeps the easy sources
  from asking themselves.
- A defence is part of an economy seed, never free (#23). A standing defence opens no gate: what it
  guards is already the base tier. A built defence (a wall with a tower, a strongpoint, a Dock
  holding a shoreline, more Town Centers) costs route needs of *some*, from a running route, never
  a bank. More Town Centers cost *some* wood and *some* stone wherever they are asked, camps
  included. The base's own Town Center is no strongpoint.
- Guarding boats is part of an economy seed, not a price and not free (#21). The structural form
  of fielding pays for nothing, so the navy that guards the afloat and shoreline tiers is fielded
  structurally, and its wood and gold are route needs of the routes working those tiers
  (ADR-0003): *some*, from a running route, never from a bank.
- The Town Center is paid for by the base, never by an easy source. A standing one is free; a built
  one is paid for by the Town Center items, which the location reaches through its own price.
- A banked pile (`HasResourceAmount`) never pays for a building. It counts the Town Center items,
  which the base has already spent, and it can't add up two buildings. Banks pay only for one-off
  seeds such as a Fishing Ship or a trade seed.
- The structural climb asks for a Town Center structurally, because an age is researched there. The
  base arrives through the age's food cost.
- Trade Cogs are a deliberate non-base economy (#19): cogs to a trade partner's dock bring in easy
  wood and gold with no base. A route to an easy source that reaches no base is not automatically a
  gap. ADR-0003 generalises this: the base is one economy route's economy seed, not the gathering
  side as a whole.
- Follow-ups that apply this: #17 (paying for the buildings a location leans on), #18 (the direct
  `has_base()` left in military and in the defeat rules), #19 (cog trade).
