import dataclasses
import json
import random
import unittest
from pathlib import Path
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import Has, True_
from test.general import setup_solo_multiworld

from . import bases
from .. import Age2World
from ..Options import (
    Caveman,
    ExistingTechs,
    MarketTrade,
    PartnerTrade,
    ShuffleAges,
    ShuffleVillager,
    Techsanity,
    Unitsanity,
)
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.connections.ScenarioResources import EMPTY, Tier
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData
from ..logic.custom_logic.EconomyRoutes import (
    EconomyRoute,
    EconomyRoutes,
    EconomyRoutesYield,
    Strength,
)
from ..logic.scenarios import ScenarioResourceLogic as economy_module

EASY_SOURCE_ANSWERS = Path(__file__).with_name("easy_source_answers.json")

EQUIVALENCE_CONFIGS: dict[str, dict] = {
    "defaults": {},
    "market trade": {
        "market_trade": MarketTrade.option_true,
    },
    "allies and enemies": {
        "partner_trade": PartnerTrade.option_allies_and_enemies,
    },
    "no partner trade": {
        "partner_trade": PartnerTrade.option_none,
    },
    "professions and caveman": {
        "shuffle_villager": ShuffleVillager.option_include_professions,
        "caveman": Caveman.option_true,
    },
    "dark age, everything shuffled": {
        "existing_techs": ExistingTechs.option_start_in_dark_age,
        "unitsanity": Unitsanity.option_all,
        "market_trade": MarketTrade.option_true,
    },
    "nothing shuffled": {
        "techsanity": Techsanity.option_none,
        "unitsanity": Unitsanity.option_none,
        "shuffle_ages": ShuffleAges.option_false,
    },
}

RANDOM_STATES = 300


class EasySourceEquivalenceBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def build_seeded(self, **options) -> Age2World:
        world = setup_solo_multiworld(Age2World, (), seed=19).worlds[1]
        world.options.enabled_campaigns.value = set(self.campaigns)
        world.options.starting_campaigns.value = set(self.starting_campaigns)
        for name, value in options.items():
            getattr(world.options, name).value = value
        for step in ("generate_early", "create_regions", "create_items", "set_rules"):
            getattr(world, step)()
        self.world = world
        self.multiworld = world.multiworld
        return world

    def collectable_items(self) -> list:
        events = [
            location.item for location in self.multiworld.get_filled_locations(self.world.player)
        ]
        return sorted(list(self.multiworld.itempool) + events, key=lambda item: item.name)

    def states(self) -> list[CollectionState]:
        items = self.collectable_items()
        rng = random.Random(19)
        picks: list[list] = [[], items]
        for _ in range(RANDOM_STATES):
            keep = rng.random()
            picks.append([item for item in items if rng.random() < keep])
        states = []
        for pick in picks:
            state = CollectionState(self.multiworld)
            for item in pick:
                state.collect(item, prevent_sweep=True)
            states.append(state)
        return states

    def easy_source_answers(self) -> dict[str, object]:
        scenarios = sorted(
            self.world.rules.logic.scenarios,
            key=lambda scenario: scenario.scenario.name,
        )
        questions = [(scenario, resource) for scenario in scenarios for resource in Resource]
        rules = [
            scenario.economy.has_easy_source(resource).resolve(self.world)
            for scenario, resource in questions
        ]
        return {
            "questions": [
                f"{scenario.scenario.name}.{resource.name}" for scenario, resource in questions
            ],
            "states": [
                "".join("1" if rule(state) else "0" for rule in rules) for state in self.states()
            ],
        }

    def every_config_answers(self) -> dict[str, dict]:
        answers = {}
        for name, options in EQUIVALENCE_CONFIGS.items():
            self.build_seeded(**options)
            answers[name] = self.easy_source_answers()
        return answers


