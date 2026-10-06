import collections

from BaseClasses import CollectionState, ItemClassification

from ..Options import ExistingTechs, Techsanity, Unitsanity
from ..items import Items
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.Civilizations import Age2CivData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..locations.connections.CivilizationTechs import CIV_TO_TECHS
from .bases import Age2RuleTestBase


MILL_CHAIN = (Age2TechData.CROP_ROTATION, Age2TechData.HEAVY_PLOW, Age2TechData.HORSE_COLLAR)


class TestTechItemsDoNotGate(Age2RuleTestBase):
    """A shuffled technology is always researchable; its item only applies the effect. So no
    technology location asks for a technology item - not its own, and nothing below it."""

    def test_a_chain_asks_for_none_of_its_links(self):
        self.build(techsanity=Techsanity.option_generic)
        wanted = self.item_requirements(Age2TechData.CROP_ROTATION.location_name)
        for tech in MILL_CHAIN:
            self.assertNotIn(tech.item.item_name, wanted, tech.name)

    def test_no_technology_in_the_pool_asks_for_its_own_chain(self):
        # Only the technology's own item and the chain below it. A technology also has to be
        # afforded, and the economy reaches units, which do ask for their upgrade items - so the
        # wider "no technology item anywhere" is not the claim being made here.
        world = self.build(techsanity=Techsanity.option_all)
        for tech in world.pool.techs.shuffled:
            with self.subTest(tech=tech.name):
                wanted = self.item_requirements(tech.location_name)
                link = tech
                while link is not None:
                    self.assertNotIn(link.item.item_name, wanted, link.name)
                    link = link.prerequisite

    def test_the_age_is_still_asked_for(self):
        # The item unlocks the effect, not the age. Crop Rotation is Imperial either way.
        self.build(techsanity=Techsanity.option_generic)
        starved = self.state_without(*self.imperial_blockers())
        self.assertFalse(starved.can_reach_location(
            Age2TechData.CROP_ROTATION.location_name, self.world.player))

    def imperial_blockers(self) -> list[str]:
        return [building.item.item_name for building in
                (Age2BuildingData.MONASTERY, Age2BuildingData.UNIVERSITY,
                 Age2BuildingData.SIEGE_WORKSHOP, Age2BuildingData.CASTLE)]


class TestPrerequisitesAddNothing(Age2RuleTestBase):
    """available() does not walk the prerequisite chain. That is only safe while every
    prerequisite is researched somewhere its dependent already needs, in an age its dependent has
    already reached -- which shipped data satisfies for all 49 chains. If it ever stops, the walk
    has to come back, so this is the tripwire rather than a test of behaviour."""

    def test_a_prerequisite_never_reaches_past_its_dependent(self):
        for tech in Age2TechData:
            prerequisite = tech.prerequisite
            if prerequisite is None:
                continue
            with self.subTest(tech=tech.name, prerequisite=prerequisite.name):
                self.assertFalse(set(prerequisite.buildings) - set(tech.buildings),
                                 "prerequisite researches somewhere its dependent does not")
                self.assertLessEqual(prerequisite.age, tech.age,
                                     "prerequisite sits in a later age than its dependent")


class TestUpgradesWaitOnTheirItem(Age2RuleTestBase):
    """The mod applies an upgrade's effect only once its item arrives, whatever else is true, so
    researching the technology is not enough to be holding the upgraded unit."""

    def test_an_upgrade_asks_for_its_technology_item(self):
        world = self.build(techsanity=Techsanity.option_units,
                           existing_techs=ExistingTechs.option_start_in_dark_age)
        checked = 0
        for unit in Age2UnitData:
            tech = unit.upgrade_tech
            if tech is None or not world.pool.techs.includes(tech):
                continue
            for scenario in world.rules.logic.scenarios:
                rule = scenario.units.has_upgrade_tech(unit).resolve(world)
                if rule.always_true or rule.always_false:
                    continue
                self.assertIn(tech.item.item_name, set(rule.item_dependencies()), unit.name)
                checked += 1
        self.assertTrue(checked, "no scenario asked for an upgrade at all")

    def test_a_technology_the_scenario_researched_itself_asks_for_nothing(self):
        # Under Vanilla a scenario auto-researches everything below the age it opens in, so the
        # tier is already upgraded there and the item has no part in it. Asking for it anyway
        # would price a unit the player was handed.
        world = self.build(techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_vanilla)
        checked = 0
        for unit in Age2UnitData:
            tech = unit.upgrade_tech
            if tech is None or not world.pool.techs.includes(tech):
                continue
            if world.pool.techs.locked_at_start(tech):
                continue
            for scenario in world.rules.logic.scenarios:
                if tech.age >= scenario.scenario.vanilla_age:
                    continue
                rule = scenario.units.has_upgrade_tech(unit).resolve(world)
                self.assertTrue(rule.always_true, f"{unit.name} in {scenario.scenario.name}")
                checked += 1
        self.assertTrue(checked, "no auto-researched upgrade found to test")


