# Economy route catalog

Every economy route the logic builds, and how many of the 18 scenarios can run each one under some combination of these options:

- `market_trade`: 0, 1
- `partner_trade`: 0, 1, 2
- `existing_techs`: 0, 3

    python -m worlds.age2de.tools.route_catalog

Regenerate with that and commit the diff. `test_route_catalog.py` pins it.

## Worth a look

A route absent from every map (oysters, whales) or built by no civilisation in these campaigns (Folwark) reads as unreachable here and is not necessarily a fault. A fixed-force scenario runs no routes at all, by design.

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
- **Oyster Gatherers at a Dock** is reachable in no scenario.
- **Oyster Gatherers at a Town Center** is reachable in no scenario.
- **Oyster Gatherers at a built Dock** is reachable in no scenario.
- **Oyster Gatherers at a built Folwark** is reachable in no scenario.
- **Oyster Gatherers at a built Mill** is reachable in no scenario.
- **Oyster Gatherers at a standing Folwark** is reachable in no scenario.
- **Oyster Gatherers at a standing Mill** is reachable in no scenario.
- **Relics at a standing Monastery, advanced to Castle** is reachable in no scenario.
- **Relics at a standing Monastery, started in Castle** is reachable in no scenario.
- **Relics with a standing Monk at a standing Monastery, advanced to Castle** is reachable in no scenario.
- **Relics with a standing Monk at a standing Monastery, started in Castle** is reachable in no scenario.
- **Shepherds at a built Folwark** is reachable in no scenario.
- **Shepherds at a standing Folwark** is reachable in no scenario.
- **Stone Miners at a Mule Cart** is reachable in no scenario.
- **Villagers gathering food with a Base at a Dock** is reachable in no scenario.
- **Villagers gathering food with a Base at a Mule Cart** is reachable in no scenario.
- **Villagers gathering food with a Base at a built Dock** is reachable in no scenario.
- **Villagers gathering food with a Base at a built Folwark** is reachable in no scenario.
- **Villagers gathering food with a Base at a standing Folwark** is reachable in no scenario.
- **Villagers gathering gold with a Base at a Dock** is reachable in no scenario.
- **Villagers gathering gold with a Base at a Mule Cart** is reachable in no scenario.
- **Villagers gathering gold with a Base at a built Dock** is reachable in no scenario.
- **Villagers gathering gold with a Base at a built Folwark** is reachable in no scenario.
- **Villagers gathering gold with a Base at a built Mill** is reachable in no scenario.
- **Villagers gathering gold with a Base at a standing Folwark** is reachable in no scenario.
- **Villagers gathering gold with a Base at a standing Mill** is reachable in no scenario.
- **Villagers gathering stone with a Base at a Mule Cart** is reachable in no scenario.
- **a little of its own food** is reachable in no scenario.
- **a little of its own gold** is reachable in no scenario.
- **a little of its own stone** is reachable in no scenario.
- **a little of its own wood** is reachable in no scenario.
- **its own food** is reachable in no scenario.
- **its own stone** is reachable in no scenario.
- **its own wood** is reachable in no scenario.


