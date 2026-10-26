# Economy route catalog

Every economy route the logic builds, and how many of the 18 scenarios can run each one.

    python -m worlds.age2de.tools.route_catalog

Regenerate with that and commit the diff. `test_route_catalog.py` pins it.

## Worth a look

Rendered at **default options**, so a route gated behind an option (Market Trade) or absent from every map (oysters, whales) reads as unreachable here and is not necessarily a fault. A fixed-force scenario runs no routes at all, by design.

- **Fishermen at a built Folwark** is reachable in no scenario.
- **Fishermen at a standing Folwark** is reachable in no scenario.
- **Fishing Ships gathering gold** is reachable in no scenario.
- **Foragers at a built Folwark** is reachable in no scenario.
- **Foragers at a standing Folwark** is reachable in no scenario.
- **Gold Miners at a Mule Cart** is reachable in no scenario.
- **Hunters at a Mule Cart** is reachable in no scenario.
- **Hunters at a built Folwark** is reachable in no scenario.
- **Hunters at a standing Folwark** is reachable in no scenario.
- **Lumberjacks at a Mule Cart** is reachable in no scenario.
- **Market Trade** is reachable in no scenario.
- **Oyster Gatherers at a Dock** is reachable in no scenario.
- **Oyster Gatherers at a Town Center** is reachable in no scenario.
- **Oyster Gatherers at a built Folwark** is reachable in no scenario.
- **Oyster Gatherers at a built Mill** is reachable in no scenario.
- **Oyster Gatherers at a standing Folwark** is reachable in no scenario.
- **Oyster Gatherers at a standing Mill** is reachable in no scenario.
- **Relics at a standing Monastery** is reachable in no scenario.
- **Shepherds at a built Folwark** is reachable in no scenario.
- **Shepherds at a standing Folwark** is reachable in no scenario.
- **Stone Miners at a Mule Cart** is reachable in no scenario.
- **a little of its own food** is reachable in no scenario.
- **a little of its own gold** is reachable in no scenario.
- **a little of its own stone** is reachable in no scenario.
- **a little of its own wood** is reachable in no scenario.
- **its own food** is reachable in no scenario.
- **its own stone** is reachable in no scenario.
- **its own wood** is reachable in no scenario.


## 66 routes - every scenario

