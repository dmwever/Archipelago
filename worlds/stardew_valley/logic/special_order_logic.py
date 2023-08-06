from typing import Dict

from .ability_logic import AbilityLogic
from .arcade_logic import ArcadeLogic
from .artisan_logic import ArtisanLogic
from .cooking_logic import CookingLogic
from .has_logic import HasLogic
from .mine_logic import MineLogic
from .money_logic import MoneyLogic
from .received_logic import ReceivedLogic
from .region_logic import RegionLogic
from .relationship_logic import RelationshipLogic
from .season_logic import SeasonLogic
from .skill_logic import SkillLogic
from .time_logic import TimeLogic
from ..stardew_rule import StardewRule, Has
from ..strings.animal_product_names import AnimalProduct
from ..strings.ap_names.transport_names import Transportation
from ..strings.artisan_good_names import ArtisanGood
from ..strings.crop_names import Vegetable, Fruit
from ..strings.fertilizer_names import Fertilizer
from ..strings.fish_names import Fish
from ..strings.forageable_names import Forageable
from ..strings.machine_names import Machine
from ..strings.material_names import Material
from ..strings.metal_names import Mineral
from ..strings.monster_drop_names import Loot
from ..strings.region_names import Region
from ..strings.season_names import Season
from ..strings.special_order_names import SpecialOrder
from ..strings.villager_names import NPC


class SpecialOrderLogic:
    player: int
    received: ReceivedLogic
    has: HasLogic
    region: RegionLogic
    season: SeasonLogic
    time: TimeLogic
    money: MoneyLogic
    arcade: ArcadeLogic
    artisan: ArtisanLogic
    relationship: RelationshipLogic
    skill: SkillLogic
    mine: MineLogic
    cooking: CookingLogic
    ability: AbilityLogic
    special_order_rules: Dict[str, StardewRule]

    def __init__(self, player: int, received: ReceivedLogic, has: HasLogic, region: RegionLogic, season: SeasonLogic, time: TimeLogic, money: MoneyLogic,
                 arcade: ArcadeLogic, artisan: ArtisanLogic, relationship: RelationshipLogic, skill: SkillLogic, mine: MineLogic, cooking: CookingLogic,
                 ability: AbilityLogic):
        self.player = player
        self.received = received
        self.has = has
        self.region = region
        self.season = season
        self.time = time
        self.money = money
        self.arcade = arcade
        self.artisan = artisan
        self.relationship = relationship
        self.skill = skill
        self.mine = mine
        self.cooking = cooking
        self.ability = ability
        self.special_order_rules = dict()

    def initialize_rules(self):
        self.special_order_rules.update({
            SpecialOrder.island_ingredients: self.has_island_transport() & self.ability.can_farm_perfectly() &
                                             self.has(Vegetable.taro_root) & self.has(Fruit.pineapple) & self.has(Forageable.ginger),
            SpecialOrder.cave_patrol: self.ability.can_mine_perfectly() & self.mine.can_mine_to_floor(120),
            SpecialOrder.aquatic_overpopulation: self.ability.can_fish_perfectly(),
            SpecialOrder.biome_balance: self.ability.can_fish_perfectly(),
            SpecialOrder.rock_rejuivenation: self.has(Mineral.ruby) & self.has(Mineral.topaz) & self.has(Mineral.emerald) &
                                             self.has(Mineral.jade) & self.has(Mineral.amethyst) & self.relationship.has_hearts(NPC.emily, 4) &
                                             self.has(ArtisanGood.cloth) & self.region.can_reach(Region.haley_house),
            SpecialOrder.gifts_for_george: self.season.has(Season.spring) & self.has(Forageable.leek),
            SpecialOrder.fragments_of_the_past: self.region.can_reach(Region.dig_site),
            SpecialOrder.gus_famous_omelet: self.has(AnimalProduct.any_egg),
            SpecialOrder.crop_order: self.ability.can_farm_perfectly(),
            SpecialOrder.community_cleanup: self.skill.can_crab_pot(),
            SpecialOrder.the_strong_stuff: self.artisan.can_keg(Vegetable.potato),
            SpecialOrder.pierres_prime_produce: self.ability.can_farm_perfectly(),
            SpecialOrder.robins_project: self.ability.can_chop_perfectly() & self.has(Material.hardwood),
            SpecialOrder.robins_resource_rush: self.ability.can_chop_perfectly() & self.has(Fertilizer.tree) & self.ability.can_mine_perfectly(),
            SpecialOrder.juicy_bugs_wanted_yum: self.has(Loot.bug_meat),
            SpecialOrder.tropical_fish: self.has_island_transport() & self.has(Fish.stingray) & self.has(Fish.blue_discus) & self.has(Fish.lionfish),
            SpecialOrder.a_curious_substance: self.ability.can_mine_perfectly() & self.mine.can_mine_to_floor(80),
            SpecialOrder.prismatic_jelly: self.ability.can_mine_perfectly() & self.mine.can_mine_to_floor(40),
            SpecialOrder.qis_crop: self.ability.can_farm_perfectly() & self.region.can_reach(Region.greenhouse) &
                                   self.region.can_reach(Region.island_west) & self.skill.has_total_level(50) &
                                   self.has(Machine.seed_maker),
            SpecialOrder.lets_play_a_game: self.arcade.has_junimo_kart_max_level(),
            SpecialOrder.four_precious_stones: self.time.has_lived_max_months() & self.has("Prismatic Shard") &
                                               self.ability.can_mine_perfectly_in_the_skull_cavern(),
            SpecialOrder.qis_hungry_challenge: self.ability.can_mine_perfectly_in_the_skull_cavern() & self.ability.has_max_buffs(),
            SpecialOrder.qis_cuisine: self.cooking.can_cook() & (
                        self.money.can_spend_at(Region.saloon, 205000) | self.money.can_spend_at(Region.pierre_store, 170000)),
            SpecialOrder.qis_kindness: self.relationship.can_give_loved_gifts_to_everyone(),
            SpecialOrder.extended_family: self.ability.can_fish_perfectly() & self.has(Fish.angler) & self.has(Fish.glacierfish) &
                                          self.has(Fish.crimsonfish) & self.has(Fish.mutant_carp) & self.has(Fish.legend),
            SpecialOrder.danger_in_the_deep: self.ability.can_mine_perfectly() & self.mine.has_mine_elevator_to_floor(120),
            SpecialOrder.skull_cavern_invasion: self.ability.can_mine_perfectly_in_the_skull_cavern() & self.ability.has_max_buffs(),
            SpecialOrder.qis_prismatic_grange: self.has(Loot.bug_meat) &  # 100 Bug Meat
                                               self.money.can_spend_at(Region.saloon, 24000) &  # 100 Spaghetti
                                               self.money.can_spend_at(Region.blacksmith, 15000) &  # 100 Copper Ore
                                               self.money.can_spend_at(Region.ranch, 5000) &  # 100 Hay
                                               self.money.can_spend_at(Region.saloon, 22000) &  # 100 Salads
                                               self.money.can_spend_at(Region.saloon, 7500) &  # 100 Joja Cola
                                               self.money.can_spend(80000),  # I need this extra rule because money rules aren't additive...
        })

    def update_rules(self, new_rules: Dict[str, StardewRule]):
        self.special_order_rules.update(new_rules)

    def can_complete_special_order(self, special_order: str) -> StardewRule:
        return Has(special_order, self.special_order_rules)

    def has_island_transport(self) -> StardewRule:
        return self.received(Transportation.island_obelisk) | self.received(Transportation.boat_repair)