class TestTechnologyClassification(Age2RuleTestBase):
    """A technology item is progression only where a rule leans on it. Since a technology is
    always researchable and its item only applies the effect, the one rule that names a technology
    item is the unit upgrade path - so progression means upgrade, and nothing else. The flag is
    declared on Tech rather than derived, because classification is fixed in create_items while
    the rules are not built until set_rules, so this is what keeps the two honest."""

    UNITSANITY = (Unitsanity.option_none, Unitsanity.option_unit_line, Unitsanity.option_all)

    def named_by_rules(self, world) -> set[str]:
        named: set[str] = set()
        for scenario in world.rules.logic.scenarios:
            for unit in Age2UnitData:
                tech = unit.upgrade_tech
                if tech is None or not world.pool.techs.includes(tech):
                    continue
                rule = scenario.units.has_upgrade_tech(unit).resolve(world)
                named |= set(rule.item_dependencies())
        return named

    def closes_a_location(self, world) -> dict[str, int]:
        """How many locations shut when one copy of each technology item is taken away."""
        locations = [loc for loc in self.multiworld.get_locations(world.player)
                     if loc.item is None]
        pool, by_name = collections.Counter(), {}
        for item in self.multiworld.itempool:
            if item.player == world.player and item.advancement:
                pool[item.name] += 1
                by_name.setdefault(item.name, []).append(item)

        def reach(held):
            state = CollectionState(self.multiworld)
            for name, count in held.items():
                for item in by_name[name][:count]:
                    state.collect(item, prevent_sweep=True)
            state.sweep_for_advancements()
            return {loc.name for loc in locations if loc.can_reach(state)}

        everything = reach(pool)
        shut = {}
        for name in pool:
            data = Items.NAME_TO_ITEM.get(name)
            if data is None or not isinstance(data.type, Items.Tech):
                continue
            trimmed = collections.Counter(pool)
            trimmed[name] -= 1
            shut[name] = len(everything - reach(trimmed))
        return shut

    def test_a_technology_a_rule_needs_is_never_merely_useful(self):
        for unitsanity in self.UNITSANITY:
            with self.subTest(unitsanity=unitsanity):
                world = self.build(techsanity=Techsanity.option_all, unitsanity=unitsanity)
                named = self.named_by_rules(world)
                wanted = [tech for tech in world.pool.techs.shuffled
                          if tech.item.item_name in named]
                self.assertTrue(wanted, "no technology was named by a rule at all")
                for tech in wanted:
                    self.assertEqual(ItemClassification.progression,
                                     Items.classification_for(tech.item), tech.name)

    def test_only_an_upgrade_is_ever_progression(self):
        for unitsanity in self.UNITSANITY:
            with self.subTest(unitsanity=unitsanity):
                world = self.build(techsanity=Techsanity.option_all, unitsanity=unitsanity)
                for tech in world.pool.techs.shuffled:
                    if Items.classification_for(tech.item) != ItemClassification.progression:
                        continue
                    self.assertTrue(tech.item.type.is_upgrade, tech.name)

    def test_per_tier_locations_only_ever_add_to_what_an_upgrade_gates(self):
        """The uncomfortable corner, pinned rather than fixed.

        Under Unitsanity All a location exists per tier, so an upgrade item is the key to its own
        tier. Below that a line is owned through its base tier, so most upgrade items gate nothing
        at all - yet they stay progression, because has_upgrade_tech legitimately asks for them
        and a useful item never enters the collection state. Demoting one would make that rule
        unsatisfiable and could strand a victory behind an upgraded unit.

        So a number of progression technologies are inert in the narrower modes. That is a
        deliberate trade. What has to hold is the direction: splitting locations per tier can only
        give an upgrade item more to gate, never less.
        """
        gating = {}
        for unitsanity in self.UNITSANITY:
            world = self.build(techsanity=Techsanity.option_all, unitsanity=unitsanity)
            shut = self.closes_a_location(world)
            gating[unitsanity] = {name for name, count in shut.items() if count > 0}

        widest = gating[Unitsanity.option_all]
        self.assertTrue(widest, "per-tier locations, so an upgrade should be the key to one")
        for unitsanity in (Unitsanity.option_none, Unitsanity.option_unit_line):
            with self.subTest(unitsanity=unitsanity):
                self.assertLessEqual(gating[unitsanity], widest,
                                     "an upgrade gates something here that it does not gate once "
                                     "locations are split per tier, which should be impossible")


