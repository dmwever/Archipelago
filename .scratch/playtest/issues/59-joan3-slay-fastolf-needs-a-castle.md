# 59: Slay Fastolf is in logic without the castle that makes Fastolf appear

**Reported:** 2026-10-30, playtesting

**Status:** needs-triage

## Report

In game, slaying Fastolf requires destroying one English castle first.

## The trigger chain

Read from `AP_Joan_3.aoe2scenario`:

| trigger | |
| --- | --- |
| `t11 [D1] Destroy 1st Castle` | **IF** English (player 3) own fewer than **3** Castles (unit 82) |
| | **DO** `activate_trigger 1` |
| `t1 [D9] Fastolf Attacks` (starts disabled) | **DO** `create_object 652` - Fastolf - plus his escort, and set variable 2 to 1 |
| `t46 AP Kill Fastolf` | **IF** own fewer than 1 of unit 652, **AND** variable 2 == 1 |
| | **DO** `script_call KillFastolf();` |

Fastolf does not exist on the map at start. He is created only once the English are down to two
castles, and `AP Kill Fastolf` additionally requires variable 2, which only that spawn sets. So
destroying one English castle is a hard prerequisite for the location, not a convenience.

## What logic says

`rules/joan_rules/joan_3.py`:

```python
self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_SLAY_FASTOLF], can_defeat_fastolf)
```

`can_defeat_fastolf` is `defeats(JOAN3_FASTOLF)` alone. Destroying a castle is defeating the
English - `Joan3Rules` says so itself in a comment on the castle locations - and those two
defeat rules do not imply one another (`logic/joan/joan_3.py`):

| player | defeat rule |
| --- | --- |
| `JOAN3_ENGLISH` | `can_cross_ocean & has_siege & counters(MILITIA) & counters(LONGBOWMAN) & counters(KNIGHT)` |
| `JOAN3_FASTOLF` | `can_cross_ocean & counters_building() & counters(BATTERING_RAM) & counters(SCOUT_CAVALRY) & counters(KNIGHT)` |

`has_siege` and the Longbowman counter are required for the English and not for Fastolf, so a
state can satisfy `defeats(FASTOLF)` while unable to take a castle. In that state logic calls
Slay Fastolf reachable and the game never spawns him.

The same file already models this dependency one step further along:

```python
self.world.set_rule(self.locations[JOAN3_DESTROY_TWO_CASTLES], can_defeat_english & can_defeat_fastolf)
```

Two castles needs both, because Fastolf is attacking by then. Slay Fastolf needs both for the
mirror-image reason, and only asks for one.

## The fix

```python
self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_SLAY_FASTOLF],
                    can_defeat_english & can_defeat_fastolf)
```

Severity: a location reachable in logic and not in game, so it can strand a seed.

## Minor, same line of code

`locations/Locations.py:136` spells the location **"Slay Fastoff"**. It is the player-facing
name.

## Comments
