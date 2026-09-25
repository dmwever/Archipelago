from test.general import setup_multiworld

from rule_builder.rules import Rule

from .. import Age2World
from ..Options import ExistingTechs, Techsanity
from ..items.Items import Age2ItemData
from ..locations.Ages import SHUFFLED_AGES, Age2AgeData
from ..locations.Buildings import Age2BuildingData
from .bases import Age2RuleTestBase


AGE_ITEMS = [age.item.item_name for age in SHUFFLED_AGES]


class TestWhichAgesAreShuffled(Age2RuleTestBase):
    """An age every scenario opens at or above is handed over, never earned, so
    it is no more shuffleable than a technology below the earliest start."""

    def test_every_age_is_shuffled_when_a_scenario_opens_in_the_dark_age(self):
        world = self.build(shuffle_ages=True)
        self.assertEqual(world.earliest_age, Age2AgeData.DARK)
        self.assertEqual(list(world.shuffled_ages), list(SHUFFLED_AGES))

    def test_an_age_no_scenario_starts_below_is_not_shuffled(self):
        world = self.build(shuffle_ages=True, enabled_campaigns={"Joan of Arc"},
                           starting_campaigns={"Joan of Arc"})
        self.assertEqual(world.earliest_age, Age2AgeData.FEUDAL)
        self.assertNotIn(Age2AgeData.FEUDAL, world.shuffled_ages)
        self.assertIn(Age2AgeData.CASTLE, world.shuffled_ages)
        self.assertIn(Age2AgeData.IMPERIAL, world.shuffled_ages)

    def test_an_unshuffled_age_is_neither_an_item_nor_a_location(self):
        self.build(shuffle_ages=True, enabled_campaigns={"Joan of Arc"},
                   starting_campaigns={"Joan of Arc"})
        feudal = Age2AgeData.FEUDAL
        pooled = [item.name for item in self.multiworld.itempool]
        precollected = [item.name for item in
                        self.multiworld.precollected_items[self.world.player]]
        self.assertNotIn(feudal.item.item_name, pooled)
        self.assertIn(feudal.item.item_name, precollected)
        self.assertNotIn(feudal.location_name, self.location_names())

    def test_a_dark_age_rebase_makes_every_age_earnable_again(self):
        world = self.build(shuffle_ages=True, techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_start_in_dark_age,
                           enabled_campaigns={"Joan of Arc"},
                           starting_campaigns={"Joan of Arc"})
        self.assertEqual(list(world.shuffled_ages), list(SHUFFLED_AGES))
        self.assertIn(Age2AgeData.FEUDAL.location_name, self.location_names())


class TestShuffleAgesOff(Age2RuleTestBase):
    def test_the_age_items_are_handed_over_at_the_start(self):
        self.build(shuffle_ages=False)
        pooled = [item.name for item in self.multiworld.itempool]
        precollected = [item.name for item in
                        self.multiworld.precollected_items[self.world.player]]
        for name in AGE_ITEMS:
            with self.subTest(item=name):
                self.assertNotIn(name, pooled)
                self.assertIn(name, precollected)

    def test_no_age_location_exists(self):
        self.build(shuffle_ages=False)
        for age in SHUFFLED_AGES:
            self.assertNotIn(age.location_name, self.location_names(), age.name)


class TestShuffleAgesOn(Age2RuleTestBase):
    def test_each_age_item_is_in_the_pool_once(self):
        self.build(shuffle_ages=True)
        pooled = [item.name for item in self.multiworld.itempool]
        for name in AGE_ITEMS:
            self.assertEqual(pooled.count(name), 1, name)

    def test_the_age_locations_live_where_the_buildings_do(self):
        self.build(shuffle_ages=True)
        for age in SHUFFLED_AGES:
            with self.subTest(age=age.name):
                location = self.multiworld.get_location(age.location_name, self.world.player)
                self.assertEqual(location.parent_region.name, "Can Build")


class TestAgeRowsMatchTheOpeningAge(Age2RuleTestBase):
    """Every scenario writes its own age rows by hand and nothing checks them
    against the age the scenario actually opens in. This is that check."""

    def rows(self, world, scenario_logic):
        return {age: scenario_logic.ages.can_reach(age).resolve(world) for age in Age2AgeData}

    def test_a_scenario_is_in_the_age_it_opens_in_and_no_lower_one(self):
        world = self.build(shuffle_ages=True)
        for scenario_logic in world.rules.logic.scenarios:
            if scenario_logic.starting_state.fixed_force:
                continue
            opens_in = scenario_logic.scenario.vanilla_age
            for age, rule in self.rows(world, scenario_logic).items():
                with self.subTest(scenario=scenario_logic.scenario.name, age=age.name):
                    if age < opens_in:
                        self.assertTrue(rule.always_false, "below the opening age")
                    elif age == opens_in:
                        self.assertTrue(rule.always_true, "the opening age is free")

    def test_a_scenario_has_started_past_every_age_below_the_one_it_opens_in(self):
        world = self.build(shuffle_ages=True)
        for scenario_logic in world.rules.logic.scenarios:
            if scenario_logic.starting_state.fixed_force:
                continue
            opens_in = scenario_logic.scenario.vanilla_age
            for age in Age2AgeData:
                with self.subTest(scenario=scenario_logic.scenario.name, age=age.name):
                    rule = scenario_logic.ages.start_past(age).resolve(world)
                    self.assertEqual(rule.always_true, age < opens_in)

    def test_a_fixed_force_scenario_is_in_no_age_at_all(self):
        # Joan 1 and Joan 5 are set pieces fought with what they hand you. No
        # base means no age, not even the one they open in.
        world = self.build(shuffle_ages=True)
        fixed = [s for s in world.rules.logic.scenarios if s.starting_state.fixed_force]
        self.assertEqual(sorted(s.scenario.name for s in fixed),
                         ["AP_JOAN_1", "AP_JOAN_5"])
        for scenario_logic in fixed:
            for age in Age2AgeData:
                with self.subTest(scenario=scenario_logic.scenario.name, age=age.name):
                    self.assertTrue(scenario_logic.ages.can_reach(age).resolve(world).always_false)
                    self.assertTrue(scenario_logic.ages.start_past(age).resolve(world).always_false)

    def test_a_dark_age_rebase_puts_every_scenario_in_the_dark_age(self):
        world = self.build(shuffle_ages=True, techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_start_in_dark_age)
        for scenario_logic in world.rules.logic.scenarios:
            if scenario_logic.starting_state.fixed_force:
                continue
            with self.subTest(scenario=scenario_logic.scenario.name):
                dark = scenario_logic.ages.can_reach(Age2AgeData.DARK).resolve(world)
                self.assertTrue(dark.always_true)
                # and it has started past nothing, so every age above is earned
                past = scenario_logic.ages.start_past(Age2AgeData.DARK).resolve(world)
                self.assertTrue(past.always_false)


