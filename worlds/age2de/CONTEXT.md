# Ageipelago (age2de)

The Archipelago world for Age of Empires II: DE campaigns. This glossary covers how the logic
reasons about a scenario: what P1 can field, what beats what, and what the map yields.

## Language

### Logic

**Rule**:
One condition the logic asks, and the `Rule` object that holds it: a leaf such as `Has`, or a tree
of them joined by `&` and `|`, usually under a `Named` label. Where several are Or'd together each
one is a rule - in prose, in docstrings, and in the identifiers holding them (`rules`, never
`ways`). /explain shows them as the lines a question opens to.
_Avoid_: way, ways

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
advance to. A villager job never counts one.
_Avoid_: no-economy scenario, army scenario

**Scenario item**:
An item that hands P1 objects already placed on the scenario's map. Objects the original campaign
leaves to Gaia stay Gaia's until it arrives, cannot be captured, and are never counted as any
**player**'s.
_Avoid_: grant, gift, reinforcement, granted (in this sense)

**Mercenary**:
An item that, inside its own scenario, is a **scenario item**: it hands P1 units already in the
scenario, and those units are cavemanified like any other P1 unit (the villagers excepted). This
is the only sense in which a mercenary counts in logic.
_Avoid_: muster (that is the pavilion spawn, below)

