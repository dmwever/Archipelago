import ast
from pathlib import Path
from unittest import mock

from rule_builder.rules import False_, True_

from ..Options import IncludeUniqueUnits, Unitsanity
from ..locations.Ages import Age2AgeData
from ..locations.Civilizations import Age2CivData
from ..locations.Locations import Age2ScenarioLocationData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS
from ..locations.connections.UnitRoles import ROLE_TO_LINES, SHIP_LINES, SIEGE_TARGETS, UnitRole
from ..logic.scenarios.ScenarioUnitLogic import ScenarioUnitLogic
from .bases import Age2RuleTestBase

EVERYTHING = dict(unitsanity=Unitsanity.option_all,
                  include_unique_units=IncludeUniqueUnits.option_both)


class TestUnitAgeGate(Age2RuleTestBase):
    """A unit is held to its own age, not to the age of the building that trains it.

    A Siege Workshop goes up in Feudal and the Bombard Cannon it turns out is Imperial. Nothing
    else was asking: a tier at the head of its line has no upgrade technology to carry the age
    for it, which left fourteen units trainable below their age.
    """

    def starved_of_imperial(self):
        self.build(shuffle_ages=True, **EVERYTHING)
        return self.state_without(Age2AgeData.IMPERIAL.item.item_name)

    def test_an_imperial_unit_needs_the_imperial_age(self):
        state = self.starved_of_imperial()
        # Neither is granted by any scenario, so training is the only way to own one.
        for unit in (Age2UnitData.CANNON_GALLEON, Age2UnitData.HEAVY_MOUNTED_CROSSBOWMAN):
            self.assertFalse(self.can_reach(unit.location_name, state), unit.unit_name)

    def test_the_tier_below_is_still_reachable(self):
        """The gate is the unit's age and nothing wider - the Castle tier is untouched."""
        state = self.starved_of_imperial()
        self.assertTrue(self.can_reach(
            Age2UnitData.MOUNTED_CROSSBOWMAN.location_name, state))


class TestNavalBombardment(Age2RuleTestBase):

    def test_the_huns_answer_with_the_dromon(self):
        """The Huns have no Cannon Galleon, so naming one would strand Attila 6.

        Their only ship that shoots buildings is the Dromon. This is the reason the role is a
        set of lines and not a named unit.
        """
        huns = CIV_TO_UNITS[Age2CivData.HUNS]
        self.assertNotIn(Age2UnitData.CANNON_GALLEON, huns)
        self.assertIn(Age2UnitData.DROMON, huns)
        world = self.build(**EVERYTHING)
        attila_6 = [scenario for scenario in world.rules.logic.scenarios
                    if scenario.scenario.name == "AP_ATTILA_6"][0]
        rule = attila_6.military.has_naval_bombardment().resolve(world)
        self.assertFalse(rule.always_false)

    def test_a_navy_needs_water(self):
        """has_water_access had been declared on every starting state and read by nothing."""
        from rule_builder.rules import False_
        world = self.build(**EVERYTHING)
        scenario = world.rules.logic.scenarios[0]
        scenario.starting_state.has_water_access = False_()
        self.assertTrue(scenario.military.has_navy().resolve(world).always_false)
        self.assertTrue(scenario.military.has_naval_bombardment().resolve(world).always_false)


