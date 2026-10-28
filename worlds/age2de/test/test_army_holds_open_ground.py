"""Playtest #29: an army P1 can train holds open ground at scale, beside a built defence.

The toy scenario of `test_economy_catalog.py` with the defence layer left real, as
`test_defence_pays.py` leaves it: `_fortified` and the new `can_hold_open_ground` are what is
under test, so only the leaves beneath them are switched. `ARMY_LINES` is the land military this
toy can field, read exactly as the navy's lines are.
"""
import unittest

from . import bases
from ..Options import ExistingTechs, MarketTrade
from ..items.Items import Resource
from ..locations.Buildings import Age2BuildingData as B
from ..locations.connections.ScenarioResources import Tier
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData as Line
from ..locations.VillagerJobs import Age2VillagerJobData as Job
from .test_defence_pays import (
    BASE_TOWN_CENTER,
    CASTLE_ADVANCE_WORKERS,
    FARMERS,
    OPEN_GOLD_MAP,
    STONE_OF_SOME,
    DefenceToyBase,
)
from .test_economy_catalog import (
    BASE,
    BASE_SWITCHES,
    FISHING_SHIPS,
    MARKET_SEED,
    SCENARIO_WOOD,
    VILLAGERS,
    army,
    building,
    granted,
    job,
    navy,
    standing,
    tier,
)

SCOUTS = Line.SCOUT_CAVALRY_LINE
"""Food alone: the cheapest army this toy can keep in the field."""
FOOTMEN = Line.MILITIA_LINE
"""Food and gold."""
ARCHERS = Line.ARCHER_LINE

SOME_FOOD = (VILLAGERS, job(Job.HUNTER_MALE))
"""Hunters dropping at the base's Town Center. No camp, so what they bring in is *some* food."""
A_LITTLE_HUNT = tier(hunt_count=600)
"""Under `DEMAND.food`, so the food route of *some* it feeds never becomes an easy source and
the army's wage is the only thing it pays."""
TRAINING_GROUNDS = (standing(B.BARRACKS), standing(B.ARCHERY_RANGE), standing(B.STABLE))


class ArmyToyBase(DefenceToyBase):
    ARMY_LINES = {
        SCOUTS: {Resource.FOOD},
        FOOTMEN: {Resource.FOOD, Resource.GOLD},
        ARCHERS: {Resource.WOOD, Resource.GOLD},
    }


class TestAnArmyHoldsOpenGround(ArmyToyBase):
    """The land sibling of the naval guard: soldiers P1 can train stand on the ground a route
    works at scale, where #23 asked for a wall, a tower or a strongpoint."""

    MAP = {Tier.OPEN: tier(gold_count=2000), Tier.BASE: A_LITTLE_HUNT}
    MINERS = (*TRAINING_GROUNDS, *BASE_SWITCHES, VILLAGERS, job(Job.GOLD_MINER_MALE),
              standing(B.MINING_CAMP), *SOME_FOOD)

    def test_open_gold_at_scale_holds_on_the_army_with_nothing_built(self):
        self.toy(self.MAP)
        self.assertFalse(self.easy(Resource.GOLD, self.state(*self.MINERS)))
        self.assertTrue(self.easy(Resource.GOLD, self.state(*self.MINERS, army(SCOUTS))))

    def test_an_army_it_cannot_pay_for_holds_nothing(self):
        self.toy({Tier.OPEN: tier(gold_count=2000)})
        no_wood = (*TRAINING_GROUNDS, *BASE_SWITCHES, VILLAGERS, job(Job.GOLD_MINER_MALE),
                   standing(B.MINING_CAMP))
        self.assertTrue(self.some(Resource.GOLD, self.state(*no_wood)))
        self.assertFalse(self.easy(Resource.GOLD, self.state(*no_wood, army(ARCHERS))))
        self.assertTrue(self.easy(Resource.GOLD, self.state(*no_wood, army(SCOUTS))))


