"""Per-scenario rules - the ones a scenario's own objectives ask for.

Caveman lives here as well as in the unit logic: the global "Own X" locations already ask a
granted unit to be restorable, but a scenario objective that leans on units an item hands over
has to ask the same question for itself.
"""

from ..Options import Caveman, ScenarioBranching, Unitsanity, UnitsanityItems
from ..items.Items import Age2ItemData
from ..locations.Locations import Age2ScenarioLocationData as L
from ..locations.UnitLines import Age2UnitLineData
from .bases import Age2RuleTestBase

MONK_LINE = Age2UnitLineData.MONK_LINE.item.item_name
KEREYID = Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name

# What the Kereyid gate covers, per branching mode. Victory and the Complete event are gated in
# both: Victory wants four tribes joined, and the Ungirrads only join for a relic.
BRANCH_LOCATIONS = {
    ScenarioBranching.option_all: (L.GEN1_RELIC_RED_MONASTERY, L.GEN1_RELIC_WOLF,
                                   L.GEN1_RELIC_PALISADED, L.GEN1_RECRUIT_UNGIRRADS),
    ScenarioBranching.option_any: (L.GEN1_ANY_RELIC,),
}
ALWAYS_GATED = (L.GEN1_VICTORY,)
COMPLETE = "Complete " + L.GEN1_VICTORY.scenario.scenario_name

UNITSANITY = dict(unitsanity=Unitsanity.option_all,
                  unitsanity_items=UnitsanityItems.option_unit_line)


class TestGenghis1Relics(Age2RuleTestBase):
    """The Kereyid Tribe hands over the two monks that collect Genghis 1's relics. Under caveman
    the game knocks them down to Militia like any other unit a scenario trigger gives you, so the
    relics then want the Monk's unit items as well as the tribe."""

    campaigns = ["Genghis Khan"]
    starting_campaigns = ["Genghis Khan"]

    def gated_locations(self, branching: int) -> list[str]:
        covered = BRANCH_LOCATIONS[branching] + ALWAYS_GATED
        return [location.global_name() for location in covered] + [COMPLETE]

    def test_caveman_asks_for_the_monk_line_on_top_of_the_tribe(self):
        for branching, mode in ((ScenarioBranching.option_all, "all"),
                                (ScenarioBranching.option_any, "any")):
            self.build(caveman=Caveman.option_true, scenario_branching=branching, **UNITSANITY)
            without_monks = self.state_without(MONK_LINE)
            for name in self.gated_locations(branching):
                with self.subTest(branching=mode, location=name):
                    self.assertFalse(self.can_reach(name, without_monks))
                    self.assertTrue(self.can_reach(name))

    def test_the_gate_still_wants_the_tribe(self):
        """Restorable monks are not the whole answer - the tribe is what puts monks on the map."""
        self.build(caveman=Caveman.option_true,
                   scenario_branching=ScenarioBranching.option_any, **UNITSANITY)
        without_tribe = self.state_without(KEREYID)
        for name in self.gated_locations(ScenarioBranching.option_any):
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, without_tribe))

    def test_without_caveman_the_tribe_is_enough(self):
        for branching, mode in ((ScenarioBranching.option_all, "all"),
                                (ScenarioBranching.option_any, "any")):
            self.build(caveman=Caveman.option_false, scenario_branching=branching, **UNITSANITY)
            without_monks = self.state_without(MONK_LINE)
            for name in self.gated_locations(branching):
                with self.subTest(branching=mode, location=name):
                    self.assertTrue(self.can_reach(name, without_monks))

    def test_caveman_without_unitsanity_leaves_the_monk_alone(self):
        """No unit table row means the game never knocks the monk down, so there is nothing to
        restore and nothing new to ask for."""
        self.build(caveman=Caveman.option_true, unitsanity=Unitsanity.option_none,
                   scenario_branching=ScenarioBranching.option_any)
        for name in self.gated_locations(ScenarioBranching.option_any):
            with self.subTest(location=name):
                self.assertEqual(self.item_requirements(name), {KEREYID})