class TestEveryEasySourceAnswersAsBefore(EasySourceEquivalenceBase):

    def test_every_scenario_and_resource_answers_as_the_rule_trees_did(self):
        before = json.loads(EASY_SOURCE_ANSWERS.read_text())
        for name, options in EQUIVALENCE_CONFIGS.items():
            with self.subTest(config=name):
                self.build_seeded(**options)
                now = self.easy_source_answers()
                self.assertEqual(before[name]["questions"], now["questions"])
                answer_pairs = zip(before[name]["states"], now["states"])
                moved = [
                    index for index, (old, new) in enumerate(answer_pairs)
                    if old != new
                ]
                self.assertEqual(len(before[name]["states"]), len(now["states"]))
                self.assertEqual([], moved)


class EconomyRoutesTestBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    LUMBER = Age2ItemData.TOWN_CENTER_WOOD.item_name

    def easy_wood(self, *routes: EconomyRoute):
        economy = EconomyRoutes(routes=routes, label="The test scenario")
        return EconomyRoutesYield(
            economy=economy,
            resource=Resource.WOOD,
            strength=Strength.AT_SCALE,
        ).resolve(self.world)


class TestRoutesSeedingOneAnotherResolve(EconomyRoutesTestBase):

    def cogs_and_lumberjacks(self) -> tuple[EconomyRoute, EconomyRoute]:
        cogs = EconomyRoute(
            name="Trade Cogs",
            yields={Resource.WOOD: Strength.AT_SCALE},
            leaf=True_(),
            needs={Resource.WOOD: Strength.SOME},
        )
        lumberjacks = EconomyRoute(
            name="Lumberjacks",
            yields={Resource.WOOD: Strength.SOME},
            leaf=Has(self.LUMBER),
        )
        return cogs, lumberjacks

    def test_a_cycle_runs_when_the_second_route_seeds_it(self):
        self.build()
        easy_wood = self.easy_wood(*self.cogs_and_lumberjacks())
        self.assertTrue(easy_wood(self.state_with(self.LUMBER)))

    def test_a_cycle_does_not_run_when_nothing_seeds_it(self):
        self.build()
        easy_wood = self.easy_wood(*self.cogs_and_lumberjacks())
        self.assertFalse(easy_wood(self.state_without(self.LUMBER)))


class TestARouteNeverSeedsItself(EconomyRoutesTestBase):

    def test_a_route_needing_only_its_own_yield_never_runs(self):
        self.build()
        cogs = EconomyRoute(
            name="Trade Cogs",
            yields={Resource.WOOD: Strength.AT_SCALE},
            leaf=True_(),
            needs={Resource.WOOD: Strength.SOME},
        )
        easy_wood = self.easy_wood(cogs)
        self.assertTrue(easy_wood.always_false)
        self.assertFalse(easy_wood(self.state_without()))


class TestStructuralFieldingPaysForNothing(EconomyRoutesTestBase):

    def test_only_the_paid_form_asks_can_sustain(self):
        self.build()
        sustain = economy_module.ScenarioResourceLogic.can_sustain
        with mock.patch.object(
            economy_module.ScenarioResourceLogic,
            "can_sustain",
            autospec=True,
            side_effect=sustain,
        ) as asked:
            for scenario in self.world.rules.logic.scenarios:
                for line in Age2UnitLineData:
                    scenario.units.can_field_structurally(line)
                    for age in Age2AgeData:
                        scenario.units.can_field_structurally(line, age)
            self.assertEqual(0, asked.call_count)
            attila_1 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
            attila_1.units.can_field(Age2UnitLineData.MILITIA_LINE, Age2AgeData.DARK)
            self.assertGreater(asked.call_count, 0)


