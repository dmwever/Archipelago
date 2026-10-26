# Ageipelago (age2de)

The Archipelago world for Age of Empires II: DE campaigns. This glossary covers how the logic
reasons about a scenario: what P1 can field, what beats what, and what the map yields.

## Language

### Scenario

**P1**:
The scenario slot the person playing controls.
_Avoid_: the player, the human, the protagonist

**Player**:
Any other slot in a scenario, P2 to P8, named for what the campaign calls it (a faction or a
colour). Each is an ally or an enemy of P1, or is neutral and ignored by the logic.
_Avoid_: faction, side, player number or colour (as an identity), AP slot (the Archipelago sense)

**Fixed-force scenario**:
A scenario fought only with what it hands P1: no base, no villagers, no economy and no age to
climb. A villager job never counts one.
_Avoid_: no-economy scenario, army scenario

### Economy

**Villager job**:
The form a villager takes while working: Shepherd, Hunter, Lumberjack, Repairer and so on. P1
owns one by having a villager start that work in a scenario, which needs the villagers and the
thing worked in that same scenario. Sheep count only in the base or the open; every other
resource counts wherever it is. The item that permits a job is its **profession**.
_Avoid_: profession (when the job or its location is meant), gatherer type

**Resource scan**:
The count of each resource a scenario's map holds, by area: gold, stone, hunt, sheep, berry
bushes, shore fish, deep fish, oysters, whales and relics. It alone says whether a scenario has a
resource. It counts no trees, so every scenario is taken to have wood; a per-scenario wood limit
means adding a tree count to the scan.
_Avoid_: resource flags, starting resource flags

**Economy route**:
One way P1 brings a resource in: a **producer** (villagers on a job, Fishing Ships, Trade Cogs,
Trade Carts, or something a scenario provides) that **yields** one or more resources once its
**economy seed** is met. A route yields at one of two strengths: **some** (enough to pay an
economy seed once, such as a few villagers chopping with no base) or **at scale** (enough to keep
paying).
_Avoid_: economy (when one route is meant), income, source (unqualified)

**Easy source**:
A route yielding a resource at scale, with its economy seed met. Only an easy source pays a
location's price.
_Avoid_: income, steady supply

**Economy seed**:
Everything a route's producer needs before it starts yielding: resources gathered or banked,
buildings, access such as water or a trade partner's dock, villagers (any number), or a scenario's own
grant. A bundle, not a pile, and particular to its route. Its resources may come from any route
already yielding them, at either strength, so one route can seed the next.
_Avoid_: seed (alone: it is the Archipelago generation seed), seed resources, starting resources
(when the whole bundle is meant)

**Defence**:
A building P1 puts up to hold resources out on the map: a wall with a tower, a strongpoint
(Castle, Fortified Church, Krepost, Donjon, or a second Town Center), or a Dock on a shoreline.
A route needs one only to work ground **at scale**; a route of *some* walks out, takes what it
needs and comes home, so open ground costs it nothing. A defence pays for itself where it is
asked, out of *some* of what it costs, so the stone on open ground can buy the wall that then
holds it. One standing at the start is no defence: what it guards is already the base's ground.
_Avoid_: fortification (when the paid build is meant), the base's Town Center as a strongpoint,
guard (that is the trade sense, below)

**Base**:
A Town Center P1 can turn out villagers from: one standing at the start, or one P1 puts up, paid
for by the starting Town Center resources and stood on ground P1 can reach. It also takes the food
to train the first villagers and the Villager Line, even where villagers already stand. The base
is the economy seed of villagers gathering at scale: one route's economy seed, not the economy
itself.
_Avoid_: Town Center (when the base is meant), camp, having villagers, economy

**Trade partner**:
A player whose market or dock P1 can actually trade with: an ally, or an opponent whose market or
dock is left standing and is either undefended, guarded by ruling, or belongs to an opponent P1 can
defeat. A market that exists but is out of practical reach is not a trade partner's.
_Avoid_: trading ally (when an opponent may be meant)

**Guard**:
Holding the trade route to one opponent's market or dock open against its owner, instead of
defeating the owner first. Ruled per player and building, hand-written per scenario, and paid in
routes of *some*: a guard is never paid at scale, so it can open a route that has no base behind
it. A guarded building opens on its guard or on its owner's defeat, whichever comes first.
_Avoid_: escort, protect, defend (when the trade route is meant)

**Partner trade**:
Gold or wood earned by sending trade carts to a trade partner's market or trade cogs to its dock.
One thing whichever route it takes. Trade is not gathering and asks no base itself: cogs bring
their own wood home, and carts run on wood from any easy source.
_Avoid_: ally trade, trade cogs, trade carts (when both are meant), trading

**Market trade**:
Buying and selling resources at P1's own market.
_Avoid_: ally trade, bartering

### Combat

**Opponent**:
A player who is an enemy of P1.
_Avoid_: enemy faction

**Main opponent**:
An opponent significantly more powerful than the rest of the scenario's opponents. Its market and
dock are not a trade partner's unless one is undefended or guarded by ruling. Not necessarily the
opponent whose defeat wins the scenario.
_Avoid_: boss, final enemy, victory target

**Defeat**:
P1 can overcome an opponent's army and take its ground. A defeated opponent's buildings may still
be standing.
_Avoid_: beat, kill

**Counter**:
A unit line that the logic accepts as beating a target line on its own, by killing it, or for a
faith line by converting it.
_Avoid_: answer, check, beat

**Sponge**:
A unit that beats a target by soaking its fire rather than killing it; it counts only when
fielded alongside a military line that deals the damage. The **Ram** is the only sponge.
_Avoid_: tank, meat shield

**Ram**:
A building-breaker that cannot fight soldiers, only buildings and siege: the Battering Ram line,
or the Armored Elephant line that stands in for it among elephant civilisations.
_Avoid_: siege (when only the ram is meant)

**Faith line**:
A unit line that converts rather than kills: the Monk and the Missionary.
_Avoid_: monk line (when the Missionary is meant too), religious units

**Anti-unit siege**:
The clumsy siege that fights armies: the mangonel, bombard cannon and rocket cart lines. The
scorpion is deliberately not one; it is easy enough to use that it counts as an ordinary counter.
Distinct from building-breaking siege such as rams and trebuchets.
_Avoid_: siege (unqualified, when only anti-unit siege is meant)

### Locations

**Registered location**:
A location the current scenario can check: a scenario objective, or a global tech, building, unit
or age location that is still achievable in this scenario. A global location already granted at
start, or out of the civ's reach, is not registered here, even when another scenario checked it.
A checked location the server reports that is not registered is expected, not an error.
_Avoid_: existing location, known location

### Units

**Unit row**:
The entry the installed unit table holds for one unit: which location owning it checks, which
line it belongs to, which items unlock it, and whether any civilisation in the seed can train it.
One row per unit, not per line.
_Avoid_: unit entry, unit record

**Granted-only row**:
A unit row for a unit no civilisation in the seed can train, so only a scenario or a mercenary
muster hands one over. It has no line and no items, which makes it unlocked from the start;
owning one is still its own check. Heroes and escorts are always granted-only. Being granted-only
says nothing about whether the game has a train button for the unit, and a granted-only unit is
never one the player may train.
_Avoid_: hero row, untrainable row (that is the per-civ flag, a different thing)
