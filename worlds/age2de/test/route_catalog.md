# Economy route catalog

Every economy route the logic builds, and how many of the 18 scenarios can run each one.

    python -m worlds.age2de.tools.route_catalog

Regenerate with that and commit the diff. `test_route_catalog.py` pins it.

## Worth a look

Rendered at **default options**, so a route gated behind an option (Market Trade) or absent from every map (oysters, whales) reads as unreachable here and is not necessarily a fault. A fixed-force scenario runs no routes at all, by design.

- **Fishing Ships gathering food** is reachable in no scenario.
- **Fishing Ships gathering gold** is reachable in no scenario.
- **Fishing Ships gathering gold with Guarded Boats** is reachable in no scenario.
- **Market Trade** is reachable in no scenario.
- **Oyster Gatherers** is reachable in no scenario.
- **Oyster Gatherers with Guarded Boats** is reachable in no scenario.
- **a little of its own food** is reachable in no scenario.
- **a little of its own gold** is reachable in no scenario.
- **a little of its own stone** is reachable in no scenario.
- **a little of its own wood** is reachable in no scenario.
- **its own food** is reachable in no scenario.
- **its own stone** is reachable in no scenario.
- **its own wood** is reachable in no scenario.


## 42 routes - every scenario

| route | yields | needs | possible in |
| --- | --- | --- | --- |
| Lumberjacks | wood some | - | 15/18 |
| Gold Miners | gold some | - | 15/18 |
| Stone Miners | stone some | - | 15/18 |
| Hunters | food some | - | 12/18 |
| Shepherds | food some | - | 10/18 |
| Foragers | food some | - | 8/18 |
| Fishermen | food some | - | 13/18 |
| Fishermen with Guarded Boats | food some | wood some, gold some | 13/18 |
| Oyster Gatherers | gold some | - | 0/18 |
| Oyster Gatherers with Guarded Boats | gold some | wood some, gold some | 0/18 |
| Lumberjacks with a Base | wood at scale | - | 15/18 |
| Villagers gathering food with a Base | food at scale | - | 2/18 |
| Villagers gathering food with a Base with Guarded Boats | food at scale | wood some, gold some | 2/18 |
| Villagers gathering gold with a Base | gold at scale | - | 15/18 |
| Villagers gathering gold with a Base with Guarded Boats | gold at scale | wood some, gold some | 15/18 |
| Villagers gathering stone with a Base | stone at scale | - | 15/18 |
| Farmers | food at scale | wood at scale | 15/18 |
| Fishing Ships gathering food | food at scale | wood at scale | 0/18 |
| Fishing Ships gathering food with Guarded Boats | food at scale | wood at scale, gold some | 1/18 |
| Fishing Ships gathering gold | gold at scale | wood at scale | 0/18 |
| Fishing Ships gathering gold with Guarded Boats | gold at scale | wood at scale, gold some | 0/18 |
| Villagers and Fishing Ships gathering food | food at scale | wood at scale | 2/18 |
| Villagers and Fishing Ships gathering food with Guarded Boats | food at scale | wood at scale, gold some | 3/18 |
| Villagers and Fishing Ships gathering gold | gold at scale | wood at scale | 15/18 |
| Villagers and Fishing Ships gathering gold with Guarded Boats | gold at scale | wood at scale, gold some | 15/18 |
| Fish Traps | food at scale | wood at scale | 12/18 |
| Trade Cogs | wood at scale, gold at scale | wood some, gold some | 1/18 |
| Trade Cogs | wood at scale, gold at scale | gold some | 1/18 |
| Trade Cogs | wood at scale, gold at scale | wood some | 1/18 |
| Trade Cogs | wood at scale, gold at scale | - | 1/18 |
| Trade Carts | gold at scale | wood at scale, gold some | 3/18 |
| Trade Carts | gold at scale | wood at scale | 3/18 |
| Relics | gold some | - | 2/18 |
| Market Trade | wood at scale, food at scale, gold at scale, stone at scale | wood at scale | 0/18 |
| its own wood | wood at scale | - | 0/18 |
| its own food | food at scale | - | 0/18 |
| its own gold | gold at scale | - | 1/18 |
| its own stone | stone at scale | - | 0/18 |
| a little of its own wood | wood some | - | 0/18 |
| a little of its own food | food some | - | 0/18 |
| a little of its own gold | gold some | - | 0/18 |
| a little of its own stone | stone some | - | 0/18 |

## Per scenario

| scenario | routes | possible |
| --- | --- | --- |
| AP_ATTILA_1 | 42 | 21 |
| AP_ATTILA_2 | 42 | 14 |
| AP_ATTILA_3 | 42 | 22 |
| AP_ATTILA_4 | 42 | 14 |
| AP_ATTILA_5 | 42 | 18 |
| AP_ATTILA_6 | 42 | 20 |
| AP_GENGHIS_1 | 42 | 0 |
| AP_GENGHIS_2 | 42 | 12 |
| AP_GENGHIS_3 | 42 | 16 |
| AP_GENGHIS_4 | 42 | 16 |
| AP_GENGHIS_5 | 42 | 15 |
| AP_GENGHIS_6 | 42 | 12 |
| AP_JOAN_1 | 42 | 0 |
| AP_JOAN_2 | 42 | 16 |
| AP_JOAN_3 | 42 | 16 |
| AP_JOAN_4 | 42 | 15 |
| AP_JOAN_5 | 42 | 0 |
| AP_JOAN_6 | 42 | 14 |
