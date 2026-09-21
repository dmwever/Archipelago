"""Option combinations run through the generic world tests.

Nothing in here is written by hand. Subclassing Age2TestBase is what makes
WorldTestBase run test_all_state_can_reach_everything, test_empty_state_can_
reach_something and test_fill against each combination, which is the only
coverage that exercises fill rather than individual rules.
"""

from ..Options import ExistingTechs, LockTechs, ShuffleUniqueTechs, Techsanity
from .bases import Age2TestBase


BOTH_CAMPAIGNS = {
    "enabled_campaigns": {"Attila the Hun", "Joan of Arc"},
    "starting_campaigns": {"Attila the Hun"},
}


class TestTechsanityAllWithItems(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "techsanity": Techsanity.option_all,
               "lock_techs": LockTechs.option_items}


class TestTechsanityAllWithEffects(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "techsanity": Techsanity.option_all,
               "lock_techs": LockTechs.option_effects}


class TestTechsanityUnits(Age2TestBase):
    options = {**BOTH_CAMPAIGNS, "techsanity": Techsanity.option_units}


class TestTechsanityGeneric(Age2TestBase):
    options = {**BOTH_CAMPAIGNS, "techsanity": Techsanity.option_generic}


class TestTechsanityWithUniquesShuffled(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "techsanity": Techsanity.option_all,
               "shuffle_unique_techs": ShuffleUniqueTechs.option_shuffled}


class TestTechsanityStartingInTheDarkAge(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "techsanity": Techsanity.option_all,
               "existing_techs": ExistingTechs.option_start_in_dark_age}


class TestTechsanityOnlyFindingUnits(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "techsanity": Techsanity.option_all,
               "existing_techs": ExistingTechs.option_only_find_units}


class TestJoanAlone(Age2TestBase):
    # The seed where the earliest start is the Feudal Age, so the Feudal Age is
    # handed over rather than shuffled.
    options = {"enabled_campaigns": {"Joan of Arc"},
               "starting_campaigns": {"Joan of Arc"},
               "techsanity": Techsanity.option_all,
               "shuffle_ages": True}


class TestShuffledAges(Age2TestBase):
    options = {**BOTH_CAMPAIGNS, "shuffle_ages": True}


class TestShuffledAgesWithTechsanity(Age2TestBase):
    options = {**BOTH_CAMPAIGNS,
               "shuffle_ages": True,
               "techsanity": Techsanity.option_all}


class TestShuffledAgesStartingInTheDarkAge(Age2TestBase):
    # The combination that makes the age items load bearing: nothing is granted,
    # so every age above the Dark Age has to be earned in every scenario.
    options = {**BOTH_CAMPAIGNS,
               "shuffle_ages": True,
               "techsanity": Techsanity.option_all,
               "existing_techs": ExistingTechs.option_start_in_dark_age}
