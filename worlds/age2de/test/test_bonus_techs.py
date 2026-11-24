from Fill import distribute_items_restrictive
from worlds.AutoWorld import call_all

from ..Options import ExistingTechs, Techsanity
from ..locations.Ages import Age2AgeData
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData
from ..logic.custom_logic.ScenarioQuestions import ScenarioCanResearch
from .bases import Age2RuleTestBase, Age2TestBase

JOAN = Age2CampaignData.JOAN.campaign_name

FEUDAL_START = Age2ScenarioData.AP_JOAN_2
CASTLE_START = Age2ScenarioData.AP_JOAN_4

FIND_MODES = (ExistingTechs.option_find_items, ExistingTechs.option_only_find_units)


class BonusTechTestBase(Age2RuleTestBase):

    def build_in(self, existing_techs: int):
        return self.build(existing_techs=existing_techs, techsanity=Techsanity.option_all)

    def assert_researched_at_start(self, scenario: Age2ScenarioData, tech: Age2TechData):
        techs = self.world.rules.logic.for_scenario(scenario).techs
        self.assertTrue(self.world.pool.techs.researched_at_start(scenario, tech))
        self.assertTrue(self.world.rules.logic.is_impossible(techs.can_research(tech)))

    def assert_never_obtained(self, scenario: Age2ScenarioData, tech: Age2TechData):
        logic = self.world.rules.logic
        techs = logic.for_scenario(scenario).techs
        self.assertFalse(self.world.pool.techs.researched_at_start(scenario, tech))
        self.assertTrue(logic.is_impossible(techs.can_research(tech)))
        self.assertTrue(logic.is_impossible(techs.can_research_structurally(tech)))
        self.assertTrue(logic.is_impossible(techs.has_researched(tech)))
        self.assertTrue(logic.is_impossible(techs.has_researched_structurally(tech)))

    def assert_obtained_by_advancing(self, scenario: Age2ScenarioData, tech: Age2TechData):
        scenario_logic = self.world.rules.logic.for_scenario(scenario)
        self.assertFalse(self.world.pool.techs.researched_at_start(scenario, tech))
        self.assertEqual(
            scenario_logic.ages.can_reach_structurally(tech.age),
            scenario_logic.techs.can_research_structurally(tech),
        )
        self.assertEqual(
            scenario_logic.ages.can_research(tech.age),
            scenario_logic.techs.can_pay_for(tech),
        )
        self.assertFalse(
            self.world.rules.logic.is_impossible(scenario_logic.techs.can_research(tech)),
        )


class TestVanillaBonusTechs(BonusTechTestBase):

    def test_below_the_opening_age_is_researched_at_start(self):
        self.build_in(ExistingTechs.option_vanilla)
        self.assert_researched_at_start(CASTLE_START, Age2TechData.HORSE_COLLAR)

    def test_at_the_opening_age_is_never_obtained(self):
        self.build_in(ExistingTechs.option_vanilla)
        self.assert_never_obtained(FEUDAL_START, Age2TechData.HORSE_COLLAR)
        self.assert_never_obtained(CASTLE_START, Age2TechData.HEAVY_PLOW)

    def test_above_the_opening_age_is_obtained_by_advancing(self):
        self.build_in(ExistingTechs.option_vanilla)
        self.assert_obtained_by_advancing(FEUDAL_START, Age2TechData.HEAVY_PLOW)


class TestFindModesBonusTechs(BonusTechTestBase):

    def test_below_the_opening_age_is_researched_at_start(self):
        for mode in FIND_MODES:
            with self.subTest(mode=mode):
                self.build_in(mode)
                self.assert_researched_at_start(CASTLE_START, Age2TechData.HORSE_COLLAR)

    def test_at_the_opening_age_is_researched_at_start(self):
        for mode in FIND_MODES:
            with self.subTest(mode=mode):
                self.build_in(mode)
                self.assert_researched_at_start(FEUDAL_START, Age2TechData.HORSE_COLLAR)
                self.assert_researched_at_start(CASTLE_START, Age2TechData.HEAVY_PLOW)

    def test_above_the_opening_age_is_obtained_by_advancing(self):
        for mode in FIND_MODES:
            with self.subTest(mode=mode):
                self.build_in(mode)
                self.assert_obtained_by_advancing(FEUDAL_START, Age2TechData.HEAVY_PLOW)