class TestRoles(Age2RuleTestBase):

    ROLES = (UnitRole.military, UnitRole.building_counter, UnitRole.siege,
             UnitRole.long_range_siege, UnitRole.navy, UnitRole.naval_bombardment)

    def fillable(self, world) -> dict[str, set[str]]:
        return {scenario.scenario.name:
                {role for role in self.ROLES
                 if not scenario.military.can_field_role(role).resolve(world).always_false}
                for scenario in world.rules.logic.scenarios}

    def test_no_scenario_asks_for_a_role_it_cannot_fill(self):
        """The invariant the whole split is for.

        Attila 1 opens in the Dark Age and never reaches Imperial, so it can field no trebuchet
        and no cannon galleon - and it asks for neither. Scoped globally these read as satisfied,
        because Attila 6 does reach Imperial and the Or could not tell the two apart.
        """
        import inspect
        world = self.build(**EVERYTHING)
        fillable = self.fillable(world)
        asks = {"has_military": UnitRole.military,
                "counters_building": UnitRole.building_counter,
                "has_siege": UnitRole.siege,
                "has_long_range_siege": UnitRole.long_range_siege,
                "has_navy": UnitRole.navy,
                "has_naval_bombardment": UnitRole.naval_bombardment}
        offenders = []
        for rules in world.rules.scenario_rules:
            name = rules.scenario.name
            source = Path(inspect.getfile(type(rules))).read_text(encoding="utf-8")
            offenders += [f"{name} asks {method}" for method, role in asks.items()
                          if f"military.{method}(" in source and role not in fillable[name]]
        self.assertEqual(offenders, [])

    def test_every_role_is_fillable_by_some_scenario(self):
        """A role no scenario in the world can fill is a vocabulary nobody can use."""
        world = self.build(**EVERYTHING)
        fillable = self.fillable(world)
        for role in self.ROLES:
            with self.subTest(role=role):
                self.assertTrue([name for name, roles in fillable.items() if role in roles])

    def test_a_fixed_force_fills_no_role(self):
        """Joan 1 and Joan 5 are set pieces fought with what they hand you - no base and no age
        to be in, so no army of their own at any grade."""
        world = self.build(**EVERYTHING)
        fillable = self.fillable(world)
        self.assertEqual(fillable["AP_JOAN_1"], set())
        self.assertEqual(fillable["AP_JOAN_5"], set())

    def test_the_mangonel_line_is_not_siege(self):
        """It has a building attack and it is anti-infantry. Nobody takes a castle down with
        onagers, and the roles record that judgement rather than the damage table."""
        self.assertNotIn(Age2UnitLineData.MANGONEL_LINE, ROLE_TO_LINES[UnitRole.siege])
        self.assertIn(Age2UnitLineData.MANGONEL_LINE, ROLE_TO_LINES[UnitRole.military])

    def test_siege_is_not_an_army(self):
        """Battering Rams alone once beat Attila 1's first opponent: they counted as military."""
        self.assertFalse(set(ROLE_TO_LINES[UnitRole.siege]) & set(ROLE_TO_LINES[UnitRole.military]))

    def test_a_suicide_raft_is_not_a_navy(self):
        """A Demolition Ship blows itself up on contact: it can sink a fleet, never hold the
        water. Counting it let Demolition Rafts alone win the water in The Walls of
        Constantinople and guard every fishing boat."""
        for line in (Age2UnitLineData.DEMOLITION_RAFT_LINE, Age2UnitLineData.INCENDIARY_RAFT_LINE):
            with self.subTest(line.name):
                self.assertNotIn(line, ROLE_TO_LINES[UnitRole.navy])


class TestCounters(Age2RuleTestBase):

    def test_a_ship_never_counters_a_land_unit(self):
        """A fleet cannot answer an army on land. The other way round stands: a Bombard Cannon or
        a Mangonel on the shore does sink ships."""
        ships = set(SHIP_LINES)
        crossed = [(line.name, counter.name) for line in Age2UnitLineData
                   for counter in line.countered_by
                   if line not in ships and counter in ships]
        self.assertEqual([], crossed)

    def test_a_monk_converts_siege_only_with_redemption(self):
        """Monks answered Mangonels with nothing researched, and a monk cannot convert a siege
        weapon without Redemption. Ships and cavalry need nothing."""
        from ..locations.Techs import Age2TechData
        monk, redemption = Age2UnitLineData.MONK_LINE, Age2TechData.REDEMPTION
        self.assertIs(redemption, Age2UnitLineData.MANGONEL_LINE.counter_techs[monk])
        self.assertIs(redemption, Age2UnitLineData.BATTERING_RAM_LINE.counter_techs[monk])
        self.assertNotIn(monk, Age2UnitLineData.CANNON_GALLEON_LINE.counter_techs)
        self.assertNotIn(monk, Age2UnitLineData.KNIGHT_LINE.counter_techs)
        # Only the counter it names needs the tech: a Knight answers a Mangonel as it is.
        self.assertNotIn(Age2UnitLineData.KNIGHT_LINE, Age2UnitLineData.MANGONEL_LINE.counter_techs)
        world = self.build(monks_can_counter=True, **EVERYTHING)
        attila_1 = world.rules.logic.for_scenario(Age2ScenarioLocationData.ATT1_VICTORY.scenario)
        siege = attila_1.military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.CASTLE)
        knight = attila_1.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE)
        # The Huns never research Redemption, so their monks answer Knights but never Mangonels.
        # counters() is named, and a name explains as its label alone: read the rule behind it.
        self.assertNotIn("can field the Monk Line", siege.resolve(world).answer.explain_str())
        self.assertIn("can field the Monk Line", knight.resolve(world).answer.explain_str())

    def test_the_demolition_ship_falls_to_galleys_and_turtle_ships(self):
        for counter in (Age2UnitLineData.GALLEY_LINE, Age2UnitLineData.TURTLE_SHIP_LINE):
            with self.subTest(counter.name):
                self.assertIn(counter, Age2UnitLineData.DEMOLITION_RAFT_LINE.countered_by)


