# 51: In-game checks left over from finished tickets

**Reported:** 2026-10-29, folded together from playtest #04, #11, #50 and item-delivery-cursor 09,
10, 11

**Status:** ready-for-human

**Related:** [#04](04-age-checks-sent-at-start.md), [#11](11-khan-trainable-at-castle.md),
[#50](50-caveman-playtest-remaining-force.md), `worlds/age2de/docs/spec-item-delivery-cursor.md`

## Report

The code for each source ticket is done and tested. What is left can only be checked in game.
Record each result under *Comments*, and open a follow-up ticket for anything that fails.

## Checks

### Ages and the train menu

- [ ] **#04** Joan 1 with `shuffle_ages` on sends no age checks at start.
- [ ] **#11** After regenerating and installing, Genghis 6 shows the Mangudai in Castle slot 1 and
      no Khan anywhere in the train menu.

### Caveman: does the remaining force push through? (#50)

Play each with **caveman on** and **unitsanity on**, with the relevant lines **not** received, so
every non-exempt unit P1 is handed is a Militia. Heroes, escorts, villagers and muster units are
untouched. Each row stays in logic as the third column says until it is tested.

| # | Scenario | Test | In logic until tested | If it fails |
| --- | --- | --- | --- | --- |
| J4-2 | Joan 4 | Five Militia (from the starting Crossbowman, Knight, Man-at-Arms, Monk, Scout Cavalry) and Joan defeat the English Guards | free | gate on whichever starting unit carries the fight, or the trained-military route |
| J5-3 | Joan 5 | With only the Bombard Cannon or the Trebuchet restored, the rest Militia, the army reaches the refugees, the Loyalist Soldiers and Compiègne | `survives_caveman(BOMBARD_CANNON) \| survives_caveman(TREBUCHET_PACKED)` | add the units it needs to that gate |
| J6-2 | Joan 6 | With only the siege restored (the army's Trebuchet or the artillery's Bombard Cannons), the French Army and Artillery capture the Burgundian Town | the same siege gate on `HasAll(French Army, French Artillery)` | add the units it needs |
| J6-4 | Joan 6 | The French Army, cavemanified, takes the English camp's base (`must_steal_base`) | ungated `Has(French Army)` | gate `must_steal_base` on the units it needs |
| A2-1 | Attila 2 | The Scythian Troops beat the Eastern Romans with only the Capped Rams restored (Mangudai and Onager as Militia) | `scythian_troop & survives_caveman(CAPPED_RAM)` | add `MANGUDAI` and/or `ONAGER` |
| A2-3 | Attila 2 | Destroy the Red Town Center (Sofia) with the starting force as Militia | free | gate on `TARKAN`, or the trained route |
| G1-1 | Genghis 1 | Eight Militia (the cavemanified Kereyid riders) slay Ornlu for the Uighurs | free | gate Recruit the Uighurs on `CAVALRY_ARCHER` and/or `LIGHT_CAVALRY` |
| G5-1 | Genghis 5 | Capture the Polish Flag with the starting force as Militia (Mangudai, Mangonel, Scout Cavalry) | free | gate on the unit it needs, or `defeats(Polish)` |

- [ ] J4-2
- [ ] J5-3
- [ ] J6-2
- [ ] J6-4
- [ ] A2-1
- [ ] A2-3
- [ ] G1-1
- [ ] G5-1
- [ ] Every row that fails has a follow-up ticket (or a fix) that gates it as the last column says.

### The spent record (item-delivery-cursor)

- [ ] **09** Spend a trap on one machine, connect from a second machine with an older state file,
      and confirm the trap does not re-fire.
- [ ] **10** Spend a mercenary, run `/install` with the scenario attached, and confirm the mercenary
      stays out of the pavilion and spent traps don't re-fire.
- [ ] **11** Finish a mercenary while reconnecting, and confirm it stays spent and out of the
      pavilion.

## Comments
