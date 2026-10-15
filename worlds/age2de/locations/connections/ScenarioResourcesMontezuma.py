"""Montezuma map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. The Montezuma campaign is not connected: there is no
Age2CampaignData.MONTEZUMA, no Age2ScenarioData.AP_MONTEZUMA_*, no locations, no rules, no logic and
no campaign bundle. Declaring the enums to make this data compile breaks the tests that walk the
campaign, scenario and civilisation enums directly - they ask things like "every campaign has
exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is connected, move the
demand and resource statements into ScenarioResources.py; they are in the same form as every other
scenario and need no translation beyond whatever tier restructuring has happened since.

MARKET_AND_DOCK_FLAGS keeps PR 19's market and dock flags, one set per scenario. They record judged
usability, not building existence: never "correct" one from a scenario scan. Connected scenarios do
not store these flags; they derive them from per-player records. So when the campaign is connected,
these flags must be rescanned per player - which player owns or builds each market and dock, on
which side, and whether it is usable - and written as player records. Do not move this table into
the connected data.

Only the skeleton is here: every count is 0 except AP_MONTEZUMA_1's enemy relics, and PR 19 left
every market and dock flag at 0, unjudged. They are written False below only so the file parses;
treat them as unknown.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import ScenarioResourceCount, ScenarioResourceDemand, Tier

Age2ScenarioData.AP_MONTEZUMA_1.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_MONTEZUMA_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_MONTEZUMA_3.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_MONTEZUMA_4.demand = ScenarioResourceDemand(gold=4500, stone=1000, food=15000)

Age2ScenarioData.AP_MONTEZUMA_5.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_MONTEZUMA_6.demand = ScenarioResourceDemand(gold=9000, stone=3000, food=30000)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=6)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    # Please just use Scenario parsing to source the total and subtract it from what I've got for
    # the enemies, it's too much to count manually, for both deep_ and shore_fish
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_MONTEZUMA_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

MARKET_AND_DOCK_FLAGS = {
    Age2ScenarioData.AP_MONTEZUMA_1: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_MONTEZUMA_2: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_MONTEZUMA_3: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_MONTEZUMA_4: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_MONTEZUMA_5: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
    Age2ScenarioData.AP_MONTEZUMA_6: {
        "ally_market": False,
        "enemy_market": False,
        "ally_dock": False,
        "enemy_dock": False,
    },
}
