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

### Economy

**Trade partner**:
A player whose market or dock P1 can actually trade with: an ally, or an opponent whose market or
dock is left standing and is either undefended or belongs to an opponent P1 can defeat. A market
that exists but is out of practical reach is not a trade partner's.
_Avoid_: trading ally (when an opponent may be meant)

**Partner trade**:
Gold or wood earned by sending trade carts to a trade partner's market or trade cogs to its dock.
One thing whichever route it takes.
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
dock are not a trade partner's unless one is undefended. Not necessarily the opponent whose defeat
wins the scenario.
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