class TestRamsAreASponge(Age2RuleTestBase):
    """A ram soaks arrows; it kills nothing that shoots back. It counts against the lines it soaks
    for only with an army behind it doing the damage, and against siege it counts on its own."""

    SOAKED = (
        Age2UnitLineData.ARCHER_LINE,
        Age2UnitLineData.CAVALRY_ARCHER_LINE,
        Age2UnitLineData.LONGBOWMAN_LINE,
        Age2UnitLineData.PLUMED_ARCHER_LINE,
        Age2UnitLineData.RATTAN_ARCHER_LINE,
        Age2UnitLineData.BALLISTA_ELEPHANT_LINE,
        Age2UnitLineData.SKIRMISHER_LINE,
    )
    # Counters none of the soaked lines itself, so only the sponge can answer them with it.
    ESCORT = Age2UnitLineData.HAND_CANNONEER_LINE
    RAM = Age2UnitLineData.BATTERING_RAM_LINE

    def can_counter_fielding(self, fielded: set[Age2UnitLineData],
                             target: Age2UnitLineData) -> bool:
        """Whether Attila 1 counters `target` in the Castle Age when `fielded` is all it fields."""
        world = self.build(**EVERYTHING)
        attila_1 = world.rules.logic.for_scenario(Age2ScenarioLocationData.ATT1_VICTORY.scenario)

        def can_field(_unit_logic, line, age=None):
            return True_() if line in fielded else False_()

        with mock.patch.object(ScenarioUnitLogic, "can_field", autospec=True,
                               side_effect=can_field):
            rule = attila_1.military.counters(target, Age2AgeData.CASTLE)
            return not rule.resolve(world).always_false

    def test_the_escort_alone_counters_none_of_them(self):
        for target in self.SOAKED:
            with self.subTest(target.name):
                self.assertFalse(self.can_counter_fielding({self.ESCORT}, target))

    def test_rams_alone_do_not_counter_what_they_soak_for(self):
        for target in self.SOAKED:
            with self.subTest(target.name):
                self.assertFalse(self.can_counter_fielding({self.RAM}, target))

    def test_rams_with_any_army_counter_what_they_soak_for(self):
        for target in self.SOAKED:
            with self.subTest(target.name):
                self.assertTrue(self.can_counter_fielding({self.RAM, self.ESCORT}, target))

    def test_the_armored_elephant_is_the_ram_of_an_elephant_civilisation(self):
        elephant_ram = Age2UnitLineData.ARMORED_ELEPHANT_LINE
        self.assertTrue(self.can_counter_fielding(
            {elephant_ram, self.ESCORT},
            Age2UnitLineData.ARCHER_LINE,
        ))

    def test_rams_counter_trebuchets_with_no_escort(self):
        for target in (Age2UnitLineData.TREBUCHET_LINE, Age2UnitLineData.MOUNTED_TREBUCHET_LINE):
            with self.subTest(target.name):
                self.assertTrue(self.can_counter_fielding({self.RAM}, target))


