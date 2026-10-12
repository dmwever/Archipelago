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

Age2ScenarioData.AP_ELCID_2.demand = ScenarioResourceDemand(gold=3000, stone12000, food=15000)

Age2ScenarioData.AP_ELCID_3.demand = ScenarioResourceDemand(gold=3000, stone=1000, food=10000)

Age2ScenarioData.AP_ELCID_4.demand = ScenarioResourceDemand(gold=7500, stone=3000, food=25000)

Age2ScenarioData.AP_ELCID_5.demand = ScenarioResourceDemand(gold=3000, stone=1000, food=10000)

Age2ScenarioData.AP_ELCID_6.demand = ScenarioResourceDemand(gold=7500, stone=2000, food=25000)

Age2ScenarioData.AP_ELCID_1.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=0, enemy_market=0,
    ally_dock=0, enemy_dock=0)

Age2ScenarioData.AP_ELCID_1.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_1.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_1.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=6)

Age2ScenarioData.AP_ELCID_2.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=0, enemy_market=0,
    ally_dock=0, enemy_dock=0)

Age2ScenarioData.AP_ELCID_2.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_2.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_2.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_3.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=0, enemy_market=0,
    ally_dock=0, enemy_dock=0)

Age2ScenarioData.AP_ELCID_3.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_3.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_3.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_4.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=0, enemy_market=0,
    ally_dock=0, enemy_dock=0)

Age2ScenarioData.AP_ELCID_4.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,   # Please just use Scenario parsing to source the total and subtract it from what I've got for the enemies, it's too much to count manually, for both deep_ and shore_fish
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_4.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_4.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=0, enemy_market=0,
    ally_dock=0, enemy_dock=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_5.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_6.resources[Tier.BASE] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0
    ally_market=0, enemy_market=0,
    ally_dock=0, enemy_dock=0)

Age2ScenarioData.AP_ELCID_6.resources[Tier.OPEN] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_6.resources[Tier.ALLY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)

Age2ScenarioData.AP_ELCID_6.resources[Tier.ENEMY] = ScenarioResourceCount(
    gold_count=0, stone_count=0,
    hunt_count=0, herd_count=0, bush_count=0,
    shore_fish_count=0, deep_fish_count=0,
    oyster_count=0, whale_count=0, relic_count=0)
