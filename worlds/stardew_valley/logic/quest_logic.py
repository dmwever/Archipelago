from typing import Dict
from dataclasses import field

from .action_logic import ActionLogic
from .building_logic import BuildingLogic
from .combat_logic import CombatLogic
from .cooking_logic import CookingLogic
from .fishing_logic import FishingLogic
from .has_logic import HasLogic
from .mine_logic import MineLogic
from .money_logic import MoneyLogic
from .received_logic import ReceivedLogic
from .region_logic import RegionLogic
from .relationship_logic import RelationshipLogic
from .season_logic import SeasonLogic
from .skill_logic import SkillLogic
from .tool_logic import ToolLogic
from ..options import SkillProgression, Mods
from ..strings.artisan_good_names import ArtisanGood
from ..strings.building_names import Building
from ..strings.craftable_names import Craftable
from ..strings.crop_names import Fruit, Vegetable
from ..strings.fish_names import Fish
from ..strings.food_names import Meal
from ..strings.forageable_names import Forageable
from ..strings.machine_names import Machine
from ..strings.monster_drop_names import Loot
from ..strings.material_names import Material
from ..strings.metal_names import MetalBar, Ore, Mineral
from ..strings.region_names import Region
from ..strings.season_names import Season
from ..strings.tool_names import Tool
from ..strings.quest_names import Quest
from ..strings.villager_names import NPC
from ..strings.wallet_item_names import Wallet
from ..stardew_rule import StardewRule, Has