class TestStructuralCounteringPaysForNothing(EconomyRoutesTestBase):
    """A guard rule states its own costs as routes of *some*, so the counter behind it must pay
    for nothing: `can_counter_structurally` is to `can_counter` what structural fielding is to
    fielding."""

    def test_only_the_paid_form_asks_can_sustain(self):
        self.build()
        sustain = economy_module.ScenarioResourceLogic.can_sustain
        with mock.patch.object(
            economy_module.ScenarioResourceLogic,
            "can_sustain",
            autospec=True,
            side_effect=sustain,
        ) as asked:
            for scenario in self.world.rules.logic.scenarios:
                for target in Age2UnitLineData:
                    for age in Age2AgeData:
                        scenario.units.can_counter_structurally(target, age)
            self.assertEqual(0, asked.call_count)
            attila_1 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
            attila_1.units.can_counter(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE)
            self.assertGreater(asked.call_count, 0)

    def test_the_structural_counter_answers_wherever_the_paid_one_does(self):
        """Dropping the price never drops a way to counter: anything the paid counter offers the
        structural one offers too."""
        self.build()
        for scenario in self.world.rules.logic.scenarios:
            for target in Age2UnitLineData:
                for age in Age2AgeData:
                    paid = scenario.units.can_counter(target, age).resolve(self.world)
                    if paid.always_false:
                        continue
                    structural = scenario.units.can_counter_structurally(
                        target, age).resolve(self.world)
                    with self.subTest(scenario=scenario.scenario.name, target=target.name,
                                      age=age.name):
                        self.assertFalse(structural.always_false)


class TestOystersGuardedByTheirOwnGold(EconomyRoutesTestBase):
    SCENARIO = Age2ScenarioData.AP_ATTILA_6
    BARBAROSSA_3_OYSTERS = 1400

    def with_open_oysters(self):
        resources = self.SCENARIO.resources
        open_ground = resources[Tier.OPEN] if Tier.OPEN in resources else EMPTY
        return mock.patch.dict(
            self.SCENARIO.resources,
            {Tier.OPEN: dataclasses.replace(open_ground, oyster_count=self.BARBAROSSA_3_OYSTERS)},
        )

    def test_easy_gold_through_guarded_oysters_resolves(self):
        self.build()
        scenario = self.world.rules.logic.for_scenario(self.SCENARIO)
        self.assertFalse(self.world.rules.logic.is_impossible(scenario.has_water_access()))
        self.assertTrue(scenario.military.can_guard_boats())
        with self.with_open_oysters():
            scenario.economy.counts = dataclasses.replace(
                scenario.economy.counts,
                oyster_count=self.BARBAROSSA_3_OYSTERS,
            )
            self.world.rules.logic.scenario_answers.clear()
            easy_gold = scenario.economy.has_easy_source(Resource.GOLD).resolve(self.world)
            self.assertFalse(easy_gold.always_false)
            self.assertTrue(easy_gold(self.state_without()))
        self.assertEqual(set(), self.world.rules.logic.scenario_answers_open)


class TestAScenarioRouteOfSomeIsItsOwnQuestion(EconomyRoutesTestBase):

    def test_a_scenario_route_of_some_answers_some_and_not_at_scale(self):
        self.build()
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        scenario.starting_state.some_resource_sources[Resource.STONE] = Has(self.LUMBER)
        self.world.rules.logic.scenario_answers.clear()
        state = self.state_with(self.LUMBER)
        some_stone = scenario.economy.has_some_source(Resource.STONE).resolve(self.world)
        easy_stone = scenario.economy.has_easy_source(Resource.STONE).resolve(self.world)
        self.assertTrue(some_stone(state))
        self.assertFalse(easy_stone(state))


class TestTheEconomyIsWorkedOutOncePerState(EconomyRoutesTestBase):

    def test_every_resource_shares_one_resolution(self):
        self.build()
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        answers = [
            scenario.economy.has_easy_source(resource).resolve(self.world)
            for resource in Resource
        ]
        state = CollectionState(self.multiworld)
        with mock.patch.object(
            EconomyRoutes.Resolved,
            "running",
            autospec=True,
            side_effect=EconomyRoutes.Resolved.running,
        ) as worked_out:
            for answer in answers:
                answer(state)
        self.assertEqual(1, worked_out.call_count)


if __name__ == "__main__":
    unittest.main()
