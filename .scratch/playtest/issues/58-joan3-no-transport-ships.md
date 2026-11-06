# 58: Joan 3's Transport Ships never spawn, because caveman eats the boats that trigger them

**Reported:** 2026-10-30, playtesting

**Status:** done (in-game checks in #78)

## Report

Joan 3, The Cleansing of the Loire, is supposed to have Transport Ships. They never appear.

Cause, from the reporter: caveman. The other boats are removed and replaced.

## The chain

The two transports are not placed on the map in any version, vanilla included. They are created
at runtime by `[D0] Finding Boats`:

| | |
| --- | --- |
| condition | `Capture Object`, **unit_object 679** |
| effect | "With these ships, we can cross the Loire River..." |
| effect | `create_object` **545 Transport Ship** for P1 at (14,85) |
| effect | `create_object` **545 Transport Ship** for P1 at (15,85) |

Object **679** is one of the two Gaia `RMSHP` Demolition Ships at (14.5,88.5).

Under caveman that object does not survive long enough to satisfy the condition:

1. `AP Give Boats` change_ownerships refs 679 and 680 from Gaia to P1.
2. They are now P1 units, and the installed table has them as **not exempt**:
   `addUnit(351, 527, 858, 27, 1, 3842, 0)` - the last field is `cavemanExempt = 0`.
3. 527 is the only unit in line 858, so `cavemanTarget` finds no lower tier and falls through to
   `CAVEMAN_MILITIA`.
4. `transformUnit` runs `xsRemoveUnit(unitId)` and then `xsCreateUnit(...)`. **The object is
   destroyed** and a new one with a new id takes its place.

Reference id 679 no longer exists, so `Capture Object 679` can never be satisfied and the two
`create_object` effects never run.

Note this is not an artefact of the condition being `Capture Object`. Vanilla used
`Own Objects, object_group 22, quantity 1` - a warship-class test - and a Militia is not class
22, so caveman breaks that form too.

## The logic consequence

`logic/joan/joan_3.py` gates the crossing on the wrong unit:

```python
self.restorable_boats = self.has_boats & logic.units.survives_caveman(Age2UnitData.TRANSPORT_SHIP)
```

With caveman on, `survives_caveman(TRANSPORT_SHIP)` asks for **item 334, Transport Ship Line**.
But holding 334 does not help: the transports are never created, so there is nothing for it to
protect. What has to survive caveman is the **Demolition Ship**, whose line item is **358**.

So logic believes 334 opens the crossing when 358 is what actually does. `restorable_boats`
feeds `meets_additional_base_requirements` and `can_cross_ocean`, and `can_cross_ocean` gates
all three of Joan 3's defeat rules.

## Options

1. **Exempt the two boats from caveman**, so 679 survives and the trigger fires as designed. The
   seam already exists - `MarkUnitCavemanImmune` is what `MercenarySpawn.xs` uses for muster
   units, and `ExemptUnitTypeFromCaveman` is called for `TRAP_FLEMISH_MILITIA` in `InitCaveman`.
   Logic would then need `restorable_boats` to stop asking for 334.
2. **Point the logic at the Demolition Ship**, leaving the game as is, so the gate reads
   `survives_caveman(DEMOLITION_SHIP)` and asks for 358. Honest about what the game does, but it
   keeps a state where the player holds the Transport Ship Line item and still gets no transport.

Option 1 matches what the scenario is trying to do; option 2 only describes what it currently
does.

## Comments

### Fixed (2026-11-03), pending in-game test

The two Transport Ship spawns moved out of `[D0] Finding Boats` and into **`AP Give Boats`**
(t49), which fires on `HasJoan3Boats()` plus `object_visible 679`.

This sidesteps caveman entirely. The old trigger needed P1 to **capture** object 679, and caveman
destroys that boat before the capture can register. The new one is driven by the **scenario item**
instead, so the two Transport Ships are created for P1 at (14,85) and (15,85) when the item
arrives.

`[D0] Finding Boats` keeps only its message. No Transport Ship is placed on the map, which
matches vanilla - they have always been created at run time.

### Closed (2026-11-06)

The game-side checks moved to [#78](78-in-game-checks-round-2.md). The AP side is done.