class TestMonksCanCounter(Age2RuleTestBase):
    """Converting is micro a yaml must ask for, except against elephants, where it is the standard
    counter and always counts."""

    FAITH = (Age2UnitLineData.MONK_LINE, Age2UnitLineData.MISSIONARY_LINE)
    ELEPHANTS = (
        Age2UnitLineData.BATTLE_ELEPHANT_LINE,
        Age2UnitLineData.WAR_ELEPHANT_LINE,
        Age2UnitLineData.ELEPHANT_ARCHER_LINE,
    )
    # Countered by both faith lines in the table.
    NOT_AN_ELEPHANT = Age2UnitLineData.KNIGHT_LINE

    def can_counter_fielding(self, faith: Age2UnitLineData, target: Age2UnitLineData,
                             **options) -> bool:
        """Whether Attila 1 counters `target` in the Castle Age when `faith` is all it fields."""
        world = self.build(**EVERYTHING, **options)
        attila_1 = world.rules.logic.for_scenario(Age2ScenarioLocationData.ATT1_VICTORY.scenario)

        def can_field(_unit_logic, line, age=None):
            return True_() if line is faith else False_()

        with mock.patch.object(ScenarioUnitLogic, "can_field", autospec=True,
                               side_effect=can_field):
            rule = attila_1.military.counters(target, Age2AgeData.CASTLE)
            return not rule.resolve(world).always_false

    def test_monks_do_not_counter_by_default(self):
        self.assertFalse(self.build().options.monks_can_counter)

    def test_off_a_faith_line_does_not_counter_what_is_not_an_elephant(self):
        for faith in self.FAITH:
            with self.subTest(faith.name):
                self.assertFalse(self.can_counter_fielding(
                    faith,
                    self.NOT_AN_ELEPHANT,
                    monks_can_counter=False,
                ))

    def test_off_a_faith_line_still_counters_each_elephant(self):
        for faith in self.FAITH:
            for elephant in self.ELEPHANTS:
                with self.subTest(faith=faith.name, target=elephant.name):
                    self.assertTrue(self.can_counter_fielding(
                        faith,
                        elephant,
                        monks_can_counter=False,
                    ))

    def test_on_a_faith_line_counters_elephants_and_everything_else(self):
        for faith in self.FAITH:
            for target in (self.NOT_AN_ELEPHANT, *self.ELEPHANTS):
                with self.subTest(faith=faith.name, target=target.name):
                    self.assertTrue(self.can_counter_fielding(
                        faith,
                        target,
                        monks_can_counter=True,
                    ))


