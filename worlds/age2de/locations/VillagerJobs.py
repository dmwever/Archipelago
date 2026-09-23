import enum

class VillagerSex:
    male = "Male"
    female = "Female"

@enum.unique
class Age2VillagerJobData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, job_name: str,
                 sex: VillagerSex, game_id: int) -> None:
        self.id = id
        self.location_name = location_name
        self.job_name = job_name
        self.sex = sex
        self.game_id = game_id

    # 560 - 799 = Villager jobs. Twelve jobs in both sexes, ordered by the male form's game id.
    FISHERMAN_MALE         = 560, "Own Fisherman (Male)", "Fisherman", VillagerSex.male, 56
    FISHERMAN_FEMALE       = 561, "Own Fisherman (Female)", "Fisherman", VillagerSex.female, 57
    BUILDER_MALE           = 562, "Own Builder (Male)", "Builder", VillagerSex.male, 118
    BUILDER_FEMALE         = 563, "Own Builder (Female)", "Builder", VillagerSex.female, 212
    FORAGER_MALE           = 564, "Own Forager (Male)", "Forager", VillagerSex.male, 120
    FORAGER_FEMALE         = 565, "Own Forager (Female)", "Forager", VillagerSex.female, 354
    HUNTER_MALE            = 566, "Own Hunter (Male)", "Hunter", VillagerSex.male, 122
    HUNTER_FEMALE          = 567, "Own Hunter (Female)", "Hunter", VillagerSex.female, 216
    LUMBERJACK_MALE        = 568, "Own Lumberjack (Male)", "Lumberjack", VillagerSex.male, 123
    LUMBERJACK_FEMALE      = 569, "Own Lumberjack (Female)", "Lumberjack", VillagerSex.female, 218
    STONE_MINER_MALE       = 570, "Own Stone Miner (Male)", "Stone Miner", VillagerSex.male, 124
    STONE_MINER_FEMALE     = 571, "Own Stone Miner (Female)", "Stone Miner", VillagerSex.female, 220
    REPAIRER_MALE          = 572, "Own Repairer (Male)", "Repairer", VillagerSex.male, 156
    REPAIRER_FEMALE        = 573, "Own Repairer (Female)", "Repairer", VillagerSex.female, 222
    FARMER_MALE            = 574, "Own Farmer (Male)", "Farmer", VillagerSex.male, 259
    FARMER_FEMALE          = 575, "Own Farmer (Female)", "Farmer", VillagerSex.female, 214
    GOLD_MINER_MALE        = 576, "Own Gold Miner (Male)", "Gold Miner", VillagerSex.male, 579
    GOLD_MINER_FEMALE      = 577, "Own Gold Miner (Female)", "Gold Miner", VillagerSex.female, 581
    SHEPHERD_MALE          = 578, "Own Shepherd (Male)", "Shepherd", VillagerSex.male, 592
    SHEPHERD_FEMALE        = 579, "Own Shepherd (Female)", "Shepherd", VillagerSex.female, 590
    HERDER_MALE            = 580, "Own Herder (Male)", "Herder", VillagerSex.male, 1892
    HERDER_FEMALE          = 581, "Own Herder (Female)", "Herder", VillagerSex.female, 1891
    OYSTER_GATHERER_MALE   = 582, "Own Oyster Gatherer (Male)", "Oyster Gatherer", VillagerSex.male, 2333
    OYSTER_GATHERER_FEMALE = 583, "Own Oyster Gatherer (Female)", "Oyster Gatherer", VillagerSex.female, 2334
