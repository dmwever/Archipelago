import dataclasses
from pathlib import Path

from rule_builder.rules import False_, Rule

from ..locations.Scenarios import Age2ScenarioData
from ..logic.ScenarioLogic import ScenarioLogic, ScenarioStartingState
from . import bases

RETIRED_FLAGS = {
    "starting_gold_mine",
    "starting_stone_mine",
    "starting_trees",
    "starting_bushes",
    "starting_hunting",
    "starting_fish",
    "starting_sheep",
    "starting_oysters",
    "starting_whales",
    "starting_relics",
}

GUARDED_QUESTIONS = {
    "_mine_gold": "gold_count",
    "_quarry_stone": "stone_count",
    "_hunt": "hunt_count",
    "_herd": "herd_count",
    "_forage": "bush_count",
    "_fish_from_shore": "shore_fish_count",
    "_fish_by_boat": "deep_fish_count",
    "_oysters_from_shore": "oyster_count",
    "_oysters_by_boat": "oyster_count",
    "_hunt_whales": "whale_count",
    "_collect_relics": "relic_count",
}

OYSTERS_AND_WHALES = {
    "can_gather_oysters": "oyster_count",
    "can_hunt_whales": "whale_count",
}

SCANNED_AMOUNT = 1400

APWORLD = Path(__file__).parent.parent

class ScanDecidesResourcesTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def scenarios(self) -> list[ScenarioLogic]:
        return sorted(
            self.world.rules.logic.scenarios,
            key=lambda scenario: scenario.scenario.name,
        )

    def is_statically_false(self, rule: Rule) -> bool:
        return rule.resolve(self.world).always_false

    def scan(self, scenario: ScenarioLogic, **counts: int) -> None:
        scenario.economy.counts = dataclasses.replace(scenario.economy.counts, **counts)
        self.world.rules.logic.scenario_answers.clear()

class TestNoStartingResourceFlagRemains(ScanDecidesResourcesTestBase):

    def test_the_starting_state_has_no_starting_resource_field(self):
        fields = {field.name for field in dataclasses.fields(ScenarioStartingState)}
        self.assertEqual(set(), fields & RETIRED_FLAGS)

    def test_no_rule_reads_a_starting_resource_flag(self):
        sources = [
            path for path in APWORLD.rglob("*.py")
            if "test" not in path.relative_to(APWORLD).parts
        ]
        flags_still_read = {
            f"{path.relative_to(APWORLD)}: {flag}" for path in sources
            for flag in RETIRED_FLAGS
            if flag in path.read_text(encoding="utf-8")
        }
        self.assertEqual(set(), flags_still_read)

class TestEveryGuardedQuestionKeepsItsScanGuard(ScanDecidesResourcesTestBase):

    def test_a_zero_count_answers_false_before_anything_else(self):
        self.build()
        for scenario in self.scenarios():
            self.scan(scenario, **dict.fromkeys(GUARDED_QUESTIONS.values(), 0))
            for question in GUARDED_QUESTIONS:
                with self.subTest(scenario=scenario.scenario.name, question=question):
                    answer = getattr(scenario.economy, question)()
                    self.assertIsInstance(answer, False_)

    def test_wood_has_no_scan_guard(self):
        self.build()
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        self.scan(scenario, **dict.fromkeys(GUARDED_QUESTIONS.values(), 0))
        self.assertFalse(self.is_statically_false(scenario.economy.can_chop_some()))

class TestOystersAndWhalesFollowTheScan(ScanDecidesResourcesTestBase):

    def test_oysters_and_whales_are_unreachable_in_every_scenario(self):
        self.build()
        for scenario in self.scenarios():
            for question in OYSTERS_AND_WHALES:
                with self.subTest(scenario=scenario.scenario.name, question=question):
                    answer = getattr(scenario.economy, question)()
                    self.assertTrue(self.is_statically_false(answer))

    def test_a_scanned_oyster_or_whale_opens_its_gathering(self):
        self.build()
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_6)
        self.assertFalse(self.world.rules.logic.is_impossible(scenario.has_water_access()))
        scanned = scenario.economy.counts
        for question, count in OYSTERS_AND_WHALES.items():
            with self.subTest(question=question):
                scenario.economy.counts = scanned
                self.scan(scenario, **{count: SCANNED_AMOUNT})
                answer = getattr(scenario.economy, question)()
                self.assertFalse(self.is_statically_false(answer))
