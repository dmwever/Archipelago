"""BARBAROSSA map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. These five scenarios do not exist yet: there is no
Age2CampaignData.BARBAROSSA, no Age2ScenarioData.AP_BARBAROSSA_*, no Mongols civilisation, no locations,
no rules, no logic and no campaign bundle. Declaring the enums to make this data compile breaks
fourteen test methods that walk the campaign, scenario and civilisation enums directly - they ask
things like "every campaign has exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is really added, move
these statements back into ScenarioResources.py; they are in the same form as every other scenario
and need no translation beyond whatever tier restructuring has happened since.

Note AP_BARBAROSSA_5 has no counts - the scan starts at chapter 2.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import ScenarioResourceCount, ScenarioResourceDemand, Tier

Age2ScenarioData.AP_BARBAROSSA_1.demand = ScenarioResourceDemand(gold=9000, stone=3000, food=30000)

Age2ScenarioData.AP_BARBAROSSA_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_BARBAROSSA_3.demand = ScenarioResourceDemand(gold=6000, stone=3000, food=20000)

Age2ScenarioData.AP_BARBAROSSA_4.demand = ScenarioResourceDemand(gold=9000, stone=3000, food=30000)

Age2ScenarioData.AP_BARBAROSSA_6.demand = ScenarioResourceDemand(gold=6000, stone=2000, food=20000)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=9600, stone_count=3500,
    hunt_count=680, herd_count=1000, bush_count=1000,
    shore_fish_count=0, deep_fish_count=4300,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=true,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=24000, stone_count=7350,
    hunt_count=2040, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=1350,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=67200, stone_count=18200,
    hunt_count=9360, herd_count=4800, bush_count=4500,
    shore_fish_count=600, deep_fish_count=2200,
    oyster_count=0, whale_count=0, relic_count=6)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=1680, herd_count=0, bush_count=875,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=false,
    ally_dock=false, enemy_dock=true)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=2600, deep_fish_count=900,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=19200, stone_count=5950,
    hunt_count=1120, herd_count=0, bush_count=1500,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=6300, herd_count=0, bush_count=0,
    shore_fish_count=6200, deep_fish_count=1350,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=6400, stone_count=3150,
    hunt_count=2100, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=1400, whale_count=0, relic_count=0
    ally_market=true, enemy_market=true,
    ally_dock=true, enemy_dock=false)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=12800, stone_count=1400,
    hunt_count=1380, herd_count=900, bush_count=750,
    shore_fish_count=4000, deep_fish_count=1050,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=4800, stone_count=700,
    hunt_count=1400, herd_count=0, bush_count=0,
    shore_fish_count=1400, deep_fish_count=2675,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=28000, stone_count=7000,
    hunt_count=1940, herd_count=1200, bush_count=750,
    shore_fish_count=6200, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=9600, stone_count=3500,
    hunt_count=680, herd_count=400, bush_count=1250,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=false,
    ally_dock=false, enemy_dock=true)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=22400, stone_count=7350,
    hunt_count=3440, herd_count=800, bush_count=1500,
    shore_fish_count=0, deep_fish_count=0,   # Please just use Scenario parsing to source the total and subtract it from what I've got for the enemies, it's too much to count manually, for both deep_ and shore_fish
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=31200, stone_count=5950,
    hunt_count=0, herd_count=1200, bush_count=750,
    shore_fish_count=3400, deep_fish_count=4750,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8800, stone_count=1050,
    hunt_count=1020, herd_count=1500, bush_count=0,
    shore_fish_count=800, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=false,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=15200, stone_count=1400,
    hunt_count=1240, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=4000, stone_count=1400,
    hunt_count=1020, herd_count=1200, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_BARBAROSSA_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=22400, stone_count=6650,
    hunt_count=1960, herd_count=1000, bush_count=3750,
    shore_fish_count=1000, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)
