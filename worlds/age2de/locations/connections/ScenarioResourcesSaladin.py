"""SALADIN Khan map yields, scanned ahead of the campaign itself.

NOT IMPORTED, and deliberately so. These five scenarios do not exist yet: there is no
Age2CampaignData.SALADIN, no Age2ScenarioData.AP_SALADIN_*, no Mongols civilisation, no locations,
no rules, no logic and no campaign bundle. Declaring the enums to make this data compile breaks
fourteen test methods that walk the campaign, scenario and civilisation enums directly - they ask
things like "every campaign has exactly one campaign item", which a placeholder cannot answer.

So the data waits here instead of rotting in a branch. When the campaign is really added, move
these statements back into ScenarioResources.py; they are in the same form as every other scenario
and need no translation beyond whatever tier restructuring has happened since.

Note AP_SALADIN_1 has no counts - the scan starts at chapter 2.
"""

from ..Scenarios import Age2ScenarioData
from .ScenarioResources import ScenarioResourceCount, ScenarioResourceDemand, Tier

Age2ScenarioData.AP_SALADIN_2.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_SALADIN_3.demand = ScenarioResourceDemand(gold=6000, stone=4000, food=20000)

Age2ScenarioData.AP_SALADIN_4.demand = ScenarioResourceDemand(gold=4500, stone=2000, food=15000)

Age2ScenarioData.AP_SALADIN_5.demand = ScenarioResourceDemand(gold=7500, stone=3000, food=25000)

Age2ScenarioData.AP_SALADIN_6.demand = ScenarioResourceDemand(gold=6000, stone=3000, food=20000)

Age2ScenarioData.AP_SALADIN_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=4000, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=250,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=1275, whale_count=0, relic_count=0
    ally_market=true, enemy_market=true,
    ally_dock=true, enemy_dock=true)

Age2ScenarioData.AP_SALADIN_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=11200, stone_count=5250,
    hunt_count=1400, herd_count=0, bush_count=0,
    shore_fish_count=5250, deep_fish_count=16975,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_SALADIN_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=2120, herd_count=3100, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=21600, stone_count=4550,
    hunt_count=0, herd_count=0, bush_count=1000,
    shore_fish_count=2825, deep_fish_count=6650,
    oyster_count=0, whale_count=0, relic_count=0)

"""The enemies don't use docks in the Scenario, leaving all open fish to the Player"""

Age2ScenarioData.AP_SALADIN_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=12000, stone_count=0,
    hunt_count=0, herd_count=1000, bush_count=0,
    shore_fish_count=600, deep_fish_count=4600,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=true,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_SALADIN_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=26400, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=1400, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_SALADIN_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=4000, stone_count=2450,
    hunt_count=0, herd_count=1500, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=true,
    ally_dock=false, enemy_dock=false)

Age2ScenarioData.AP_SALADIN_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=19200, stone_count=2450,
    hunt_count=3500, herd_count=1100, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_SALADIN_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=26400, stone_count=3850,
    hunt_count=0, herd_count=1100, bush_count=0,
    shore_fish_count=3200, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_SALADIN_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=4800, stone_count=1050,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=true, enemy_market=true,
    ally_dock=false, enemy_dock=true)

Age2ScenarioData.AP_SALADIN_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=10400, stone_count=7000,
    hunt_count=1040, herd_count=600, bush_count=0,
    shore_fish_count=3000, deep_fish_count=0,   # Please just use Scenario parsing to source the total and subtract it from what I've got for the enemies, it's too much to count manually
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_SALADIN_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=23200, stone_count=1750,
    hunt_count=340, herd_count=600, bush_count=375,
    shore_fish_count=2200, deep_fish_count=8925,
    oyster_count=0, whale_count=0, relic_count=1)

Age2ScenarioData.AP_SALADIN_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=8000, stone_count=3150,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=800, deep_fish_count=1325,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=false, enemy_market=true,
    ally_dock=true, enemy_dock=true)

Age2ScenarioData.AP_SALADIN_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=15200, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=400, deep_fish_count=0,   #Please just use Scenario parsing to source the total and subtract it from what I've got for the enemies and Player, then add 1400 for unreachable shore_fish, it's too much to count manually
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_SALADIN_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=36000, stone_count=3150,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=2200, deep_fish_count=1575,
    oyster_count=0, whale_count=0, relic_count=0)
