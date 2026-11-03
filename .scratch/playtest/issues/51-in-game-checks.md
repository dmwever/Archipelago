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

- [x] **#04** Joan 1 with `shuffle_ages` on sends no age checks at start. **Passed**, see Comments.
- [x] **#11** After regenerating and installing, Genghis 6 shows the Mangudai in Castle slot 1 and
      no Khan anywhere in the train menu. **Passed**, see Comments.

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

- [x] J4-2 - **passed**; see Comments
- [x] J5-3 - **passed**; see Comments
- [x] J6-2 - **passed**; see Comments
- [x] J6-4 - **passed**; see Comments
- [x] A2-1 - **passed**; see Comments
- [x] A2-3 - **failed**, fixed; see Comments
- [x] G1-1 - **failed**, fixed; see Comments (an earlier pass here was wrong)
- [x] G5-1 - **passed**; see Comments
- [x] Every row that fails has a follow-up ticket (or a fix) that gates it as the last column says.

### The spent record (item-delivery-cursor)

- [ ] **09** Spend a trap on one machine, connect from a second machine with an older state file,
      and confirm the trap does not re-fire.
- [ ] **10** Spend a mercenary, run `/install` with the scenario attached, and confirm the mercenary
      stays out of the pavilion and spent traps don't re-fire.
- [ ] **11** Finish a mercenary while reconnecting, and confirm it stays spent and out of the
      pavilion.

## Comments

### Fork harness (2026-10-29)

Ten throwaway scenarios put each check in front of the player without playing up to it:
`.scratch/playtest/spikes/pt51/` (`build.py`, `read.py`, `clean.sh`, `pt51.yaml`, `README.md`).
Each is a fork of the live AP scenario with map, AI, civs, techs and grant triggers intact;
only the start position and the item flags change. One seed serves all ten.

Two corrections to this ticket's own wording, found while building it:

- **J4-2 says "Five Militia".** Joan 4's start is 18 units plus Joan (6 Knight, 4 Man-at-Arms,
  4 Crossbowman, 2 Monk, 2 Scout), so the cavemanified force is far stronger than the row reads.
- **"The rest Militia" is approximate.** `cavemanTarget` (`Caveman.xs:151`) walks down to the
  lowest *unlocked* tier in the same `lineId` and only falls back to `CAVEMAN_MILITIA` when
  nothing qualifies, so Light Cavalry most likely lands on Scout Cavalry. That affects G1-1's
  four Light Cavalry and the whole Tayichi'ud tribe.

Confirmed while checking those: mercenary soldiers spawned at the pavilion are
`MarkUnitCavemanImmune` (`MercenarySpawn.xs:77`), but none of these eight rows takes that path.
A2-1's troops are pre-placed Gaia units freed by a `remove_object` over the tree wall, and
G1-1's tribes are `change_ownership` from the tribe player. Both become ordinary P1 units and
are cavemanified. All eight rows stand as written.

### A2-3 result (2026-10-29)

**Failed.** Under caveman the Attila 2 starting force cannot destroy Sofia's Red Town Center.
Played on `PT51_A23`.

Fixed as the row's last column says. `ATT2_RED_TC` was unruled; it is now gated in
`rules/attila_rules/attila_2.py`:

```python
can_raze_red_tc: Rule = (self.logic.units.survives_caveman(Age2UnitData.TARKAN)
                         | self.has_military)
```

`survives_caveman` is `NOT_CAVEMAN | can_restore(unit)`, so with caveman off the location stays
free; with caveman on it asks for the Tarkan line restored or a trained military. Pre-commit
client subset plus the logic canaries: 105 passed, 276 subtests.

### G1-1 result (2026-10-29, corrected)

**Failed.** An earlier note here recorded a pass; that was wrong. The Genghis 1 starting force
alone - 4 Cavalry Archers and 4 Light Cavalry, cavemanified - does not kill the 400 HP Ornlu.
At least one tribe is needed, and it can only be the **Kereyid (blue)** tribe:

