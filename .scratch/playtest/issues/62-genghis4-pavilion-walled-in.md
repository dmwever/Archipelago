# 62: Genghis pavilions: 4 is walled in by forest, 6 is out at the map edge

**Reported:** 2026-10-31, playtesting

**Status:** needs-triage

## Report

Move the Genghis Khan pavilions. Genghis 4's is stuck in the cliffed-out area in the centre of
the level; it should be by one of the two bases, possibly one in each.

## All six measured

Pavilion tile from each `AP_Genghis_<n>.xs`, against where P1 actually is and what surrounds the
tile within 8 tiles:

| scenario | pavilion | distance to P1 | within 8 tiles | verdict |
| --- | --- | --- | --- | --- |
| Genghis 1 | (38,149) | sits 2 tiles under the granted start box `(35,141)-(41,147)` | 25 objects, 12 trees, P1's own Cavalry Archers and Light Cavalry among them | fine |
| Genghis 2 | (142,123) | 11 | 17 objects, 4 trees | fine |
| Genghis 3 | (177,22) | 6 | 21 objects, 3 trees, 5 cliffs - P1 units are there too | fine |
| **Genghis 4** | **(189,139)** | its 34 objects are split across two distant bases | **116 objects, every one a tree** | **walled in** |
| Genghis 5 | (130,62) | 5, TC at (132,65) | 26 objects, 0 trees | fine |
| **Genghis 6** | **(104,3)** | **42 to the centroid, 17 north of the TC at (104,20)** | 60 objects, 31 trees; the tile is on the map's top edge | **too far out** |

Four of the six are already where they should be. Two are not.

## Genghis 4

Nothing but forest around it - 116 trees and no other object within 8 tiles - on flat ground
with no cliffs, so it is a wooded pocket rather than literal cliffs, walled in the same way. It
is about 64 tiles from the south base and 79 from the north.

P1's two bases: Town Centers at **(180,203)** and **(208,60)**, with 16 objects clustered at
each.

Clear 3x3 ground three tiles from each Town Center, unoccupied and on terrain the scenario
already walks:

| near | tile | terrain |
| --- | --- | --- |
| south base (180,203) | **(177,201)** | 11 |
| | (177,200), (177,205), (177,206) | 6, 11, 6 |
| north base (208,60) | **(205,59)** | 11 |
| | (205,57), (205,58), (205,60) | 11, 42, 0 |

## Genghis 6

The pavilion is at (104,3), on the top edge of the map, 17 tiles north of P1's Town Center at
(104,20) and 42 from the centroid of P1's 110 objects. Clear 3x3 sites three tiles from the TC:

| tile | terrain |
| --- | --- |
| **(101,19)** | 6 |
| (101,17), (101,18), (101,20) | 6 |

## Facing still has to be chosen

Spawn and muster derive from the tile and the facing, two and six tiles out along it, so the
facing has to point at open ground rather than back into the base or into the trees. Current
facings: Genghis 4 `PAVILION_FACE_NE`, Genghis 6 `PAVILION_FACE_SE`.

## One pavilion or two

The runtime supports **one**. `APavilion.xs` holds a single `pavilionX`, `pavilionY`,
`pavilionFacing` and a single `pavilionId`, and `SetPavilionPlacement` overwrites rather than
appends. `PavilionSpawnPoint` and `PavilionMusterPoint` both derive from that one tile, and
`MercenarySpawn.xs` calls `PavilionSpawnPoint()` with no notion of which pavilion.

So "one in each base" for Genghis 4 is not a coordinate change - it means making the pavilion a
list and deciding which one a mustering mercenary uses. Worth costing separately.

Moving each pavilion to one base is a one-line change per scenario in `AP_Genghis_<n>.xs`.

## Comments
