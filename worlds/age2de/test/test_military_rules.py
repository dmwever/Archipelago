import ast
from pathlib import Path

from ..Options import IncludeUniqueUnits, Unitsanity
from ..locations.Ages import Age2AgeData
from ..locations.Civilizations import Age2CivData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS
from ..locations.connections.UnitRoles import ROLE_TO_LINES, UnitRole
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
                     Age2UnitLineData.WARRIOR_PRIEST_LINE, Age2UnitLineData.GALLEY_LINE,
                     Age2UnitLineData.VILLAGER_LINE, Age2UnitLineData.TRADE_CART_LINE):
            self.assertNotIn(line, ROLE_TO_LINES[UnitRole.military], line.line_name)
