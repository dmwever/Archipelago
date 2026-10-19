"""ELCID map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. These five scenarios do not exist yet: there is no
Age2CampaignData.ELCID, no Age2ScenarioData.AP_ELCID_*, no Mongols civilisation, no locations,
no rules, no logic and no campaign bundle. Declaring the enums to make this data compile breaks
fourteen test methods that walk the campaign, scenario and civilisation enums directly - they ask
things like "every campaign has exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is really added, move
these statements back into ScenarioResources.py; they are in the same form as every other scenario
and need no translation beyond whatever tier restructuring has happened since.

Note AP_ELCID_5 has no counts - the scan starts at chapter 2.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import ScenarioResourceCount, ScenarioResourceDemand, Tier

Age2ScenarioData.AP_ELCID_1.demand = ScenarioResourceDemand(gold=3000, stone=1000, food=10000)

Age2ScenarioData.AP_ELCID_2.demand = ScenarioResourceDemand(gold=3000, stone=1000, food=15000)

Age2ScenarioData.AP_ELCID_3.demand = ScenarioResourceDemand(gold=3000, stone=1000, food=10000)

Age2ScenarioData.AP_ELCID_4.demand = ScenarioResourceDemand(gold=7500, stone=3000, food=25000)

Age2ScenarioData.AP_ELCID_5.demand = ScenarioResourceDemand(gold=3000, stone=1000, food=10000)

Age2ScenarioData.AP_ELCID_6.demand = ScenarioResourceDemand(gold=7500, stone=2000, food=25000)

Age2ScenarioData.AP_ELCID_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=7200, stone_count=0,
    hunt_count=420, herd_count=0, bush_count=500,
    shore_fish_count=1625, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=false,
    ally_dock=true, enemy_dock=false)

Age2ScenarioData.AP_ELCID_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=9600, stone_count=0,
    hunt_count=560, herd_count=0, bush_count=0,
    shore_fish_count=3725, deep_fish_count=450,
    oyster_count=0, whale_count=0, relic_count=4)

Age2ScenarioData.AP_ELCID_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=12800, stone_count=1400,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=7200, stone_count=2800,
    hunt_count=340, herd_count=0, bush_count=0,
    shore_fish_count=6000, deep_fish_count=625,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_ELCID_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=6400, stone_count=0,
    hunt_count=0, herd_count=1200, bush_count=0,
    shore_fish_count=800, deep_fish_count=2400,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=false,
    ally_dock=true, enemy_dock=false)

Age2ScenarioData.AP_ELCID_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=8000, stone_count=3850,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=7200, deep_fish_count=1000,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=17600, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=2600, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=4)

Age2ScenarioData.AP_ELCID_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=5600, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=2025, deep_fish_count=675,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=false,
    ally_dock=true, enemy_dock=false)

Age2ScenarioData.AP_ELCID_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=10400, stone_count=2100,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=1600, deep_fish_count=2025,
    oyster_count=0, whale_count=0, relic_count=4)

Age2ScenarioData.AP_ELCID_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=8000, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=1750,
    hunt_count=1360, herd_count=600, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_ELCID_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=2400, stone_count=700,
    hunt_count=0, herd_count=0, bush_count=500,
    shore_fish_count=1625, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_ELCID_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=17600, stone_count=8400,
    hunt_count=1240, herd_count=0, bush_count=2625,
    shore_fish_count=800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=12000, stone_count=1400,
    hunt_count=700, herd_count=0, bush_count=0,
    shore_fish_count=3400, deep_fish_count=8125,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=3200, stone_count=2100,
    hunt_count=0, herd_count=1900, bush_count=0,
    shore_fish_count=0, deep_fish_count=5925,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=false,
    ally_dock=true, enemy_dock=false)

Age2ScenarioData.AP_ELCID_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=4800, stone_count=2100,
    hunt_count=420, herd_count=0, bush_count=0,
    shore_fish_count=5025, deep_fish_count=1050,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=4000, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=225,     #This fish is unreachable.
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=5600, stone_count=3500,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_ELCID_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=14400, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=800, deep_fish_count=8950,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_ELCID_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=44000, stone_count=2450,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=5250, deep_fish_count=5400,
    oyster_count=0, whale_count=0, relic_count=0)