class TestTheArmyHoldsEveryResourceOutThere(ArmyToyBase):
    """The army opens the gate, not a resource, and the gates take no parameter - so one army
    holds the stone it costs nothing of as well as the gold it is paid in."""

    MAP = {Tier.OPEN: tier(gold_count=2000, stone_count=2000), Tier.BASE: A_LITTLE_HUNT}
    MINERS = (*TRAINING_GROUNDS, *BASE_SWITCHES, VILLAGERS, job(Job.GOLD_MINER_MALE),
              job(Job.STONE_MINER_MALE), standing(B.MINING_CAMP), *SOME_FOOD)

    def test_one_army_opens_the_stone_as_well_as_the_gold(self):
        self.toy(self.MAP)
        self.assertFalse(self.easy(Resource.STONE, self.state(*self.MINERS)))
        held = self.state(*self.MINERS, army(SCOUTS))
        self.assertTrue(self.easy(Resource.GOLD, held))
        self.assertTrue(self.easy(Resource.STONE, held))


class TestTheArmyPaysPerLine(ArmyToyBase):
    """A defence pays for itself out of *some* of its own cost, and the line it fields is what
    sets that cost - the same ruling `TestTheNavyPaysPerLine` holds the warships to."""

    MAP = {Tier.OPEN: tier(stone_count=2000), Tier.BASE: A_LITTLE_HUNT}
    QUARRY = (*TRAINING_GROUNDS, *BASE_SWITCHES, VILLAGERS, job(Job.STONE_MINER_MALE),
              standing(B.MINING_CAMP), *SOME_FOOD)

    def test_a_line_costing_food_and_gold_asks_for_both(self):
        self.toy(self.MAP)
        fed_only = self.state(*self.QUARRY, army(FOOTMEN))
        self.assertFalse(self.easy(Resource.STONE, fed_only))

    def test_a_line_costing_only_food_is_not_taxed_for_gold(self):
        self.toy(self.MAP)
        fed_only = self.state(*self.QUARRY, army(SCOUTS))
        self.assertTrue(self.easy(Resource.STONE, fed_only))

    def test_the_dearer_line_holds_once_its_gold_is_in(self):
        self.toy({Tier.OPEN: tier(stone_count=2000),
                  Tier.BASE: tier(hunt_count=600, gold_count=100)})
        with_gold = self.state(*self.QUARRY, job(Job.GOLD_MINER_MALE), army(FOOTMEN))
        self.assertTrue(self.easy(Resource.STONE, with_gold))

    def test_a_bank_never_pays_the_army(self):
        self.toy(self.MAP)
        banked = self.state(*self.QUARRY, army(FOOTMEN), gold=250)
        self.assertFalse(self.easy(Resource.STONE, banked))


class TestAGrantedArmyHoldsNothing(ArmyToyBase):
    """`can_field_structurally` asks what P1 can train and never `obtains_unit`. Soldiers the
    scenario hands over are its own plan, not a garrison."""

    MAP = {Tier.OPEN: tier(gold_count=2000), Tier.BASE: A_LITTLE_HUNT}
    MINERS = (*TRAINING_GROUNDS, *BASE_SWITCHES, VILLAGERS, job(Job.GOLD_MINER_MALE),
              standing(B.MINING_CAMP), *SOME_FOOD)
    HANDED_OVER = tuple(granted(soldier) for line in (SCOUTS, FOOTMEN) for soldier in line.units)
    """Every tier of both lines, standing there and P1's - and none of them trained."""

    def test_an_army_handed_over_opens_no_ground(self):
        self.toy(self.MAP)
        self.assertFalse(self.easy(Resource.GOLD, self.state(*self.MINERS, *self.HANDED_OVER)))

    def test_the_same_lines_trained_do(self):
        self.toy(self.MAP)
        self.assertTrue(self.easy(Resource.GOLD, self.state(*self.MINERS, army(SCOUTS))))


class TestTheBaseIsStillAsked(ArmyToyBase):
    """The army is a rule the gate holds on. It does not excuse the villager routes from their
    own economy seed."""

    MAP = {Tier.OPEN: tier(gold_count=2000), Tier.BASE: A_LITTLE_HUNT}

    def test_an_army_does_not_stand_in_for_the_base(self):
        self.toy(self.MAP)
        baseless = (*TRAINING_GROUNDS, building(B.TOWN_CENTER), VILLAGERS, job(Job.GOLD_MINER_MALE),
                    standing(B.MINING_CAMP), *SOME_FOOD, army(SCOUTS))
        self.assertNotIn(BASE, baseless)
        self.assertFalse(self.easy(Resource.GOLD, self.state(*baseless)))
        self.assertTrue(self.some(Resource.GOLD, self.state(*baseless)))


