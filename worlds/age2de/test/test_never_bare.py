import contextlib
import functools
import pathlib
import unittest
from typing import Iterable, Iterator

from BaseClasses import Entrance, Location
from rule_builder.rules import And, Has, HasAll, HasAllCounts, NestedRule, Or, Rule, WrapperRule
from test.general import setup_solo_multiworld

from .. import Age2World
from ..items.Items import Age2ItemData, Resource, SeedResources
from ..locations.Buildings import Age2BuildingData, BuildingOption
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData
from ..logic.Logic import Logic
from ..logic.custom_logic.EconomyRoutes import EconomyRouteRunning, EconomyRoutes
from ..logic.custom_logic.Named import Named
from ..logic.custom_logic.ResourceAmount import HasResourceAmount
from ..logic.custom_logic.ScenarioQuestions import (
    ScenarioCanBuild,
    ScenarioCanResearch,
    ScenarioCanTrain,
    ScenarioHasEasyResource,
    ScenarioHasReached,
    ScenarioHasSomeResource,
    ScenarioQuestion,
)
from ..Options import (
    ExistingTechs,
    IncludeUniqueUnits,
    PartnerTrade,
    ShuffleVillager,
    Techsanity,
    Unitsanity,
)
from ..regions.UnitRegions import UnitEntranceKind

ALLOWLIST = pathlib.Path(__file__).with_name("never_bare_allowlist.txt")

QUESTIONS = {
    question.__name__: (question, subject)
    for question, subject in (
        (ScenarioCanBuild, "building"),
        (ScenarioCanResearch, "tech"),
        (ScenarioCanTrain, "unit"),
        (ScenarioHasReached, "age"),
        (ScenarioHasEasyResource, "resource"),
        (ScenarioHasSomeResource, "resource"),
    )
}
RESOURCE_QUESTIONS = {ScenarioHasEasyResource.__name__, ScenarioHasSomeResource.__name__}
STANDING_OR_BUILDABLE = ", standing or buildable"
SEED_ITEMS = {
    item.item_name: item.type.type
    for item in Age2ItemData
    if isinstance(item.type, SeedResources)
}

CAMPAIGNS = {campaign.campaign_name for campaign in Age2CampaignData}
MAXIMAL = {
    "enabled_campaigns": CAMPAIGNS,
    "starting_campaigns": CAMPAIGNS,
    "techsanity": Techsanity.option_all,
    "unitsanity": Unitsanity.option_all,
    "shuffle_villager": ShuffleVillager.option_include_professions,
    "include_unique_units": IncludeUniqueUnits.option_both,
    "shuffle_buildings": {
        BuildingOption.base,
        BuildingOption.economy,
        BuildingOption.tech,
        BuildingOption.military,
        BuildingOption.castle,
        BuildingOption.defense,
        BuildingOption.unique,
        BuildingOption.wonder,
    },
    "partner_trade": PartnerTrade.option_allies_and_enemies,
    "market_trade": True,
}
EXISTING_TECHS = (ExistingTechs.option_vanilla, ExistingTechs.option_start_in_dark_age)

type Spot = Location | Entrance

