---
status: accepted
---

# The economy is a set of routes, resolved together

Playtest #19 asked what the base pays for. The answer was nearly everything: every easy source
asked for a base, directly or through wood chopped with one, so the base was the economy. Instead,
the economy is a set of **economy routes**. Each has a producer, the resources it yields, a strength
(**some**, enough to pay an economy seed once, or **at scale**, enough to keep paying), and an
**economy seed**: the bundle it needs before it yields. The base is one route's economy seed, that
of villagers gathering at scale. An easy source is a route yielding at scale with its economy seed
met, and only an easy source pays a location's price (ADR-0002).

An economy seed's resources may come from **any** route already yielding them, at either strength,
so one route seeds the next: Lumberjacks with no base yield some wood, which seeds Trade Cogs, whose
wood at scale seeds Fishing Ships. Routes therefore ask one another in cycles (a cog yields the wood
a cog needs), which a chain of rules asking rules cannot express: `ScenarioQuestion` fails loudly on
a question that asks itself. So the routes of a scenario are worked out together, from the state:
start from the routes whose economy seeds are met without any route, and keep switching on any route
whose economy seed the running routes cover, until nothing changes.

## Considered Options

- **Economy seeds take only leaf gathering, banks and scenario grants.** No cycles, and plain rules
  suffice, but cog wood could never seed Fishing Ships.
- **Routes in an authored order, each seeded only by the layers below.** No cycles either, but the
  order has to be written and kept, and every new route has to find its place in it.

## Consequences

- The Trade Cog is the only route an economy seed of *some* can start, so it is the only way to an
  economy without a base. Every other at-scale route asks for a base or for wood at scale.
- Trade Carts and Trade Cogs are resource bootstraps: given wood at scale, carts turn some gold into
  gold at scale.
- A banked pile is *some* only for an economy seed whose authored amount it covers
  (`TRADE_SEED_*`).
- Relics yield only *some* gold.
- The villager count never matters: any villagers gather *some*; scale is the base's job.
- Local start still aims for a base.