class QuestLogic:
    player: int
    received: ReceivedLogic
    has: HasLogic
    mine: MineLogic
    region: RegionLogic
    relationship: RelationshipLogic
    tool: ToolLogic
    fishing: FishingLogic
    cooking: CookingLogic
    mods_option: Mods
    money: MoneyLogic
    combat: CombatLogic
    season: SeasonLogic
    skill: SkillLogic
    quest_rules: Dict[str, StardewRule]

    def __init__(self, player: int, skill_option: SkillProgression, received: ReceivedLogic, has: HasLogic, mine: MineLogic, region: RegionLogic, action: ActionLogic,
                 relationship: RelationshipLogic, building: BuildingLogic, tool: ToolLogic, fishing: FishingLogic, cooking: CookingLogic,
                 money: MoneyLogic, combat: CombatLogic, season: SeasonLogic, mods_option: Mods):
        self.player = player
        self.skill_option = skill_option
        self.received = received
        self.has = has
        self.mine = mine
        self.region = region
        self.action = action
        self.relationship = relationship
        self.building = building
        self.tool = tool
        self.fishing = fishing
        self.cooking = cooking
        self.mods_option = mods_option
        self.money = money
        self.combat = combat
        self.season = season
        self.quest_rules = dict()

    def initialize_rules(self):
        self.quest_rules.update({
            Quest.introductions: self.region.can_reach(Region.town),
            Quest.how_to_win_friends: self.can_complete_quest(Quest.introductions),
            Quest.getting_started: self.has(Vegetable.parsnip) & self.tool.has_tool(Tool.hoe) & self.tool.can_water(0),
            Quest.to_the_beach: self.region.can_reach(Region.beach),
            Quest.raising_animals: self.can_complete_quest(Quest.getting_started) & self.building.has_building(Building.coop),
            Quest.advancement: self.can_complete_quest(Quest.getting_started) & self.has(Craftable.scarecrow),
            Quest.archaeology: (self.tool.has_tool(Tool.hoe) | self.mine.can_mine_in_the_mines_floor_1_40() | self.skill.can_fish()) & self.region.can_reach(Region.museum),
            Quest.meet_the_wizard: self.region.can_reach(Region.town) & self.region.can_reach(Region.community_center) & self.region.can_reach(Region.wizard_tower),
            Quest.forging_ahead: self.has(Ore.copper) & self.has(Machine.furnace),
            Quest.smelting: self.has(MetalBar.copper),
            Quest.initiation: self.mine.can_mine_in_the_mines_floor_1_40(),
            Quest.robins_lost_axe: self.season.has(Season.spring) & self.region.can_reach(Region.forest) & self.relationship.can_meet(NPC.robin),
            Quest.jodis_request: self.season.has(Season.spring) & self.has(Vegetable.cauliflower) & self.relationship.can_meet(NPC.jodi),
            Quest.mayors_shorts: self.season.has(Season.summer) & self.region.can_reach(Region.ranch) &
                                 (self.relationship.has_hearts(NPC.marnie, 2) | (self.mod.magic.can_blink())) & self.relationship.can_meet(NPC.lewis),
            Quest.blackberry_basket: self.season.has(Season.fall) & self.relationship.can_meet(NPC.linus),
            Quest.marnies_request: self.relationship.has_hearts(NPC.marnie, 3) & self.has(Forageable.cave_carrot) & self.region.can_reach(Region.ranch),
            Quest.pam_is_thirsty: self.season.has(Season.summer) & self.has(ArtisanGood.pale_ale) & self.relationship.can_meet(NPC.pam),
            Quest.a_dark_reagent: self.season.has(Season.winter) & self.has(Loot.void_essence) & self.relationship.can_meet(NPC.wizard),
            Quest.cows_delight: self.season.has(Season.fall) & self.has(Vegetable.amaranth) & self.relationship.can_meet(NPC.marnie),
            Quest.the_skull_key: self.received(Wallet.skull_key) & self.region.can_reach(Region.skull_cavern_entrance),
            Quest.crop_research: self.season.has(Season.summer) & self.has(Fruit.melon) & self.relationship.can_meet(NPC.demetrius),
            Quest.knee_therapy: self.season.has(Season.summer) & self.has(Fruit.hot_pepper) & self.relationship.can_meet(NPC.george),
            Quest.robins_request: self.season.has(Season.winter) & self.has(Material.hardwood) & self.relationship.can_meet(NPC.robin),
            Quest.qis_challenge: self.mine.can_mine_in_the_skull_cavern(),
            Quest.the_mysterious_qi: self.region.can_reach(Region.bus_tunnel) & self.has(ArtisanGood.battery_pack) & self.region.can_reach(Region.desert) & self.has(Forageable.rainbow_shell) & self.has(Vegetable.beet) & self.has(Loot.solar_essence),
            Quest.carving_pumpkins: self.season.has(Season.fall) & self.has(Vegetable.pumpkin) & self.relationship.can_meet(NPC.caroline),
            Quest.a_winter_mystery: self.season.has(Season.winter) & self.region.can_reach(Region.town),
            Quest.strange_note: self.has(Forageable.secret_note) & self.region.can_reach(Region.secret_woods) & self.has(ArtisanGood.maple_syrup),
            Quest.cryptic_note: self.has(Forageable.secret_note) & self.region.can_reach(Region.skull_cavern_100),
            Quest.fresh_fruit: self.season.has(Season.spring) & self.has(Fruit.apricot) & self.relationship.can_meet(NPC.emily),
            Quest.aquatic_research: self.season.has(Season.summer) & self.has(Fish.pufferfish) & self.relationship.can_meet(NPC.demetrius),
            Quest.a_soldiers_star: self.season.has(Season.summer) & self.time.has_year_two() & self.has(Fruit.starfruit) & self.relationship.can_meet(NPC.kent),
            Quest.mayors_need: self.season.has(Season.summer) & self.has(ArtisanGood.truffle_oil) & self.relationship.can_meet(NPC.lewis),
            Quest.wanted_lobster: self.season.has(Season.fall) & self.season.has(Season.fall) & self.has(Fish.lobster) & self.relationship.can_meet(NPC.gus),
            Quest.pam_needs_juice: self.season.has(Season.fall) & self.has(ArtisanGood.battery_pack) & self.relationship.can_meet(NPC.pam),
            Quest.fish_casserole: self.relationship.has_hearts(NPC.jodi, 4) & self.has(Fish.largemouth_bass) & self.region.can_reach(Region.sam_house),
            Quest.catch_a_squid: self.season.has(Season.winter) & self.has(Fish.squid) & self.relationship.can_meet(NPC.willy),
            Quest.fish_stew: self.season.has(Season.winter) & self.has(Fish.albacore) & self.relationship.can_meet(NPC.gus),
            Quest.pierres_notice: self.season.has(Season.spring) & self.has(Meal.sashimi) & self.relationship.can_meet(NPC.pierre),
            Quest.clints_attempt: self.season.has(Season.winter) & self.has(Mineral.amethyst) & self.relationship.can_meet(NPC.emily),
            Quest.a_favor_for_clint: self.season.has(Season.winter) & self.has(MetalBar.iron) & self.relationship.can_meet(NPC.clint),
            Quest.staff_of_power: self.season.has(Season.winter) & self.has(MetalBar.iridium) & self.relationship.can_meet(NPC.wizard),
            Quest.grannys_gift: self.season.has(Season.spring) & self.has(Forageable.leek) & self.relationship.can_meet(NPC.evelyn),
            Quest.exotic_spirits: self.season.has(Season.winter) & self.has(Forageable.coconut) & self.relationship.can_meet(NPC.gus),
            Quest.catch_a_lingcod: self.season.has(Season.winter) & self.has(Fish.lingcod) & self.relationship.can_meet(NPC.willy),
            Quest.dark_talisman: self.wallet.has_rusty_key() & self.region.can_reach(Region.railroad) & self.relationship.can_meet(NPC.krobus) & self.region.can_reach(Region.mutant_bug_lair),
            Quest.goblin_problem: self.region.can_reach(Region.witch_swamp) & self.has(ArtisanGood.void_mayonnaise),
            Quest.magic_ink: self.region.can_reach(Region.witch_hut) & self.relationship.can_meet(NPC.wizard),
            Quest.the_pirates_wife: self.region.can_reach(Region.island_west) & self.relationship.can_meet(NPC.kent) &
                                    self.relationship.can_meet(NPC.gus) & self.relationship.can_meet(NPC.sandy) & self.relationship.can_meet(NPC.george) &
                                    self.relationship.can_meet(NPC.wizard) & self.relationship.can_meet(NPC.willy),
        })

    def update_rules(self, new_rules: Dict[str, StardewRule]):
        self.quest_rules.update(new_rules)

    def can_complete_quest(self, quest: str) -> StardewRule:
        return Has(quest, self.quest_rules)