class BareAsks:

    def __init__(self, subjects: dict[str, tuple[str, object]]) -> None:
        self.subjects = subjects
        self.bare_asks_by_rule: dict[tuple[int, frozenset[Resource]], frozenset[str]] = {}
        self.economies: dict[int, EconomyRoutes.Resolved] = {}

    def asks(self, rule: Rule.Resolved) -> tuple[str, object]:
        if not isinstance(rule, ScenarioQuestion.Resolved) or rule.description not in self.subjects:
            return "", None
        return self.subjects[rule.description]

    def cost(self, rule: Rule.Resolved) -> frozenset[Resource] | None:
        question, subject = self.asks(rule)
        if question in QUESTIONS and question not in RESOURCE_QUESTIONS:
            return frozenset(
                resource for resource, amount in subject.cost.items()
                    if amount > 0
            )
        if isinstance(rule, Named.Resolved) and rule.label.endswith(STANDING_OR_BUILDABLE):
            buildable = self.buildable_in(rule.child)
            if buildable is None:
                return frozenset()
            return self.cost(buildable)
        return None

    def buildable_in(self, rule: Rule.Resolved) -> Rule.Resolved | None:
        if self.asks(rule)[0] == ScenarioCanBuild.__name__:
            return rule
        if isinstance(rule, Or.Resolved):
            for child in rule.children:
                found = self.buildable_in(child)
                if found is not None:
                    return found
        return None

    def pays_for(self, rule: Rule.Resolved) -> frozenset[Resource]:
        question, subject = self.asks(rule)
        if question in RESOURCE_QUESTIONS:
            return frozenset({subject})
        if isinstance(rule, HasResourceAmount.Resolved):
            return frozenset({rule.resource})
        if isinstance(rule, EconomyRouteRunning.Resolved):
            return frozenset(rule.route.yields)
        if isinstance(rule, Has.Resolved):
            return self.paid_by_seed_items([rule.item_name])
        if isinstance(rule, HasAll.Resolved):
            return self.paid_by_seed_items(rule.item_names)
        if isinstance(rule, HasAllCounts.Resolved):
            return self.paid_by_seed_items([name for name, _ in rule.item_counts])
        if isinstance(rule, Or.Resolved):
            return frozenset.intersection(*[self.pays_for(child) for child in rule.children])
        return frozenset()

    def paid_by_seed_items(self, item_names: Iterable[str]) -> frozenset[Resource]:
        return frozenset(
            SEED_ITEMS[name] for name in item_names
                if name in SEED_ITEMS
        )

    def bare_asks_under(self, rule: Rule.Resolved, paid: frozenset[Resource]) -> frozenset[str]:
        key = (id(rule), paid)
        if key not in self.bare_asks_by_rule:
            self.bare_asks_by_rule[key] = frozenset(self._bare_asks_under(rule, paid))
        return self.bare_asks_by_rule[key]

    def _bare_asks_under(self, rule: Rule.Resolved, paid: frozenset[Resource]) -> set[str]:
        if rule.always_true or rule.always_false:
            return set()
        cost = self.cost(rule)
        if cost is not None:
            unpaid = cost - paid
            if not unpaid:
                return set()
            named = ", ".join(sorted(resource.name.lower() for resource in unpaid))
            return {f"{rule.description} (unpaid: {named})"}
        if isinstance(rule, EconomyRoutes.Resolved):
            self.economies[id(rule)] = rule
            return set()
        if isinstance(rule, EconomyRouteRunning.Resolved):
            self.economies[id(rule.economy)] = rule.economy
            return set()
        if isinstance(rule, ScenarioQuestion.Resolved):
            return set(self.bare_asks_under(rule.answer, paid))
        if isinstance(rule, And.Resolved):
            paid = paid.union(*[self.pays_for(child) for child in rule.children])
        if isinstance(rule, NestedRule.Resolved):
            return {
                found for child in rule.children
                    for found in self.bare_asks_under(child, paid)
            }
        if isinstance(rule, WrapperRule.Resolved):
            return set(self.bare_asks_under(rule.child, paid))
        return set()

    def bare_asks_in_economies(self) -> set[str]:
        found: set[str] = set()
        done: set[int] = set()
        while len(done) < len(self.economies):
            for key, economy in list(self.economies.items()):
                if key in done:
                    continue
                done.add(key)
                for route in economy.routes:
                    for description in self.bare_asks_under(route.leaf, frozenset(route.needs)):
                        found.add(f"{economy.label} runs {route.name}: {description}")
        return found

@functools.cache
def maximal_world(existing_techs: int) -> Age2World:
    world = setup_solo_multiworld(Age2World, ()).worlds[1]
    for name, value in {**MAXIMAL, "existing_techs": existing_techs}.items():
        getattr(world.options, name).value = value
    for step in ("generate_early", "create_regions", "create_items", "set_rules"):
        getattr(world, step)()
    return world

def bare_asks(world: Age2World) -> set[str]:
    walk = BareAsks(subjects(world.rules.logic))
    found: set[str] = set()
    for spot in spots_with_rules(world):
        found.update(
            f"{spot.name}: {description}"
            for description in walk.bare_asks_under(spot.access_rule, frozenset())
        )
    return found | walk.bare_asks_in_economies()