| route | yields | needs | possible in |
| --- | --- | --- | --- |
| Lumberjacks at a Town Center | wood some | - | 15/18 |
| Lumberjacks at a Lumber Camp | wood some | - | 15/18 |
| Lumberjacks at a Mule Cart | wood some | - | 0/18 |
| Gold Miners at a Town Center | gold some | - | 15/18 |
| Gold Miners at a standing Mining Camp | gold some | - | 2/18 |
| Gold Miners at a built Mining Camp | gold some | wood some | 15/18 |
| Gold Miners at a Mule Cart | gold some | - | 0/18 |
| Stone Miners at a Town Center | stone some | - | 15/18 |
| Stone Miners at a standing Mining Camp | stone some | - | 2/18 |
| Stone Miners at a built Mining Camp | stone some | wood some | 15/18 |
| Stone Miners at a Mule Cart | stone some | - | 0/18 |
| Hunters at a Town Center | food some | - | 12/18 |
| Hunters at a standing Mill | food some | - | 4/18 |
| Hunters at a built Mill | food some | wood some | 12/18 |
| Hunters at a standing Folwark | food some | - | 0/18 |
| Hunters at a built Folwark | food some | wood some | 0/18 |
| Hunters at a Mule Cart | food some | - | 0/18 |
| Shepherds at a Town Center | food some | - | 10/18 |
| Shepherds at a standing Mill | food some | - | 3/18 |
| Shepherds at a built Mill | food some | wood some | 10/18 |
| Shepherds at a standing Folwark | food some | - | 0/18 |
| Shepherds at a built Folwark | food some | wood some | 0/18 |
| Foragers at a Town Center | food some | - | 8/18 |
| Foragers at a standing Mill | food some | - | 3/18 |
| Foragers at a built Mill | food some | wood some | 8/18 |
| Foragers at a standing Folwark | food some | - | 0/18 |
| Foragers at a built Folwark | food some | wood some | 0/18 |
| Fishermen at a Town Center | food some | - | 13/18 |
| Fishermen at a standing Mill | food some | - | 5/18 |
| Fishermen at a built Mill | food some | wood some | 13/18 |
| Fishermen at a standing Folwark | food some | - | 0/18 |
| Fishermen at a built Folwark | food some | wood some | 0/18 |
| Fishermen at a Dock | food some | - | 12/18 |
| Oyster Gatherers at a Town Center | gold some | - | 0/18 |
| Oyster Gatherers at a standing Mill | gold some | - | 0/18 |
| Oyster Gatherers at a built Mill | gold some | wood some | 0/18 |
| Oyster Gatherers at a standing Folwark | gold some | - | 0/18 |
| Oyster Gatherers at a built Folwark | gold some | wood some | 0/18 |
| Oyster Gatherers at a Dock | gold some | - | 0/18 |
| Relics at a standing Monastery | gold some | - | 0/18 |
| Relics at a built Monastery | gold some | wood some | 2/18 |
| Farmers | food at scale | wood at scale | 15/18 |
| Fish Traps | food at scale | wood at scale | 12/18 |
| Trade Cogs | wood at scale, gold at scale | wood some, gold some | 1/18 |
| Trade Cogs on banked wood | wood at scale, gold at scale | gold some | 1/18 |
| Trade Cogs on banked gold | wood at scale, gold at scale | wood some | 1/18 |
| Trade Cogs on banked wood and gold | wood at scale, gold at scale | - | 1/18 |
| Trade Carts | gold at scale | wood at scale, gold some | 3/18 |
| Trade Carts on banked gold | gold at scale | wood at scale | 3/18 |
| Market Trade | wood at scale, food at scale, gold at scale, stone at scale | wood at scale | 0/18 |
| its own wood | wood at scale | - | 0/18 |
| its own food | food at scale | - | 0/18 |
| its own gold | gold at scale | - | 1/18 |
| its own stone | stone at scale | - | 0/18 |
| a little of its own wood | wood some | - | 0/18 |
| a little of its own food | food some | - | 0/18 |
| a little of its own gold | gold some | - | 0/18 |
| a little of its own stone | stone some | - | 0/18 |
| Lumberjacks with a Base | wood at scale | - | 15/18 |
| Villagers gathering food with a Base | food at scale | - | 2/18 |
| Villagers gathering gold with a Base | gold at scale | - | 15/18 |
| Villagers gathering stone with a Base | stone at scale | - | 15/18 |
| Fishing Ships gathering food | food at scale | wood at scale | 1/18 |
| Fishing Ships gathering gold | gold at scale | wood at scale | 0/18 |
| Villagers and Fishing Ships gathering food | food at scale | wood at scale | 3/18 |
| Villagers and Fishing Ships gathering gold | gold at scale | wood at scale | 15/18 |

## Per scenario

| scenario | routes | possible |
| --- | --- | --- |
| AP_ATTILA_1 | 66 | 26 |
| AP_ATTILA_2 | 66 | 17 |
| AP_ATTILA_3 | 66 | 27 |
| AP_ATTILA_4 | 66 | 17 |
| AP_ATTILA_5 | 66 | 23 |
| AP_ATTILA_6 | 66 | 25 |
| AP_GENGHIS_1 | 66 | 0 |
| AP_GENGHIS_2 | 66 | 15 |
| AP_GENGHIS_3 | 66 | 21 |
| AP_GENGHIS_4 | 66 | 27 |
| AP_GENGHIS_5 | 66 | 18 |
| AP_GENGHIS_6 | 66 | 15 |
| AP_JOAN_1 | 66 | 0 |
| AP_JOAN_2 | 66 | 21 |
| AP_JOAN_3 | 66 | 20 |
| AP_JOAN_4 | 66 | 24 |
| AP_JOAN_5 | 66 | 0 |
| AP_JOAN_6 | 66 | 17 |
