"""Genghis Khan map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. These five scenarios do not exist yet: there is no
Age2CampaignData.GENGHIS, no Age2ScenarioData.AP_GENGHIS_*, no Mongols civilisation, no locations,
no rules, no logic and no campaign bundle. Declaring the enums to make this data compile breaks
fourteen test methods that walk the campaign, scenario and civilisation enums directly - they ask
things like "every campaign has exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is really added, move
these statements back into ScenarioResources.py; they are in the same form as every other scenario
and need no translation beyond whatever tier restructuring has happened since.

Note AP_GENGHIS_1 has no counts - the scan starts at chapter 2.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import (ScenarioAllyResourceCount, ScenarioBaseResourceCount,
                                ScenarioEnemyResourceCount, ScenarioOpenResourceCount,
                                ScenarioResourceDemand)

Age2ScenarioData.AP_GENGHIS_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_GENGHIS_3.demand = ScenarioResourceDemand(gold=12000, stone=4000, food=40000)

Age2ScenarioData.AP_GENGHIS_4.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_GENGHIS_5.demand = ScenarioResourceDemand(gold=4500, stone=4000, food=15000)

Age2ScenarioData.AP_GENGHIS_6.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_GENGHIS_2.resources = ScenarioBaseResourceCount(
    gold_count=8000, stone_count=1050,
    hunt_count=1400, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_2.resources = ScenarioOpenResourceCount(
    gold_count=7200, stone_count=1050,
    hunt_count=5040, herd_count=300, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_2.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_2.resources = ScenarioEnemyResourceCount(
    gold_count=12000, stone_count=2450,
    hunt_count=1120, herd_count=0, bush_count=2500,
    shore_fish_count=600, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources = ScenarioBaseResourceCount(
    gold_count=3200, stone_count=3500,
    hunt_count=680, herd_count=300, bush_count=1500,
    shore_fish_count=800, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources = ScenarioOpenResourceCount(
    gold_count=12000, stone_count=10050,
    hunt_count=1660, herd_count=200, bush_count=0,
    shore_fish_count=2275, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_3.resources = ScenarioEnemyResourceCount(
    gold_count=40800, stone_count=15750,
    hunt_count=2980, herd_count=600, bush_count=5125,
    shore_fish_count=3000, fish_count=12525,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources = ScenarioBaseResourceCount(
    gold_count=8000, stone_count=0,
    hunt_count=1660, herd_count=1000, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources = ScenarioOpenResourceCount(
    gold_count=4000, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=625,
    shore_fish_count=3600, fish_count=2475,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_4.resources = ScenarioEnemyResourceCount(
    gold_count=28000, stone_count=4900,
    hunt_count=980, herd_count=0, bush_count=1500,
    shore_fish_count=800, fish_count=400,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_5.resources = ScenarioBaseResourceCount(
    gold_count=3200, stone_count=3850,
    hunt_count=840, herd_count=0, bush_count=0,
    shore_fish_count=800, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_5.resources = ScenarioOpenResourceCount(
    gold_count=4000, stone_count=2450,
    hunt_count=1120, herd_count=0, bush_count=0,
    shore_fish_count=1000, fish_count=425,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_GENGHIS_5.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_5.resources = ScenarioEnemyResourceCount(
    gold_count=17600, stone_count=5600,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=1000, fish_count=425,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources = ScenarioBaseResourceCount(
    gold_count=8000, stone_count=3500,
    hunt_count=980, herd_count=800, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources = ScenarioOpenResourceCount(
    gold_count=8000, stone_count=3500,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources = ScenarioAllyResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_GENGHIS_6.resources = ScenarioEnemyResourceCount(
    gold_count=16000, stone_count=5950,
    hunt_count=1660, herd_count=900, bush_count=875,
    shore_fish_count=225, fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)