| Tribe | Why it cannot be the one |
| --- | --- |
| Ungirrad (grey) | requires the Kereyids first |
| Naiman (green) | requires killing troops |
| Tayichi'ud (purple) | requires killing troops |
| Uighur (cyan) | requires killing Ornlu, so it is circular |

Gated in `rules/genghis_rules/genghis_1.py`:

```python
can_slay_ornlu: Rule = NOT_CAVEMAN | Has(Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name)
```

set on `GEN1_RECRUIT_UIGHURS`, inside the `all_scenario_branches` arm because that location is
`OBJECTIVE_BRANCHING_ALL` and does not exist otherwise. Under "any" branching the Recruit
One/Two/Three Tribes locations can be satisfied by other tribes, so they need no Ornlu gate.

The gate is caveman-conditional rather than a bare `Has`: without caveman the starting eight
handle the wolf, and an unconditional gate would tighten the fill for no reason.

`GEN1_VICTORY` already required the Kereyids through `has_monk`, so victory was never at risk.

Pre-commit client subset plus the logic canaries: 105 passed, 276 subtests.

### G5-1 harness change (2026-10-29)

`PT51_G51` no longer teleports. The row is a walk up from the Genghis 5 start at (133,58) to the
Polish Flag at (111,130), so surviving the approach is part of what is being asked, the same way
J5-3 is. Not yet played.

### J4-2 result (2026-10-29)

**Passed.** The cavemanified Joan 4 starting force plus Joan defeats the English Guards. Played
on `PT51_J42`. The row stays free in logic; no gate on Defeat the English Guards.

Note on the row's wording: the force is 18 units plus Joan (6 Knight, 4 Man-at-Arms,
4 Crossbowman, 2 Monk, 2 Scout), not the "five Militia" the table says. Five is the number of
unit *types*, not units.

### G5-1 result (2026-10-29)

**Passed.** The cavemanified Genghis 5 starting force walks up and captures the Polish Flag.
Played on `PT51_G51` with no teleport, from the start at (133,58) to the flag at (111,130).
The row stays free in logic; no gate on Capture the Polish Flag.

### A2-1 result (2026-10-29)

**Passed.** The Scythian Troops beat the Eastern Romans with only the Capped Rams restored.
Played on `PT51_A21`, which delivers Battering Ram Line (369) and nothing else, so the 3 Capped
Rams survive caveman while the 9 Mangudai and 1 Onager drop. The gate
`scythian_troop & survives_caveman(CAPPED_RAM)` holds as written; no change needed.

This fork was deliberately left at its original per-player ages, so the result carries no
Dark Age caveat.

### J6-2 and J6-4 results (2026-10-29)

**Both passed.** The French Army plus Artillery take the Burgundian Town, and the French Army
alone takes the English camp base. The gates hold as written; no change needed to
`can_siege_town` or to `must_steal_base`.

**Caveat, and it cuts against the result.** `PT51_J62` and `PT51_J64` were played with every
playable slot set to Dark Age. That was done so caveman's output renders as Militia rather than
Man-at-Arms, but aoe2kit's `scenario.starting_age` writes all slots, not just P1
(`writer.go`: `for i := range ages { if i < f.PlayerCount }`), and the kit exposes no per-player
write.

What that does and does not change:

- **Unchanged**: every target. The Burgundian Town's 36 walls, 23 Crossbowmen, 8 Watch Towers
  and 8 Coustilliers, and the English camp's 124 walls, 44 Longbowmen and 13 Knights are all
  map-placed and keep their identity.
- **Changed**: what Burgundy and the English can train and research once the fight starts. Both
  are live AI towns in the real scenario, so a long fight there is easier here than it would be
  at their shipped ages.

Reviewed and accepted by the maintainer on 2026-10-29: both rows pass outright, no re-run at
shipped ages. Neither fight was close enough for the reinforcement difference to decide it.

### J5-3 result (2026-10-29)