## 122 routes - every scenario

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
| Fishermen at a built Dock | food some | wood some | 12/18 |
| Oyster Gatherers at a Town Center | gold some | - | 0/18 |
| Oyster Gatherers at a standing Mill | gold some | - | 0/18 |
| Oyster Gatherers at a built Mill | gold some | wood some | 0/18 |
| Oyster Gatherers at a standing Folwark | gold some | - | 0/18 |
| Oyster Gatherers at a built Folwark | gold some | wood some | 0/18 |
| Oyster Gatherers at a Dock | gold some | - | 0/18 |
| Oyster Gatherers at a built Dock | gold some | wood some | 0/18 |
| Lumberjacks with a Base | wood at scale | food some, housing at scale | 15/18 |
| Lumberjacks with a Base at a second Town Center, started in Castle | wood at scale | wood some, food some, stone some, housing at scale | 10/18 |
| Lumberjacks with a Base at a second Town Center, advanced to Castle | wood at scale | wood some, food at scale, gold some, stone some, housing at scale | 15/18 |
| Relics at a standing Monastery, started in Castle | gold some | housing some | 0/18 |
| Relics at a standing Monastery, advanced to Castle | gold some | wood some, food at scale, gold some, housing some | 0/18 |
| Relics at a built Monastery, started in Castle | gold some | wood some, housing some | 2/18 |
| Relics at a built Monastery, advanced to Castle | gold some | wood some, food at scale, gold some, housing some | 2/18 |
| Relics with a standing Monk at a standing Monastery, started in Castle | gold some | - | 0/18 |
| Relics with a standing Monk at a standing Monastery, advanced to Castle | gold some | wood some, food at scale, gold some | 0/18 |
| Relics with a standing Monk at a built Monastery, started in Castle | gold some | wood some | 1/18 |
| Relics with a standing Monk at a built Monastery, advanced to Castle | gold some | wood some, food at scale, gold some | 1/18 |
| Farmers | food at scale | wood at scale, food some, housing at scale | 15/18 |
| Fish Traps, started in Feudal | food at scale | wood at scale, housing at scale | 11/18 |
| Fish Traps, advanced to Feudal | food at scale | wood at scale, food some, housing at scale | 12/18 |
| Fish Traps, on Feudal Age Food | food at scale | wood at scale, housing at scale | 12/18 |
| Trade Cogs, started in Feudal | wood at scale, gold at scale | wood some, gold some, housing at scale | 7/18 |
| Trade Cogs, advanced to Feudal | wood at scale, gold at scale | wood some, food some, gold some, housing at scale | 8/18 |
| Trade Cogs, on Feudal Age Food | wood at scale, gold at scale | wood some, gold some, housing at scale | 8/18 |
| Trade Cogs on banked wood, started in Feudal | wood at scale, gold at scale | gold some, housing at scale | 7/18 |
| Trade Cogs on banked wood, advanced to Feudal | wood at scale, gold at scale | wood some, food some, gold some, housing at scale | 8/18 |
| Trade Cogs on banked wood, on Feudal Age Food | wood at scale, gold at scale | gold some, housing at scale | 8/18 |
| Trade Cogs on banked gold, started in Feudal | wood at scale, gold at scale | wood some, housing at scale | 7/18 |
| Trade Cogs on banked gold, advanced to Feudal | wood at scale, gold at scale | wood some, food some, housing at scale | 8/18 |
| Trade Cogs on banked gold, on Feudal Age Food | wood at scale, gold at scale | wood some, housing at scale | 8/18 |
| Trade Cogs on banked wood and gold, started in Feudal | wood at scale, gold at scale | housing at scale | 7/18 |
| Trade Cogs on banked wood and gold, advanced to Feudal | wood at scale, gold at scale | wood some, food some, housing at scale | 8/18 |
| Trade Cogs on banked wood and gold, on Feudal Age Food | wood at scale, gold at scale | housing at scale | 8/18 |
| Trade Carts, started in Feudal | gold at scale | wood at scale, gold some, housing at scale | 11/18 |
| Trade Carts, advanced to Feudal | gold at scale | wood at scale, food some, gold some, housing at scale | 13/18 |
| Trade Carts, on Feudal Age Food | gold at scale | wood at scale, gold some, housing at scale | 13/18 |
| Trade Carts on banked gold, started in Feudal | gold at scale | wood at scale, housing at scale | 11/18 |
| Trade Carts on banked gold, advanced to Feudal | gold at scale | wood at scale, food some, housing at scale | 13/18 |
| Trade Carts on banked gold, on Feudal Age Food | gold at scale | wood at scale, housing at scale | 13/18 |
| Market Trade, started in Feudal | wood at scale, food at scale, gold at scale, stone at scale | wood at scale | 12/18 |
| Market Trade, advanced to Feudal | wood at scale, food at scale, gold at scale, stone at scale | wood at scale, food some | 14/18 |
| Market Trade, on Feudal Age Food | wood at scale, food at scale, gold at scale, stone at scale | wood at scale | 14/18 |
| its own wood | wood at scale | - | 0/18 |
| its own food | food at scale | - | 0/18 |
| its own gold | gold at scale | - | 1/18 |
| its own stone | stone at scale | - | 0/18 |
| a little of its own wood | wood some | - | 0/18 |
| a little of its own food | food some | - | 0/18 |
| a little of its own gold | gold some | - | 0/18 |
| a little of its own stone | stone some | - | 0/18 |
| Houses | housing at scale | wood some | 9/18 |
| Builds no Houses | housing at scale | - | 6/18 |
| its own housing | housing at scale | - | 1/18 |
| a little of its own housing | housing some | - | 6/18 |
| Villagers gathering food with a Base at a second Town Center, started in Castle | food at scale | wood some, food some, stone some, housing at scale | 1/18 |
| Villagers gathering food with a Base at a second Town Center, advanced to Castle | food at scale | wood some, food at scale, gold some, stone some, housing at scale | 2/18 |
| Villagers gathering food with a Base at a standing Mill | food at scale | food some, housing at scale | 2/18 |
| Villagers gathering food with a Base at a built Mill | food at scale | wood some, food some, housing at scale | 2/18 |
| Villagers gathering food with a Base at a standing Folwark | food at scale | food some, housing at scale | 0/18 |
| Villagers gathering food with a Base at a built Folwark | food at scale | wood some, food some, housing at scale | 0/18 |
| Villagers gathering food with a Base at a Mule Cart | food at scale | food some, housing at scale | 0/18 |
| Villagers gathering food with a Base at a Dock | food at scale | food some, housing at scale | 0/18 |
| Villagers gathering food with a Base at a built Dock | food at scale | wood some, food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a second Town Center, started in Castle | gold at scale | wood some, food some, stone some, housing at scale | 10/18 |
| Villagers gathering gold with a Base at a second Town Center, advanced to Castle | gold at scale | wood some, food at scale, gold some, stone some, housing at scale | 15/18 |
| Villagers gathering gold with a Base at a standing Mining Camp | gold at scale | food some, housing at scale | 2/18 |
| Villagers gathering gold with a Base at a built Mining Camp | gold at scale | wood some, food some, housing at scale | 15/18 |
| Villagers gathering gold with a Base at a Mule Cart | gold at scale | food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a standing Mill | gold at scale | food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a built Mill | gold at scale | wood some, food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a standing Folwark | gold at scale | food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a built Folwark | gold at scale | wood some, food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a Dock | gold at scale | food some, housing at scale | 0/18 |
| Villagers gathering gold with a Base at a built Dock | gold at scale | wood some, food some, housing at scale | 0/18 |
| Villagers gathering stone with a Base at a second Town Center, started in Castle | stone at scale | wood some, food some, stone some, housing at scale | 10/18 |
| Villagers gathering stone with a Base at a second Town Center, advanced to Castle | stone at scale | wood some, food at scale, gold some, stone some, housing at scale | 15/18 |
| Villagers gathering stone with a Base at a standing Mining Camp | stone at scale | food some, housing at scale | 2/18 |
| Villagers gathering stone with a Base at a built Mining Camp | stone at scale | wood some, food some, housing at scale | 15/18 |
| Villagers gathering stone with a Base at a Mule Cart | stone at scale | food some, housing at scale | 0/18 |
| Fishing Ships gathering food | food at scale | wood at scale, housing at scale | 1/18 |
| Fishing Ships gathering gold | gold at scale | wood at scale, housing at scale | 0/18 |
| Villagers and Fishing Ships gathering food | food at scale | wood at scale, food some, housing at scale | 3/18 |
| Villagers and Fishing Ships gathering food at a second Town Center, started in Castle | food at scale | wood at scale, food some, stone some, housing at scale | 1/18 |
| Villagers and Fishing Ships gathering food at a second Town Center, advanced to Castle | food at scale | wood at scale, food at scale, gold some, stone some, housing at scale | 3/18 |
| Villagers and Fishing Ships gathering gold | gold at scale | wood at scale, food some, housing at scale | 15/18 |
| Villagers and Fishing Ships gathering gold at a second Town Center, started in Castle | gold at scale | wood at scale, food some, stone some, housing at scale | 10/18 |
| Villagers and Fishing Ships gathering gold at a second Town Center, advanced to Castle | gold at scale | wood at scale, food at scale, gold some, stone some, housing at scale | 15/18 |

## Per scenario

| scenario | routes | possible |
| --- | --- | --- |
| AP_ATTILA_1 | 122 | 48 |
| AP_ATTILA_2 | 122 | 50 |
| AP_ATTILA_3 | 122 | 57 |
| AP_ATTILA_4 | 122 | 35 |
| AP_ATTILA_5 | 122 | 42 |
| AP_ATTILA_6 | 122 | 54 |
| AP_GENGHIS_1 | 122 | 0 |
| AP_GENGHIS_2 | 122 | 27 |
| AP_GENGHIS_3 | 122 | 50 |
| AP_GENGHIS_4 | 122 | 51 |
| AP_GENGHIS_5 | 122 | 43 |
| AP_GENGHIS_6 | 122 | 28 |
| AP_JOAN_1 | 122 | 0 |
| AP_JOAN_2 | 122 | 37 |
| AP_JOAN_3 | 122 | 50 |
| AP_JOAN_4 | 122 | 60 |
| AP_JOAN_5 | 122 | 0 |
| AP_JOAN_6 | 122 | 51 |