class TestAgeGate(Age2RuleTestBase):
    def test_two_technologies_in_one_region_can_disagree(self):
        # Both live in the Mill. If the age ever migrates from the location to
        # the region entrance, these two stop being separable and this fails.
        self.build(techsanity=Techsanity.option_generic)
        starved = self.state_without(
            *[building.item.item_name for building in
              (Age2BuildingData.MONASTERY, Age2BuildingData.UNIVERSITY,
               Age2BuildingData.SIEGE_WORKSHOP, Age2BuildingData.CASTLE)])
        self.assertTrue(starved.can_reach_location(
            Age2TechData.HORSE_COLLAR.location_name, self.world.player))
        self.assertFalse(starved.can_reach_location(
            Age2TechData.CROP_ROTATION.location_name, self.world.player))


class TestExistingTechs(Age2RuleTestBase):
    def test_a_scenario_that_was_handed_a_technology_cannot_check_it(self):
        # Under Vanilla a scenario auto-researches everything below the age it
        # opens in, and those locations never send a check. Only the scenarios
        # standing in the age itself count.
        world = self.build(techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_vanilla)
        scenarios = [scenario for campaign in world.pool.campaigns.enabled
                     for scenario in CAMPAIGN_TO_SCENARIOS[campaign]]
        for tech in world.pool.techs.shuffled:
            with self.subTest(tech=tech.name):
                rule = world.rules.logic.can_research_anywhere(tech).resolve(world)
                self.assertFalse(rule.always_false)
        # every technology has at least one scenario that opens at or below it
        for tech in world.pool.techs.shuffled:
            self.assertTrue([s for s in scenarios if s.vanilla_age <= tech.age], tech.name)

    def test_find_items_hands_every_technology_back(self):
        # Withheld everywhere, so a scenario that opens above the age can still
        # research it -- for free, but it still sends the check.
        world = self.build(techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_find_items)
        for tech in world.pool.techs.shuffled:
            self.assertTrue(world.pool.techs.locked_at_start(tech), tech.name)


class TestReplacementBuildingReachesSharedTechs(Age2RuleTestBase):
    """A civilization that puts up a Settlement instead of a Mill still
    researches the Mill technologies. The location cannot move or be duplicated,
    so the Mill region earns a second, free entrance instead."""

    def setUp(self):
        was = Age2CivData.FRANKS.included_buildings
        Age2CivData.FRANKS.included_buildings = was + [Age2BuildingData.SETTLEMENT]
        self.addCleanup(setattr, Age2CivData.FRANKS, "included_buildings", was)

    def build_with_uniques(self):
        return self.build(techsanity=Techsanity.option_generic,
                          shuffle_buildings={"Economy", "Tech", "Military", "Unique"})

    def test_either_building_reaches_the_shared_technology(self):
        self.build_with_uniques()
        mill = Age2ItemData.MILL.item_name
        settlement = Age2ItemData.SETTLEMENT.item_name
        location = Age2TechData.HORSE_COLLAR.location_name
        self.assertTrue(self.can_reach(location, self.state_without(settlement)))
        self.assertTrue(self.can_reach(location, self.state_without(mill)))
        self.assertFalse(self.can_reach(location, self.state_without(mill, settlement)))

    def test_the_cross_entrance_carries_no_rule_of_its_own(self):
        # A rule here would double gate: the replacement's own door already
        # asked whether the player can build it.
        self.build_with_uniques()
        cross = self.multiworld.get_entrance("Settlement to Mill Techs", self.world.player)
        self.assertTrue(cross.access_rule(CollectionState(self.multiworld)))