**Muster**:
The one-time spawn a mercenary's camp at the pavilion produces. It is never counted in logic, and
the units it spawns are kept from being cavemanified.
_Avoid_: mercenary (when the spawn is meant), mercenary units (when counting what logic can rely
on)

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
One route by which P1 brings a resource in: a **producer** (villagers on a job, Fishing Ships, Trade Cogs,
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
already yielding them, at either strength, so one route can seed the next. A route's needs are its
operating input and never its capital: they say what must already be yielding before the producer
runs, and never buy the building it stands in, which does not exist yet. That building is capital,
funded from outside the economy by a **seed item** or by *some* wood. An age the producer waits on is
capital the same way, at the age's one price (see **Age price**).
_Avoid_: seed (alone: it is the Archipelago generation seed), seed resources, starting resources
(when the whole bundle is meant)

**Age price**:
What reaching an age costs P1, the same wherever the age is asked, whether as a location or as
something another rule stands on: Feudal is *some* food or its seed item, Castle is food at scale
and *some* gold, Imperial is food and gold at scale. An age the scenario starts in or past costs
nothing, which is where a Castle Age economy opens. Nothing may ask an age without its price.
Reaching an age also pays for the advance into it: a Town Center, and the age-up requirement of the
age before, each standing or paid for. An age started in or past needs no advance.
_Avoid_: age cost (the in-game numbers), age-up requirement (the two buildings), climb (say advance)

**Seed item**:
An item granting the starting resources one building or age costs, so it is paid for from
outside the economy: the Town Center items and the villagers' food for the base, one wood item
each for the Lumber Camp, Mule Cart, Dock and Market - the buildings that can open an economy from
nothing - and the Feudal Age Food for the age trade, Fish Traps and market trade wait on. A building that only opens a resource inside an economy already running (Mining Camp,
Mill, Folwark, Monastery) has none; its route needs *some* wood instead. A building standing at
the start asks for no seed item, and one is pooled only where a route under the seed's options can
use it. A building whose seed item is not pooled is funded like a Mill: a Dock with partner trade
off is a plain dropsite whose villager routes need *some* wood.
_Avoid_: Town Center resources (when every seed item is meant), starting resources, seed (alone)

**Defence**:
What P1 builds or trains to hold resources out on the map: a wall with a tower, a strongpoint
(Castle, Fortified Church, Krepost, Donjon, or a second Town Center), a Dock on a shoreline, or,
on open ground only, an army of any land military line.
A route needs one only to work ground **at scale**; a route of *some* walks out, takes what it
needs and comes home, so open ground costs it nothing. A defence pays for itself where it is
asked, out of *some* of what it costs, so the stone on open ground can buy the wall that then
holds it. The Castle is the exception: it always needs easy stone, except where it holds stone,
which *some* stone still buys. A defence of an age the scenario starts below also pays the advance
into it (see **Age price**), out of the economy that runs without a defence. An army pays *some* of
a building to train it in, unless one stands. One standing at the start is no defence: what it guards is already the base's ground.
Nor is an army P1 starts with or is granted: that is the scenario's plan, not a garrison.
_Avoid_: fortification (when the paid build is meant), the base's Town Center as a strongpoint,
guard (that is the trade sense, below)

**Base**:
A Town Center P1 can turn out villagers from: one standing at the start, or one P1 puts up, paid
for by the starting Town Center resources and stood on ground P1 can reach. It also takes the food
to train the first villagers and the Villager Line, even where villagers already stand. The base
is the economy seed of villagers gathering at scale: one route's economy seed, not the economy
itself. Its Town Center is also a dropsite, so a route on the base never asks again for a dropsite
the Town Center already is. The base buys the first villagers only; training more is *some* food that every route
standing on the base needs, and the room for them is **housing**.
_Avoid_: Town Center (when the base is meant), camp, having villagers, economy

**Housing**:
The room P1 has to field units past those already standing. It is a resource of the economy
routes, but never an item resource. *Some* housing is room for a unit or a few, and only a
scenario grants it. Housing at scale comes from a Houses route, paying for buildable Houses with
*some* wood, from a civilisation that builds no Houses, for nothing, or from a scenario grant that
fills the population limit. A fixed-force scenario trains nothing and asks none. A unit P1 trains needs
*some* housing; units at scale need it at scale: a route whose producer is trained, and every
force P1 fields. A unit already standing needs none.
_Avoid_: House (when the room is meant), population, pop cap

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
By ruling, a guard may instead be another way its owner lets P1 trade, such as an alliance; that
asks whatever the alliance costs, not routes of *some*.
_Avoid_: escort, protect, defend (when the trade route is meant)

**Basic guard**:
The guard that asks no counters to the owner's forces. For a dock, P1 can keep some navy on the
water, the same ability that protects P1's own boats at sea. For a market, P1 can hold open ground
with some army; fortifications do not count, since the carts' route moves. Either is paid in routes
of *some*.
_Avoid_: naval guard (when counters to the owner's navy are meant), escort

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

**Cavemanify**:
What caveman does to a unit P1 owns: replace it with the best tier of its own line P1 has
unlocked, or a Militia if none is. Items for the line raise it again, but never past its
**original unit**. Every unit of P1's is subject to it, trained or not; a trained unit stays as it
is only because its items had to arrive before it could be trained. Which units are exempt is
**caveman-exempt**, below.
_Avoid_: knockdown, downgrade

**Original unit**:
The unit a cavemanified unit was before caveman replaced it. Items for its line raise it back up
to its original unit, never past it.
_Avoid_: ceiling

**Restore**:
Bring a cavemanified unit back to its **original unit**: its line's items have arrived and, when
the seed shuffles it, so has the upgrade tech that makes it. A unit the scenario hands P1 counts
toward a rule under caveman only once it can be restored.
_Avoid_: un-caveman, recover, survive (the code's `survives_caveman` is "caveman is off, or it can
be restored")

**Caveman-exempt**:
A unit row cavemanify leaves alone. Two code paths set it, and only one of them is named for it:
`UnitData.is_caveman_exempt` covers the villager lines, while `UnitData.owned_type_row` writes
`exempt=True` outright and never consults it — which is how heroes, escorts, the villager job
rows and the granted-only rows come to be exempt. Editing `is_caveman_exempt` therefore moves
only part of the set.

Measured, not inferred ([#46](../../.scratch/playtest/spikes/46/README.md) run 2, all 107 rows of
one seed's table probed on land and on water): 40 rows exempt — 22 villager rows and 18
granted-only rows — and a 41st left alone because it *is* the target, the Militia. **No ship and
no cart is exempt.** Every other row becomes a Militia created on the tile the original stood on,
water included; nothing is destroyed.
_Avoid_: immune (that is the mercenary pavilion's separate protection, `MercenarySpawn.xs`)