def subjects(logic: Logic) -> dict[str, tuple[str, object]]:
    found: dict[str, tuple[str, object]] = {}
    for name, scenario, *asked in logic.scenario_answers:
        if name not in QUESTIONS:
            continue
        question, subject = QUESTIONS[name]
        description = question(scenario=scenario, **{subject: asked[0]}).describe(scenario)
        found[description] = (name, asked[0])
    return found

def spots_with_rules(world: Age2World) -> list[Spot]:
    doors = paid_where_they_lead(world)
    every = [
        *world.multiworld.get_locations(world.player),
        *world.multiworld.get_entrances(world.player),
    ]
    return [
        spot for spot in every
            if spot.name not in doors and isinstance(spot.access_rule, Rule.Resolved)
    ]

def paid_where_they_lead(world: Age2World) -> set[str]:
    tech_doors = {door.name for door in world.get_region("Can Build").exits}
    unit_doors = {
        entrance.name for region in world.unit_regions.regions
            for entrance in region.entrances
            if entrance.kind == UnitEntranceKind.train
    }
    return tech_doors | unit_doors

def findings() -> set[str]:
    return set().union(*[
        bare_asks(maximal_world(existing_techs)) for existing_techs in EXISTING_TECHS
    ])

def allowlist() -> set[str]:
    return set(ALLOWLIST.read_text(encoding="utf-8").splitlines())

def unlisted_and_stale(allowed: set[str], found: set[str]) -> tuple[list[str], list[str]]:
    return sorted(found - allowed), sorted(allowed - found)

class TestNothingIsAskedBare(unittest.TestCase):

    maxDiff = None

    ATTILA_3_BUILD_CASTLE = "The Walls of Constantinople: Build a Castle"
    ATTILA_3_CASTLE = (
        f"{ATTILA_3_BUILD_CASTLE}: "
        "The Walls of Constantinople can build a Castle (unpaid: stone)"
    )

    def test_every_bare_ask_is_on_the_allowlist_and_every_entry_is_still_bare(self):
        unlisted, stale = unlisted_and_stale(allowlist(), findings())
        self.assertEqual(
            ([], []),
            (unlisted, stale),
            "The first list is structural questions asked with nothing paying for them: pay for "
            "each beside the question. The second is sites now paid for: delete them from "
            "never_bare_allowlist.txt.",
        )

    def test_a_bare_build_added_to_a_location_is_named(self):
        world = maximal_world(ExistingTechs.option_vanilla)
        location = world.get_location(Age2BuildingData.BARRACKS.location_name)
        scourge = world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        bare = scourge.buildings.can_build_structurally(Age2BuildingData.UNIVERSITY)
        added = f"{location.name}: The Scourge of God can build a University (unpaid: wood)"
        with self.rule_added(location, bare.resolve(world), world):
            unlisted, _ = unlisted_and_stale(allowlist(), findings())
        self.assertEqual([added], unlisted)

    def test_a_still_bare_site_taken_off_the_allowlist_fails(self):
        unlisted, stale = unlisted_and_stale(
            allowlist() - {self.ATTILA_3_CASTLE},
            findings(),
        )
        self.assertEqual(([self.ATTILA_3_CASTLE], []), (unlisted, stale))

    def test_an_entry_whose_site_is_now_paid_fails(self):
        with contextlib.ExitStack() as paid:
            for existing_techs in EXISTING_TECHS:
                world = maximal_world(existing_techs)
                location = world.get_location(self.ATTILA_3_BUILD_CASTLE)
                walls = world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
                stone = walls.economy.has_easy_source(Resource.STONE)
                paid.enter_context(self.rule_added(location, stone.resolve(world), world))
            unlisted, stale = unlisted_and_stale(allowlist(), findings())
        self.assertEqual(([], [self.ATTILA_3_CASTLE]), (unlisted, stale))

    @staticmethod
    @contextlib.contextmanager
    def rule_added(location: Location, rule: Rule.Resolved, world: Age2World) -> Iterator[None]:
        original = location.access_rule
        location.access_rule = And.Resolved((original, rule), player=world.player)
        try:
            yield
        finally:
            location.access_rule = original

if __name__ == "__main__":
    unittest.main()