class TestStartInDarkAgeBonusTechs(BonusTechTestBase):

    def test_below_the_opening_age_is_obtained_by_advancing(self):
        self.build_in(ExistingTechs.option_start_in_dark_age)
        self.assert_obtained_by_advancing(CASTLE_START, Age2TechData.HORSE_COLLAR)

    def test_at_the_opening_age_is_obtained_by_advancing(self):
        self.build_in(ExistingTechs.option_start_in_dark_age)
        self.assert_obtained_by_advancing(FEUDAL_START, Age2TechData.HORSE_COLLAR)
        self.assert_obtained_by_advancing(CASTLE_START, Age2TechData.HEAVY_PLOW)

    def test_above_the_opening_age_is_obtained_by_advancing(self):
        self.build_in(ExistingTechs.option_start_in_dark_age)
        self.assert_obtained_by_advancing(FEUDAL_START, Age2TechData.HEAVY_PLOW)


class TestJoanOnlyFindItems(BonusTechTestBase):
    campaigns = [JOAN]
    starting_campaigns = [JOAN]

    def test_heavy_plow_is_researched_at_start_in_castle_starts(self):
        self.build_in(ExistingTechs.option_find_items)
        for scenario in (Age2ScenarioData.AP_JOAN_4, Age2ScenarioData.AP_JOAN_6):
            with self.subTest(scenario=scenario.name):
                self.assert_researched_at_start(scenario, Age2TechData.HEAVY_PLOW)

    def test_heavy_plow_is_offered_on_the_castle_advance_in_feudal_starts(self):
        self.build_in(ExistingTechs.option_find_items)
        self.assertIn(Age2TechData.HEAVY_PLOW.location_name, self.location_names())
        for scenario in (Age2ScenarioData.AP_JOAN_2, Age2ScenarioData.AP_JOAN_3):
            with self.subTest(scenario=scenario.name):
                self.assert_obtained_by_advancing(scenario, Age2TechData.HEAVY_PLOW)


class TestHunsResearchHorseCollarAtAMill(BonusTechTestBase):

    def test_attila_researches_horse_collar_at_a_mill(self):
        for mode in (ExistingTechs.option_vanilla, ExistingTechs.option_start_in_dark_age):
            with self.subTest(mode=mode):
                self.build_in(mode)
                attila_1 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
                self.assertFalse(self.world.pool.techs.researched_at_start(
                    Age2ScenarioData.AP_ATTILA_1,
                    Age2TechData.HORSE_COLLAR,
                ))
                self.assertEqual(
                    ScenarioCanResearch(
                        scenario=Age2ScenarioData.AP_ATTILA_1,
                        tech=Age2TechData.HORSE_COLLAR,
                    ),
                    attila_1.techs.can_research_structurally(Age2TechData.HORSE_COLLAR),
                )
                self.assertNotEqual(
                    attila_1.ages.can_research(Age2AgeData.FEUDAL),
                    attila_1.techs.can_pay_for(Age2TechData.HORSE_COLLAR),
                )


class TestJoanOnlyVanillaSeed(Age2TestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
        "existing_techs": ExistingTechs.option_vanilla,
        "techsanity": Techsanity.option_all,
    }

    def test_horse_collar_holds_no_progression(self):
        distribute_items_restrictive(self.multiworld)
        call_all(self.multiworld, "post_fill")
        self.assertNotIn(
            Age2TechData.HORSE_COLLAR.location_name,
            {location.name for location in self.multiworld.get_locations(self.player)},
        )
