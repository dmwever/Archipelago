# 71: Attila 5's starting resources were moved into an item that logic never requires

**Reported:** 2026-11-02, playtesting

**Status:** done (in-game checks in #78)

## Report

The Catalaunian Fields does not require Attila 5 Deathmatch Resources in order to win the game.

## The conversion zeroed the player's purse

Attila 5 is a deathmatch-shaped scenario: no Town Center, three villagers, ten Tarkans, and a
large opening pile of resources. The AP conversion took the pile away and put it in an item.

| | food | wood | stone | gold |
| --- | --- | --- | --- | --- |
| **vanilla `C1_Attila_5`**, the human | **8000** | **2000** | **1000** | **8000** |
| **Ageipelago `AP_Attila_5`**, P0 Attila | **0** | **0** | **0** | **0** |
| item 1027 `Attila5Deathmatch()` grants | 7000 | 1000 | 500 | 7250 |

Meanwhile the opposition is untouched and enormous:

| player | food | wood | stone | gold |
| --- | --- | --- | --- | --- |
| Ostrogoths | 4000 | 10000 | 5000 | 5000 |
| Western Roman Empire | 20000 | 20000 | 5000 | 20000 |
| Visigoths | 10000 | 10000 | 5000 | 10000 |
| Alans | 10000 | 10000 | 5000 | 10000 |

So without `AP_ATTILA_5_DEATHMATCH` the player opens with nothing at all, against four players
holding tens of thousands, and has to bootstrap from three villagers with no Town Center.

## Logic does not know the item exists

`AP_ATTILA_5_DEATHMATCH` (1027) appears in `items/Items.py` and nowhere else that matters:

- `logic/attila/attila_5.py` `Attila5StartingState` never references it. It sets only
  `is_unlocked` and `defeat_rules`, so `has_vils` falls through to the default `True_()` and no
  resource consequence is modelled.
- `rules/attila_rules/attila_5.py` gates victory on the three defeats alone:

```python
can_win_scenario: Rule = (
    defeats(ATT5_WESTERN_ROMAN_EMPIRE) &
    defeats(ATT5_ALANS) &
    defeats(ATT5_VISIGOTHS)
)
```

The scenario's declared demand is `gold=7500, stone=2000, food=20000`, and the item covers most
of the gold and a third of the food outright.

## The dead flag

`Attila5Deathmatch()` sets `attila5Deathmatch = true` and `HasAttila5Deathmatch()` reads it, but
**nothing calls `HasAttila5Deathmatch()`** - not in any `.xs` file, not as a trigger condition in
`AP_Attila_5.aoe2scenario`. The resource grant itself works; the flag beside it is unused. Either
a trigger was meant to gate on it, or the accessor is left over.

## What has to be decided

Whether the map's own economy is enough to win without the item. The scan says Attila 5 has real
resources - BASE alone holds gold 12000, stone 2800, hunt 680, herd 1400, bush 750 - and the
player does have three villagers, so a very slow bootstrap is not obviously impossible. But with
zero wood there is no Town Center until the Town Center seed items arrive, and the three defeat
rules all demand Imperial-age counters and long-range siege.

- **If the item is required**, `Attila5StartingState` needs to carry it and victory should rest on
  it, in whatever shape matches the house style - most likely feeding the economy rather than
  being `&`-ed onto `can_win_scenario` directly.
- **If the map economy suffices**, the item is a bonus and logic is already right, but then the
  scenario is winnable from a standing start of literally nothing, which is worth confirming in
  play before it is relied on.

Severity: if the first reading is correct this is reachable-in-logic-but-not-in-game, which can
strand a seed.

## Comments

### Fixed (2026-11-03), pending in-game test

Three changes.

`rules/attila_rules/attila_5.py` - every Attila 5 defeat location and the victory now ask for the
item:

```python
has_deathmatch_resources = Has(Age2ItemData.AP_ATTILA_5_DEATHMATCH.item_name)
```

`items/Items.py` - `AP_ATTILA_5_DEATHMATCH` moved out of the Genghis Khan block into the Attila
block, where it belongs.

`ProgressionItems.xs` - `Attila5Deathmatch()` now only pays out inside Attila 5:

```xs
if (scenarioId == 105) {
    ...
}
```

Without that guard the resources landed in whatever scenario P1 happened to be in when the item
arrived.

The `scenarioId` guard is safe across scenarios: items are paid out again on scenario startup,
and on a load once the item cursor catches up. An item received while P1 is elsewhere still pays
when P1 reaches Attila 5.

### Closed (2026-11-06)

The game-side checks moved to [#78](78-in-game-checks-round-2.md). The AP side is done.
