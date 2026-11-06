# 78: In-game checks left over from finished tickets, round 2

**Reported:** 2026-11-06, folded together from playtest #58, #60, #66, #68, #70, #71, #72,
#73 and #74

**Status:** ready-for-human

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

- [ ] **#73** Genghis 5, with caveman on, unitsanity `all`, techsanity `all`, the Hermit Monks
      mercenary and the Leitis Line item: the ten Elite Leitis are not cavemanified.

### Scenario triggers

- [ ] **#58** Joan 3 with caveman on: once the boats scenario item has arrived and object 679 is
      visible, `AP Give Boats` creates two Transport Ships for P1 at (14,85) and (15,85).
      `[D0] Finding Boats` shows only its message.
- [ ] **#66** Attila 3: both gold tributes, including `AP Give Red TC Gold`, take from player 4,
      and P1 receives the full amount.
- [ ] **#68** Joan 5: the six refugees reaching Compiegne without Joan does not win. Joan reaching
      Compiegne as well does.
- [ ] **#70** Joan 6 on Easy, and on Easy and Moderate: the Bombard Cannons and the Packed
      Trebuchet spawn as Gaia inside the French Artillery and French Army areas, and the AP grants
      pick them up.
- [ ] **#71** The Attila 5 Deathmatch item pays its resources only inside Attila 5. If it arrives
      while P1 is in another scenario, nothing is paid there, and it pays once P1 reaches Attila 5.

### Victory threats (#60)

- [ ] Genghis 3: a Jin Wonder foundation reveals about 10 tiles around it.
- [ ] Genghis 3: on completion, the announcement and on-screen timer appear. The timer line reads
      `<colour>Jin Wonder <TIMER>` and stands in for the objective line.
- [ ] Destroying the Wonder clears the timer and objective. A rebuilt Wonder restarts the cycle.
- [ ] Letting the countdown run out defeats P1.
- [ ] Attila 6: two Wonders standing at once show two independent timers.
- [ ] Attila 6: researching Atheism mid-countdown adds 100 years to every running timer.
- [ ] Attila 6: defeating a city clears its Wonder's countdown even if the Wonder still stands.
      Its "Prevent or Destroy" and "Defeat" locations still credit.

### Upgrade locations (#72)

Run in a techsanity seed.

- [ ] Researching an upgrade whose tech item is already held marks the upgraded tier's unit row
      and sends its location on the next Unitsanity pass. It does not wait for another research,
      another tech item, or a new unit.
- [ ] Receiving the tech item for an upgrade that is already researched still behaves as before.
- [ ] Siege Ram (location 363) and Siege Onager (location 376), item first and research second.
- [ ] One non-siege tier-2 upgrade in the same seed, to confirm the fix is not siege-specific.

### Upgraded unit tiers (#74)

The `tier == 0` gate in `setUnitDisable` is a **candidate, not a proven fix**. Spike questions
Q1 to Q4 in [`spikes/74/README.md`](../spikes/74/README.md) decide whether it is the answer. Run
those first. Use `unitsanity_items: unit_line` throughout.

- [ ] Spike Q1: Mongols' Camel Rider still appears without an enable.
- [ ] Spike Q2: the Barracks shows Pikeman when Pikeman is researched before the Spearman line item
      arrives, and also when it is researched after. Run with techsanity off and on.
- [ ] Spike Q4: with Militia locked, researching Man-at-Arms does not let the player train
      Man-at-Arms.
- [ ] A line item received in a scenario that opens at or above an upgraded tier's age does not
      make that upgraded tier trainable.
- [ ] The base tier of that line is still trainable as soon as its own age is reached.
- [ ] Once the upgrade is applied, the upgraded tier becomes trainable without a further item.
- [ ] All of the above also holds with techsanity off, where the upgrade tech is researched
      normally and no tech item exists.
- [ ] Behaviour does not depend on registration order: check an upgrade-first line (skirmisher)
      and a base-first line (spearman).
- [ ] Under caveman, an upgrade tech below the scenario's vanilla age is withheld, and its unit
      tier stays untrainable.
- [ ] Spike Q3, fresh Joan 4 start (not the old save): the Archery Range offers Skirmisher, the
      Dock offers Galley and Demolition Raft, and each upgrade's research button is present and
      unresearched.

## Comments