class TestSiegeCanCounter(Age2RuleTestBase):
    """Mangonels, bombards and rocket carts need micro to land on an army, so a yaml must ask for
    it. Against other siege they need none and always count."""

    MANGONEL = Age2UnitLineData.MANGONEL_LINE
    # Counters nothing in the table itself, so it can only ever answer anything as a ram's escort.
    ROCKET_CART = Age2UnitLineData.ROCKET_CART_LINE
    RAM = Age2UnitLineData.BATTERING_RAM_LINE
    BOMBARD = Age2UnitLineData.BOMBARD_CANNON_LINE
    # Each pair is an anti-unit siege line and a target the table has it countering.
    AGAINST_AN_ARMY = (MANGONEL, Age2UnitLineData.ARCHER_LINE)
    AGAINST_A_SHIP = (BOMBARD, Age2UnitLineData.CANNON_GALLEON_LINE)
    AGAINST_SIEGE = (
        (MANGONEL, Age2UnitLineData.TREBUCHET_LINE),
        (BOMBARD, Age2UnitLineData.TREBUCHET_LINE),
        (BOMBARD, Age2UnitLineData.MANGONEL_LINE),
        (MANGONEL, Age2UnitLineData.SCORPION_LINE),
    )

    def can_counter_fielding(self, fielded: set[Age2UnitLineData], target: Age2UnitLineData,
                             **options) -> bool:
        """Whether Attila 1 counters `target` in the Castle Age when `fielded` is all it fields."""
        world = self.build(**EVERYTHING, **options)
        attila_1 = world.rules.logic.for_scenario(Age2ScenarioLocationData.ATT1_VICTORY.scenario)

        def can_field(_unit_logic, line, age=None):
            return True_() if line in fielded else False_()

        with mock.patch.object(ScenarioUnitLogic, "can_field", autospec=True,
                               side_effect=can_field):
            rule = attila_1.military.counters(target, Age2AgeData.CASTLE)
            return not rule.resolve(world).always_false

    def test_siege_does_not_counter_by_default(self):
        self.assertFalse(self.build().options.siege_can_counter)

    def test_off_anti_unit_siege_does_not_counter_an_army_or_a_ship(self):
        for siege, target in (self.AGAINST_AN_ARMY, self.AGAINST_A_SHIP):
            with self.subTest(siege=siege.name, target=target.name):
                self.assertFalse(self.can_counter_fielding(
                    {siege},
                    target,
                    siege_can_counter=False,
                ))

    def test_off_anti_unit_siege_still_counters_siege(self):
        for siege, target in self.AGAINST_SIEGE:
            with self.subTest(siege=siege.name, target=target.name):
                self.assertTrue(self.can_counter_fielding(
                    {siege},
                    target,
                    siege_can_counter=False,
                ))

    def test_on_anti_unit_siege_counters_armies_ships_and_siege(self):
        for siege, target in (self.AGAINST_AN_ARMY, self.AGAINST_A_SHIP, *self.AGAINST_SIEGE):
            with self.subTest(siege=siege.name, target=target.name):
                self.assertTrue(self.can_counter_fielding(
                    {siege},
                    target,
                    siege_can_counter=True,
                ))

    def test_the_scorpion_counters_an_army_whatever_the_option(self):
        for siege_can_counter in (False, True):
            with self.subTest(siege_can_counter=siege_can_counter):
                self.assertTrue(self.can_counter_fielding(
                    {Age2UnitLineData.SCORPION_LINE},
                    Age2UnitLineData.ARCHER_LINE,
                    siege_can_counter=siege_can_counter,
                ))

    def test_off_anti_unit_siege_is_no_escort_for_rams(self):
        for siege in (self.MANGONEL, self.ROCKET_CART):
            with self.subTest(siege.name):
                self.assertFalse(self.can_counter_fielding(
                    {self.RAM, siege},
                    Age2UnitLineData.ARCHER_LINE,
                    siege_can_counter=False,
                ))

    def test_on_anti_unit_siege_escorts_rams(self):
        self.assertTrue(self.can_counter_fielding(
            {self.RAM, self.ROCKET_CART},
            Age2UnitLineData.ARCHER_LINE,
            siege_can_counter=True,
        ))

    def test_off_the_organ_gun_is_an_army_to_a_mangonel(self):
        self.assertFalse(self.can_counter_fielding(
            {self.MANGONEL},
            Age2UnitLineData.ORGAN_GUN_LINE,
            siege_can_counter=False,
        ))

    def test_the_lines_that_count_as_armies_are_not_siege_targets(self):
        for line in (
            Age2UnitLineData.FIRE_ARCHER_LINE,
            Age2UnitLineData.PETARD_LINE,
            Age2UnitLineData.ORGAN_GUN_LINE,
        ):
            with self.subTest(line.name):
                self.assertNotIn(line, SIEGE_TARGETS)


