from ..Options import (Caveman, IncludeUniqueUnits, ShuffleVillager, Techsanity, Unitsanity,
                       UnitsanityItems)
from .bases import Age2TestBase


BOTH_CAMPAIGNS = {
    "enabled_campaigns": {"Attila the Hun", "Joan of Arc"},
    "starting_campaigns": {"Attila the Hun"},
}


class TestUnitsanityByLine(Age2TestBase):
    options = {**BOTH_CAMPAIGNS, "unitsanity": Unitsanity.option_unit_line}


class TestUnitsanityByUnit(Age2TestBase):
    options = {**BOTH_CAMPAIGNS, "unitsanity": Unitsanity.option_all}


class TestUnitsanityWithUpgradeTokens(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "unitsanity_items": UnitsanityItems.option_upgrades}


class TestUnitsanityWithBuildingItems(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "unitsanity_items": UnitsanityItems.option_buildings}


class TestUnitsanityWithUniqueAndRegionalUnits(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "include_unique_units": IncludeUniqueUnits.option_both}


class TestShuffledVillagerWithoutUnitsanity(Age2TestBase):
    options = {**BOTH_CAMPAIGNS, "shuffle_villager": ShuffleVillager.option_yes}


class TestVillagerProfessionsWithoutUnitsanity(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "shuffle_villager": ShuffleVillager.option_include_professions}


class TestVillagerProfessionsBesideUnitsanity(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "shuffle_villager": ShuffleVillager.option_include_professions}


class TestCavemanWithLineItems(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "caveman": Caveman.option_true}


class TestCavemanWithUpgradeTokens(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "unitsanity_items": UnitsanityItems.option_upgrades,
               "caveman": Caveman.option_true}


class TestCavemanWithBuildingItems(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "unitsanity_items": UnitsanityItems.option_buildings,
               "caveman": Caveman.option_true}


class TestCavemanKeepsGrantedOnlyLinesReachable(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "include_unique_units": IncludeUniqueUnits.option_both,
               "caveman": Caveman.option_true}


class TestCavemanAdaptsToTechsanity(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "techsanity": Techsanity.option_all,
               "caveman": Caveman.option_true}


class TestEveryUnitOptionAtOnce(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "unitsanity": Unitsanity.option_all,
               "unitsanity_items": UnitsanityItems.option_upgrades,
               "shuffle_villager": ShuffleVillager.option_include_professions,
               "include_unique_units": IncludeUniqueUnits.option_both,
               "caveman": Caveman.option_true,
               "techsanity": Techsanity.option_all}