**Passed.** With only the Bombard Cannon line restored and the rest cavemanified, the Joan 5
army reaches the refugees, the Loyalists and Compiegne. Played on `PT51_J53`, no teleport, so
the approach was part of it. The gate
`survives_caveman(BOMBARD_CANNON) | survives_caveman(TREBUCHET_PACKED)` holds as written.

Passed on the maintainer's call for both halves of the Or, not only the Bombard Cannon arm that
was played. The Trebuchet is the stronger siege piece of the two against what the approach puts
in the way, so the arm that was tested is the harder one.

### Fight rows: all eight done (2026-10-29)

| Row | Result |
| --- | --- |
| J4-2 | passed, stays free |
| J5-3 | passed, gate holds, both arms |
| J6-2 | passed, gate holds |
| J6-4 | passed, ungated `Has(French Army)` holds |
| A2-1 | passed, gate holds |
| A2-3 | **failed**, gated on `survives_caveman(TARKAN) \| has_military` |
| G1-1 | **failed**, gated on `NOT_CAVEMAN \| Has(Kereyid Tribe)` |
| G5-1 | passed, stays free |

Six pass, two fixed. Both fixes are in the working tree, uncommitted, each run against the
pre-commit client subset plus the logic canaries.

### #04 result (2026-10-29)

**Passed**, engine-verified. Played `PT51_P04` and decoded the sidecar against
`ledgers/P04.json`: 13 of 13 assertions pass, footer `424242` present, so the run completed.

| field | value | meaning |
| --- | --- | --- |
| `AP_SHUFFLE_AGES` | 1 | shuffle_ages on, so the check means something |
| `apVanillaAge` | 27 | Joan 1 is Castle |
| `apMaxAge` | 28 | |
| `feudalRegistered` | **0** | granted by the climb, not registered |
| `castleRegistered` | **0** | granted by the climb, not registered |
| `imperialRegistered` | 1 | above vanilla and at or below max, so registered |
| Feudal tech state | 3 | Done |
| Castle tech state | 3 | Done |
| Imperial tech state | -1 | Disabled, because `InitAges` locks an age it registers |

Feudal and Castle being **done and still unregistered** is the fix working: an age the vanilla
climb grants is never registered, so `ShuffleAgesUpdate` has nothing to send for it on its first
tick. Imperial is the control - it is above the vanilla age, so it is registered and locked.

The Imperial tech state was wildcarded in the ledger. `-1` is `cTechStateDisabled` and follows
from `lockAge`, so it is consistent rather than an unverified slot.

Harness note: DE names the sidecar `default1.xsdat` for a loose scenario, not after the
scenario, and every run truncates it. `read.py` now resolves that and checks the row id in the
header, so reading the wrong run reports itself instead of passing quietly.

### #11 result (2026-10-29)

**Passed.** Played `PT51_G6C`: the Mangudai occupies Castle slot 1 and no Khan appears in the
train menu.

Backed by the installed unit data for this seed, which is what the fix actually changes:

```
addUnit(604, 1275, -1, 25, 0, -1, 1);
addUnitUntrainable(1275, 17);   Huns
addUnitUntrainable(1275, 2);    Franks
addUnitUntrainable(1275, 12);   Mongols
```

Two things close it:

- **The Khan is a hero.** Its row comes from `owned_type_row`, so `lineId` is -1, it is
  caveman-exempt, and it carries no item at all - `addUnitItem(604, ...)` does not appear. There
  is no Khan item to receive; the unit becomes P1's by being owned.
- **It is untrainable for every civ the seed can play.** `all_civs_untrainable()` returns every
  civ in `self._civs`, which is the campaign civs in the seed. Three lines is full coverage here,
  not a partial write.

Correction to the harness: `PT51_G6C` gives `AP_GENGHIS_6_SUBOTAIS_ARMY` (4019) ten seconds after
the Mangudai Line, on the theory that it was "the Khan item". It is not - it is a mercenary, and
giving it seats a muster rather than unlocking anything. The delayed grant is harmless but tests
nothing; the spawned Khan at (94,45) is what proves the row is live.
