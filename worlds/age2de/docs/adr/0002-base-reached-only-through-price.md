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

- Prerequisites stay structural. `has_reached` (an age as a prerequisite) and `has_building`
  (standing or buildable) never pay. What depends on them pays its own price.
- The structural climb asks for a Town Center structurally, because an age is researched there. The
  base arrives through the age's food cost.
- A route to an easy source that reaches no base (Trade Cogs, #19) may be a deliberate non-base
  economy, not automatically a gap.
- Follow-ups that apply this: #17 (building costs on the buildable path), #18 (military's remaining
  direct `has_base()`), #19 (cog trade).
