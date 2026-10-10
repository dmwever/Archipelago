from rule_builder.rules import Rule

from ..Options import IncludeUniqueUnits, Techsanity, Unitsanity
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..items.Items import Resource
from ..logic.custom_logic.ScenarioQuestions import ScenarioCanBuild, ScenarioHasReached
from .bases import Age2RuleTestBase

EVERYTHING = dict(techsanity=Techsanity.option_all, unitsanity=Unitsanity.option_all,
                  include_unique_units=IncludeUniqueUnits.option_both, shuffle_ages=True)


class TestScenarioQuestionsAnswerTheSameThing(Age2RuleTestBase):
    """The questions exist to be resolved once instead of thousands of times.

    That is only sound because the answer cannot differ: resolution depends on the world's options
    and on the scenario, and both are fixed before any rule is built. These tests are what says so
    - if a question ever resolved to something other than the rule it stands for, every rule built
    on it would be wrong and nothing else would notice.
    """

    def behind(self, resolved):
        """The rule a question stands for. A question that collapses to True_ or False_ is handed
        straight back rather than wrapped, so unwrap only when there is a wrapper."""
        return getattr(resolved, "answer", resolved)

    def test_a_building_question_matches_the_rule_it_stands_for(self):
        world = self.build(**EVERYTHING)
        for scenario in world.rules.logic.scenarios:
            for building in (Age2BuildingData.BARRACKS, Age2BuildingData.CASTLE,
                             Age2BuildingData.MILL, Age2BuildingData.DOCK):
                if not scenario.civilization.can_build(building):
                    continue
                with self.subTest(scenario=scenario.scenario.name, building=building.name):
                    question = ScenarioCanBuild(scenario=scenario.scenario, building=building)
                    asked = question.resolve(world)
                    direct = question.answer(scenario).resolve(world)
                    self.assertIs(self.behind(asked), direct)

    def test_an_age_question_matches_the_rule_it_stands_for(self):
        world = self.build(**EVERYTHING)
        for scenario in world.rules.logic.scenarios:
            for age in Age2AgeData:
                with self.subTest(scenario=scenario.scenario.name, age=age.name):
                    asked = ScenarioHasReached(scenario=scenario.scenario, age=age).resolve(world)
                    direct = (scenario.ages.can_reach(age)
                              | scenario.ages.start_past(age)).resolve(world)
                    self.assertIs(self.behind(asked), direct)

    def test_asking_twice_gives_the_same_object(self):
        world = self.build(**EVERYTHING)
        scenario = world.rules.logic.scenarios[0].scenario
        question = ScenarioCanBuild(scenario=scenario, building=Age2BuildingData.BARRACKS)
        self.assertIs(question.resolve(world), question.resolve(world))
        # and a separately constructed question is the same question
        twin = ScenarioCanBuild(scenario=scenario, building=Age2BuildingData.BARRACKS)
        self.assertIs(question.resolve(world), twin.resolve(world))

    def test_a_question_explains_itself_in_one_line(self):
        """What the wrapper is for. Without it the explanation unrolls the villagers, the
        civilisation, the age and the two buildings of the age below."""
        world = self.build(**EVERYTHING)
        scenario = world.rules.logic.scenarios[0]
        question = ScenarioCanBuild(scenario=scenario.scenario,
                                    building=Age2BuildingData.BARRACKS)
        explained = question.resolve(world).explain_str()
        self.assertEqual(explained,
                         f"{scenario.scenario.scenario_name} can build a Barracks")

    def test_a_false_question_still_collapses_its_parent(self):
        """The wrapper forwards always_false as a property, so And still short-circuits through
        it. Without that the tree grows by a fifth and dead branches survive to be evaluated."""
        world = self.build(**EVERYTHING)
        huns = [s for s in world.rules.logic.scenarios if s.scenario.name == "AP_ATTILA_1"][0]
        # The Huns build no houses, so this is False before anything else is asked.
        resolved = huns.buildings.can_build_building(Age2BuildingData.HOUSE).resolve(world)
        self.assertTrue(resolved.always_false)

    def test_the_cache_belongs_to_the_world(self):
        """Two seeds answer for themselves - the cache belongs to that seed's Logic, not to the
        World and not to the rule class. The options differ between them, so sharing would be the
        one way this could silently produce a wrong rule."""
        first = self.build(**EVERYTHING)
        second = self.build(techsanity=Techsanity.option_none, unitsanity=Unitsanity.option_none)
        self.assertIsNot(first.rules.logic.scenario_answers, second.rules.logic.scenario_answers)
        self.assertTrue(first.rules.logic.scenario_answers)


class TestTheAnswersAreActuallyShared(Age2RuleTestBase):

    def test_one_answer_per_question_asked(self):
        """The point of the exercise: one answer per question, not one per time it is asked. A
        question is about one scenario and one thing - a tech, a unit, a building, an age, a
        resource - so there can never be more answers than that."""
        world = self.build(**EVERYTHING)
        logic = world.rules.logic
        subjects = (len(Age2TechData) + len(Age2UnitData) + len(Age2BuildingData)
                    + len(Age2AgeData) + len(Resource))
        self.assertTrue(logic.scenario_answers)
        self.assertLessEqual(len(logic.scenario_answers), len(logic.scenarios) * subjects)
        for answer in logic.scenario_answers.values():
            self.assertIsInstance(answer, Rule.Resolved)
        self.assertFalse(logic.scenario_answers_open, "a question was left part-way answered")
        self.assertFalse(logic.budget_totals_open, "a budget total was left part-way resolved")
        self.assertTrue(logic.budget_totals, "no budget total was resolved, so nothing above was tried")


class TestOneScenarioLogicPerScenario(Age2RuleTestBase):
    """The rules side and the logic side have to be looking at the same object.

    A question is memoised against Logic.scenario_answers and answered through
    logic.for_scenario(...), whichever object built it. A second ScenarioLogic per scenario would
    carry its own starting state and its own mercenary grants, and the two would answer the same
    question apart the moment either stopped being pure.
    """

    def test_the_rules_read_the_logic_owned_object(self):
        world = self.build(**EVERYTHING)
        logic = world.rules.logic
        self.assertEqual(len(world.rules.scenario_rules), len(logic.scenarios))
        for rules in world.rules.scenario_rules:
            with self.subTest(rules.scenario.scenario_name):
                self.assertIs(rules.scenario_logic, logic.for_scenario(rules.scenario))

    def test_there_is_exactly_one_per_scenario(self):
        world = self.build(**EVERYTHING)
        owned = {id(scenario_logic) for scenario_logic in world.rules.logic.scenarios}
        owned.update(id(rules.scenario_logic) for rules in world.rules.scenario_rules)
        self.assertEqual(len(owned), len(world.rules.logic.scenarios))