class TestMilitaryIsAskedOfAScenario(Age2RuleTestBase):

    def test_there_is_no_global_military(self):
        """An army belongs to the scenario fighting with it, and nothing else asks.

        `self.logic.military` read perfectly naturally at every one of the 107 call sites while
        it meant "can a Siege Workshop go up anywhere", so nothing but a scan stops it coming
        back. The roles are data and live in connections/UnitRoles.py; there is no global half
        left to reach for.
        """
        offenders = []
        world_dir = Path(__file__).resolve().parent.parent
        for path in sorted(world_dir.rglob("*.py")):
            if "__pycache__" in path.parts or path.name == Path(__file__).name:
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if (isinstance(node, ast.Attribute) and node.attr == "military"
                        and isinstance(node.value, ast.Attribute)
                        and node.value.attr == "logic"):
                    offenders.append(f"{path.name}:{node.lineno}")
        self.assertEqual(offenders, [])

    def test_no_role_is_read_off_a_building(self):
        """The roles are about what a unit is.

        The Castle turns out Longbowmen and Chu Ko Nu, so "trained at a melee building" swept in
        two dozen lines that cannot scratch a wall. Every archer line must stay out.
        """
        for line in (Age2UnitLineData.LONGBOWMAN_LINE, Age2UnitLineData.CHU_KO_NU_LINE,
                     Age2UnitLineData.MANGUDAI_LINE, Age2UnitLineData.GENOESE_CROSSBOWMAN_LINE,
                     Age2UnitLineData.SKIRMISHER_LINE):
            self.assertNotIn(line, ROLE_TO_LINES[UnitRole.building_counter], line.line_name)
        # and the unit whose whole purpose is burning buildings down must stay in
        self.assertIn(Age2UnitLineData.TARKAN_LINE,
                      ROLE_TO_LINES[UnitRole.building_counter])

    def test_a_monastery_is_not_an_army_and_neither_is_a_dock(self):
        for line in (Age2UnitLineData.MONK_LINE, Age2UnitLineData.MISSIONARY_LINE,
                     Age2UnitLineData.GALLEY_LINE, Age2UnitLineData.VILLAGER_MALE_LINE,
                     Age2UnitLineData.TRADE_CART_LINE):
            self.assertNotIn(line, ROLE_TO_LINES[UnitRole.military], line.line_name)
        # The Warrior Priest is the exception: a Monastery unit that carries an axe and a sword,
        # so it is an army unit and it counters buildings.
        self.assertIn(Age2UnitLineData.WARRIOR_PRIEST_LINE, ROLE_TO_LINES[UnitRole.military])


class TestDefeatingOnePlayer(Age2RuleTestBase):
    """Attila 1 has four opponents and one location for beating any of them, so it is the union of
    what beating each costs - not the cost of beating the one the victory rule happens to name."""

    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def test_the_first_kill_costs_the_cheapest_opponent(self):
        """Blue is the cheapest of the three and needs the Feudal Age. Red and green need the
        Castle Age, and demanding that of this location would price it as a victory."""
        self.build(shuffle_ages=True)
        state = self.state_without("Castle Age", "Imperial Age")
        location = Age2ScenarioLocationData.ATT1_DEFEAT_FIRST_PLAYER.global_name()
        self.assertTrue(self.multiworld.get_location(location, self.world.player)
                        .access_rule(state))

    def test_the_victory_costs_more_than_the_first_kill(self):
        """Winning needs blue beaten and then one of red or green, so the same state that clears
        one player does not clear the scenario."""
        self.build(shuffle_ages=True)
        state = self.state_without("Castle Age", "Imperial Age")
        location = Age2ScenarioLocationData.ATT1_VICTORY.global_name()
        self.assertFalse(self.multiworld.get_location(location, self.world.player)
                         .access_rule(state))


class TestAttila3HasRulesForGreenAndRed(Age2RuleTestBase):
    """Green's and red's objectives had no rule of their own, so entering the scenario was the
    whole requirement: a dock or a Town Center fell with no army and no base."""

    OBJECTIVES = (
        Age2ScenarioLocationData.ATT3_GREEN_DOCK_NORTH,
        Age2ScenarioLocationData.ATT3_GREEN_DOCK_SOUTH,
        Age2ScenarioLocationData.ATT3_RED_DOCK,
        Age2ScenarioLocationData.ATT3_GREEN_TC,
        Age2ScenarioLocationData.ATT3_RED_TC,
        Age2ScenarioLocationData.ATT3_RED_MARKET,
    )

    def test_each_asks_for_an_army(self):
        world = self.build(**EVERYTHING)
        for objective in self.OBJECTIVES:
            with self.subTest(objective.name):
                location = self.multiworld.get_location(objective.global_name(), world.player)
                self.assertIn("can train", self.explained_through_names(location.access_rule))

    def explained_through_names(self, rule) -> str:
        """Every line of the rule's tree. A named rule or scenario question explains as its
        label alone, so the army it asks for sits below it."""
        lines = []
        seen = set()
        pending = [rule]
        while pending:
            node = pending.pop()
            if id(node) in seen:
                continue
            seen.add(id(node))
            lines.append(node.explain_str())
            for attribute in ("child", "answer"):
                if hasattr(node, attribute):
                    pending.append(getattr(node, attribute))
            pending.extend(getattr(node, "children", ()))
        return "\n".join(lines)