class TestTheShorelineTakesNoArmy(ArmyToyBase):
    """Open ground only. A shoreline is held by a building or by the navy, as before #29."""

    MAP = {Tier.OPEN: tier(shore_fish_count=2000), Tier.BASE: A_LITTLE_HUNT}
    FISHERMEN = (*TRAINING_GROUNDS, *BASE_SWITCHES, VILLAGERS, job(Job.FISHERMAN_MALE),
                 building(B.MILL), *SOME_FOOD)

    def test_soldiers_on_the_beach_hold_nothing(self):
        self.toy(self.MAP)
        self.assertFalse(self.easy(Resource.FOOD, self.state(*self.FISHERMEN, army(SCOUTS))))

    def test_a_dock_the_same_map_can_pay_for_does(self):
        self.toy(self.MAP)
        with_a_dock = self.state(*self.FISHERMEN, army(SCOUTS),
                                 job(Job.LUMBERJACK_MALE), building(B.DOCK))
        self.assertTrue(self.easy(Resource.FOOD, with_a_dock))


class TestTheAfloatGateIgnoresALandArmy(ArmyToyBase):
    """Deep water is the navy's, and no soldier walks out onto it."""

    NAVY_LINES = {Line.FIRE_GALLEY_LINE: {Resource.WOOD}}
    """Wood alone, so this map needs no gold to put warships out."""
    WARSHIPS = navy(Line.FIRE_GALLEY_LINE)
    MAP = {Tier.OPEN: tier(deep_fish_count=2000), Tier.BASE: A_LITTLE_HUNT}
    BOATS = (*TRAINING_GROUNDS, *BASE_SWITCHES, *FISHING_SHIPS, SCENARIO_WOOD, *SOME_FOOD)

    def test_an_army_does_not_escort_the_fishing_ships(self):
        self.toy(self.MAP)
        self.assertFalse(self.easy(Resource.FOOD, self.state(*self.BOATS, army(SCOUTS))))

    def test_warships_do(self):
        self.toy(self.MAP)
        self.assertTrue(self.easy(Resource.FOOD, self.state(*self.BOATS, self.WARSHIPS)))


class TestACastleAgeArmyPaysItsAdvanceAndItsCastle(ArmyToyBase):
    ARMY_LINES = {Line.TARKAN_LINE: {Resource.FOOD, Resource.GOLD}}
    TARKANS = army(Line.TARKAN_LINE)
    EASY_STONE = (SCENARIO_WOOD, building(B.MARKET), MARKET_SEED)
    PAID = (
        *CASTLE_ADVANCE_WORKERS,
        *FARMERS,
        *EASY_STONE,
        building(B.CASTLE),
        TARKANS,
    )

    def holds(self, *switches: str) -> bool:
        self.toy(
            OPEN_GOLD_MAP,
            existing_techs=ExistingTechs.option_start_in_dark_age,
            market_trade=MarketTrade.option_true,
        )
        held = self.scenario.military.can_hold_open_ground().resolve(self.world)
        return bool(held(self.state(*switches)))

    def test_with_the_town_center_and_easy_stone_the_army_holds(self):
        self.assertTrue(self.holds(*self.PAID))

    def test_without_the_paid_town_center_it_does_not(self):
        self.assertFalse(self.holds(*[name for name in self.PAID if name not in BASE_TOWN_CENTER]))

    def test_some_stone_does_not_pay_for_its_castle(self):
        some_stone = [name for name in self.PAID if name not in self.EASY_STONE]
        self.assertIn(STONE_OF_SOME, some_stone)
        self.assertFalse(self.holds(*some_stone))


class TestExplainShowsTheArmyBesideTheBuildings(bases.Age2RuleTestBase):
    """The gate reads as two rules, each its own line: what P1 builds, and what P1 trains."""

    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]
    SCENARIO = Age2ScenarioData.AP_ATTILA_1

    def test_can_defend_resources_opens_to_a_built_defence_and_an_army(self):
        self.build()
        asked = str(self.world.rules.logic.for_scenario(self.SCENARIO).economy
                    .can_defend_resources())
        name = self.SCENARIO.scenario_name
        self.assertIn(f"{name} can defend resources", asked)
        self.assertIn(f"{name} has a built defence", asked)
        self.assertIn(f"{name} can hold open ground with an army", asked)


if __name__ == "__main__":
    unittest.main()