class TestBuildingInYourOpeningAge(Age2RuleTestBase):
    def test_a_scenario_owes_nothing_for_the_age_it_opens_in(self):
        # A global age term would apply to every scenario at once, so a Castle
        # start would be charged for the Castle Age it was handed.
        self.build(shuffle_ages=True)
        without_feudal = self.state_without(Age2AgeData.FEUDAL.item.item_name)
        self.assertTrue(without_feudal.can_reach_location(
            Age2BuildingData.MARKET.location_name, self.world.player))


class TestAgeRowsStayOutOfTheAggregateLayer(Age2RuleTestBase):
    """An age row may ask AgeLogic and BuildingLogic, never Logic. The aggregate
    adds the age and villager terms, so a row that reaches it closes a loop:
    the Dark Age term asks a scenario, which asks for a base, which asks for a
    House, which asks the Dark Age term."""

    def children(self, rule):
        found = list(getattr(rule, "children", ()) or [])
        child = getattr(rule, "child", None)
        if isinstance(child, Rule):
            found.append(child)
        return found

    def reaches(self, rule, targets, seen):
        if id(rule) in seen:
            return False
        seen.add(id(rule))
        if id(rule) in targets:
            return True
        return any(self.reaches(child, targets, seen) for child in self.children(rule))

    def test_no_age_row_reaches_the_shared_age_rules(self):
        world = self.build(shuffle_ages=True)
        shells = {id(rule) for rule in world.rules.logic.ages.can_reach_age.values()}
        for scenario_logic in world.rules.logic.scenarios:
            for age in Age2AgeData:
                with self.subTest(scenario=scenario_logic.scenario.name, age=age.name):
                    row = scenario_logic.ages.can_reach(age)
                    self.assertFalse(self.reaches(row, shells, set()))


class TestAttila1(Age2RuleTestBase):
    def test_a_base_can_be_built_without_bledas_camp(self):
        # The alternate start -- Attila's Camp or the Roman villagers, then
        # build -- was dead for a while: it was asked for while the scenario
        # list was still being filled, so it resolved to nothing and was
        # dropped from the disjunction.
        world = self.build()
        attila_1 = [s for s in world.rules.logic.scenarios
                    if s.scenario.name == "AP_ATTILA_1"][0]
        wanted = set(attila_1.has_base().resolve(world).item_dependencies())
        self.assertIn(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name, wanted)
        self.assertIn(Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name, wanted)
        self.assertIn(Age2ItemData.TOWN_CENTER.item_name, wanted)


class TestMultipleSlots(Age2RuleTestBase):
    def test_a_second_slot_does_not_inherit_the_first_one_s_scenarios(self):
        # Logic.scenarios was a class attribute once, so it accumulated every
        # scenario from every world built in the process. Slot 1 shuffles no
        # buildings, which makes its building rules collapse to nothing -- the
        # shape that, leaked, hands slot 2 free buildings.
        pair = setup_multiworld([Age2World, Age2World], steps=("generate_early",), options=[
            {"enabled_campaigns": {"Attila the Hun"}, "starting_campaigns": {"Attila the Hun"},
             "shuffle_buildings": set(), "techsanity": Techsanity.option_all},
            {"enabled_campaigns": {"Joan of Arc"}, "starting_campaigns": {"Joan of Arc"},
             "techsanity": Techsanity.option_all},
        ])
        for world in pair.worlds.values():
            for step in ("create_regions", "create_items", "set_rules"):
                getattr(world, step)()
        second = pair.worlds[2]
        self.assertEqual(len(second.rules.logic.scenarios), 6)

        solo = setup_multiworld(Age2World, steps=("generate_early",), options={
            "enabled_campaigns": {"Joan of Arc"}, "starting_campaigns": {"Joan of Arc"},
            "techsanity": Techsanity.option_all})
        alone = solo.worlds[1]
        for step in ("create_regions", "create_items", "set_rules"):
            getattr(alone, step)()
        self.assertEqual(
            set(second.get_entrance("Mill").access_rule.item_dependencies()),
            set(alone.get_entrance("Mill").access_rule.item_dependencies()))
