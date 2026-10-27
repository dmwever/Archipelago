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
- A defence is never free, and pays for itself where it is asked (#23). A standing defence opens no
  gate: what it guards is already the base tier. A built defence (a wall with a tower, a
  strongpoint, a Dock holding a shoreline, more Town Centers) asks for *some* of each resource it
  costs, read off `Age2BuildingData.cost`, in the same expression that asks whether P1 can build it
  at all. That is not a price in ADR-0002's sense — a price is an easy source — and it is not a
  bank. More Town Centers pay inside `can_build_multiple_tc`, so the strongpoint, the shoreline and
  the camps all inherit it. The base's own Town Center is no strongpoint.
- **Only ground worked at scale has to be held** (#23). A route of *some* takes what it needs off
  open ground and comes home, so it asks no gate; a route at scale has to hold the ground, so it
  does. This is what lets a resource pay for its own defence — *some* stone off open ground buys
  the wall that holds the same ground at scale — and it is why the gates need no parameter.
- Guarding boats is the same, not a price and not free (#21, amended by #23). The structural form
  of fielding pays for nothing, so the navy that guards the afloat and shoreline tiers is fielded
  structurally and pays for *some* of each line's own wood and gold in the same expression.
- Holding open ground with an army is the same (#29). Any land military line P1 can train holds
  open ground at scale, for every resource there, beside a built defence, paying *some* of the
  line's own cost in the same expression. The base is still asked. A starting or granted army
  holds nothing: it is the scenario's own plan, not a garrison. An army does not hold a shoreline.
- The buildings an economy route stands on are funded from outside the economy (#24), because a
  route's needs are its operating input, never its capital. A building which can open an economy
  from nothing - the Lumber Camp, Mule Cart, Dock and Market - is funded by a seed item, in the
  shape of the Town Center items. One which cannot - the Mining Camp, Mill, Folwark and Monastery -
  is funded by *some* of its cost: its route needs *some* wood, which the fixpoint takes from a
  different route. A standing one is free, and the Town Center branch of a dropsite carries no
  funding, so each villager route of *some* is one route per dropsite, and one per funding state
  of that dropsite (#30): a route's needs are flat and the fixpoint reads them without a state, so
  "free where it stands, charged where it is built" cannot be one route with a conditional need.
  A funded camp is therefore two routes, standing and built, whose leaves are the two halves of
  `has_building_structurally`. A seed item is pooled only
  where a route that would otherwise fund itself needs it; where it is not, the building falls
  back to the second kind, so a Dock with partner trade off is funded like a Mill.
- The Town Center is paid for by the base, never by an easy source. A standing one is free; a built
  one is paid for by the Town Center items, which the location reaches through its own price.
- A banked pile (`HasResourceAmount`) never pays for a building. It counts the Town Center items,
  which the base has already spent, and it can't add up two buildings. Banks pay only for one-off
  seeds such as a Fishing Ship or a trade seed. The one exception is the Mule Cart's food (#24):
  its seed item carries the wood, and a food need would make its hunt route need what it yields.
  The cog route's wood bank excludes the Dock's seed item, which is already buying that Dock.
- The structural climb asks for a Town Center structurally, because an age is researched there. The
  base arrives through the age's food cost.
- Trade Cogs are a deliberate non-base economy (#19): cogs to a trade partner's dock bring in easy
  wood and gold with no base. A route to an easy source that reaches no base is not automatically a
  gap. ADR-0003 generalises this: the base is one economy route's economy seed, not the gathering
  side as a whole.
- Follow-ups that apply this: #17 (paying for the buildings a location leans on), #18 (the direct
  `has_base()` left in military and in the defeat rules), #19 (cog trade), #30 (the funded camps
  that went on charging for a standing one).
