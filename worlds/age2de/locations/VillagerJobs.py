import enum

from ..items.Items import Age2ItemData
from .UnitLines import Age2UnitLineData

@enum.unique
class Age2VillagerJobData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, job_name: str,
                 line: Age2UnitLineData, game_id: int, item: Age2ItemData) -> None:
        self.id = id
        self.location_name = location_name
        self.job_name = job_name
        self.building = None
        self.line = line
        self.game_id = game_id
        self.item = item

    # 560 - 799 = Villager jobs. Twelve jobs in both sexes, ordered by the male form's game id.
    FISHERMAN_MALE         = 560, "Own Fisherman (Male)", "Fisherman", Age2UnitLineData.VILLAGER_MALE_LINE, 56, Age2ItemData.PROFESSION_FISHERMAN
    FISHERMAN_FEMALE       = 561, "Own Fisherman (Female)", "Fisherman", Age2UnitLineData.VILLAGER_FEMALE_LINE, 57, Age2ItemData.PROFESSION_FISHERMAN
    BUILDER_MALE           = 562, "Own Builder (Male)", "Builder", Age2UnitLineData.VILLAGER_MALE_LINE, 118, Age2ItemData.PROFESSION_BUILDER
    BUILDER_FEMALE         = 563, "Own Builder (Female)", "Builder", Age2UnitLineData.VILLAGER_FEMALE_LINE, 212, Age2ItemData.PROFESSION_BUILDER
    FORAGER_MALE           = 564, "Own Forager (Male)", "Forager", Age2UnitLineData.VILLAGER_MALE_LINE, 120, Age2ItemData.PROFESSION_FORAGER
    FORAGER_FEMALE         = 565, "Own Forager (Female)", "Forager", Age2UnitLineData.VILLAGER_FEMALE_LINE, 354, Age2ItemData.PROFESSION_FORAGER
    HUNTER_MALE            = 566, "Own Hunter (Male)", "Hunter", Age2UnitLineData.VILLAGER_MALE_LINE, 122, Age2ItemData.PROFESSION_HUNTER
    HUNTER_FEMALE          = 567, "Own Hunter (Female)", "Hunter", Age2UnitLineData.VILLAGER_FEMALE_LINE, 216, Age2ItemData.PROFESSION_HUNTER
    LUMBERJACK_MALE        = 568, "Own Lumberjack (Male)", "Lumberjack", Age2UnitLineData.VILLAGER_MALE_LINE, 123, Age2ItemData.PROFESSION_LUMBERJACK
    LUMBERJACK_FEMALE      = 569, "Own Lumberjack (Female)", "Lumberjack", Age2UnitLineData.VILLAGER_FEMALE_LINE, 218, Age2ItemData.PROFESSION_LUMBERJACK
    STONE_MINER_MALE       = 570, "Own Stone Miner (Male)", "Stone Miner", Age2UnitLineData.VILLAGER_MALE_LINE, 124, Age2ItemData.PROFESSION_STONE_MINER
    STONE_MINER_FEMALE     = 571, "Own Stone Miner (Female)", "Stone Miner", Age2UnitLineData.VILLAGER_FEMALE_LINE, 220, Age2ItemData.PROFESSION_STONE_MINER
    REPAIRER_MALE          = 572, "Own Repairer (Male)", "Repairer", Age2UnitLineData.VILLAGER_MALE_LINE, 156, Age2ItemData.PROFESSION_REPAIRER
    REPAIRER_FEMALE        = 573, "Own Repairer (Female)", "Repairer", Age2UnitLineData.VILLAGER_FEMALE_LINE, 222, Age2ItemData.PROFESSION_REPAIRER
    FARMER_MALE            = 574, "Own Farmer (Male)", "Farmer", Age2UnitLineData.VILLAGER_MALE_LINE, 259, Age2ItemData.PROFESSION_FARMER
    FARMER_FEMALE          = 575, "Own Farmer (Female)", "Farmer", Age2UnitLineData.VILLAGER_FEMALE_LINE, 214, Age2ItemData.PROFESSION_FARMER
    GOLD_MINER_MALE        = 576, "Own Gold Miner (Male)", "Gold Miner", Age2UnitLineData.VILLAGER_MALE_LINE, 579, Age2ItemData.PROFESSION_GOLD_MINER
    GOLD_MINER_FEMALE      = 577, "Own Gold Miner (Female)", "Gold Miner", Age2UnitLineData.VILLAGER_FEMALE_LINE, 581, Age2ItemData.PROFESSION_GOLD_MINER
    SHEPHERD_MALE          = 578, "Own Shepherd (Male)", "Shepherd", Age2UnitLineData.VILLAGER_MALE_LINE, 592, Age2ItemData.PROFESSION_SHEPHERD
    SHEPHERD_FEMALE        = 579, "Own Shepherd (Female)", "Shepherd", Age2UnitLineData.VILLAGER_FEMALE_LINE, 590, Age2ItemData.PROFESSION_SHEPHERD
    HERDER_MALE            = 580, "Own Herder (Male)", "Herder", Age2UnitLineData.VILLAGER_MALE_LINE, 1892, Age2ItemData.PROFESSION_HERDER
    HERDER_FEMALE          = 581, "Own Herder (Female)", "Herder", Age2UnitLineData.VILLAGER_FEMALE_LINE, 1891, Age2ItemData.PROFESSION_HERDER
    OYSTER_GATHERER_MALE   = 582, "Own Oyster Gatherer (Male)", "Oyster Gatherer", Age2UnitLineData.VILLAGER_MALE_LINE, 2333, Age2ItemData.PROFESSION_OYSTER_GATHERER
    OYSTER_GATHERER_FEMALE = 583, "Own Oyster Gatherer (Female)", "Oyster Gatherer", Age2UnitLineData.VILLAGER_FEMALE_LINE, 2334, Age2ItemData.PROFESSION_OYSTER_GATHERER


FOOD_PROFESSIONS: tuple[Age2ItemData, ...] = (
    Age2ItemData.PROFESSION_FARMER,
    Age2ItemData.PROFESSION_FISHERMAN,
    Age2ItemData.PROFESSION_FORAGER,
    Age2ItemData.PROFESSION_HUNTER,
    Age2ItemData.PROFESSION_SHEPHERD,
    Age2ItemData.PROFESSION_HERDER,
)
