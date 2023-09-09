import os
import unittest
from argparse import Namespace
from typing import Dict, FrozenSet, Tuple, Any, ClassVar, Iterable

from BaseClasses import MultiWorld, CollectionState
from Utils import cache_argsless
from test.TestBase import WorldTestBase
from test.general import gen_steps, setup_solo_multiworld as setup_base_solo_multiworld
from .. import StardewValleyWorld
from ..mods.mod_data import ModNames
from worlds.AutoWorld import call_all
from ..options import Cropsanity, SkillProgression, SpecialOrderLocations, Friendsanity, NumberOfLuckBuffs, SeasonRandomization, ToolProgression, \
    ElevatorProgression, Museumsanity, BackpackProgression, BuildingProgression, ArcadeMachineLocations, HelpWantedLocations, Fishsanity, NumberOfMovementBuffs, \
    BundleRandomization, BundlePrice, FestivalLocations, FriendsanityHeartSize, ExcludeGingerIsland, TrapItems, Goal, Mods


def get_minsanity_options():
    minsanity = {
        options.Goal.internal_name: options.Goal.option_bottom_of_the_mines,
        options.BundleRandomization.internal_name: options.BundleRandomization.option_vanilla,
        options.BundlePrice.internal_name: options.BundlePrice.option_very_cheap,
        options.SeasonRandomization.internal_name: options.SeasonRandomization.option_disabled,
        options.Cropsanity.internal_name: options.Cropsanity.option_disabled,
        options.BackpackProgression.internal_name: options.BackpackProgression.option_vanilla,
        options.ToolProgression.internal_name: options.ToolProgression.option_vanilla,
        options.SkillProgression.internal_name: options.SkillProgression.option_vanilla,
        options.BuildingProgression.internal_name: options.BuildingProgression.option_vanilla,
        options.FestivalLocations.internal_name: options.FestivalLocations.option_disabled,
        options.ElevatorProgression.internal_name: options.ElevatorProgression.option_vanilla,
        options.ArcadeMachineLocations.internal_name: options.ArcadeMachineLocations.option_disabled,
        options.SpecialOrderLocations.internal_name: options.SpecialOrderLocations.option_disabled,
        options.HelpWantedLocations.internal_name: 0,
        options.Fishsanity.internal_name: options.Fishsanity.option_none,
        options.Museumsanity.internal_name: options.Museumsanity.option_none,
        options.Monstersanity.internal_name: options.Monstersanity.option_none,
        options.Shipsanity.internal_name: options.Shipsanity.option_none,
        options.Friendsanity.internal_name: options.Friendsanity.option_none,
        options.FriendsanityHeartSize.internal_name: 8,
        options.NumberOfMovementBuffs.internal_name: 0,
        options.NumberOfLuckBuffs.internal_name: 0,
        options.ExcludeGingerIsland.internal_name: options.ExcludeGingerIsland.option_true,
        options.TrapItems.internal_name: options.TrapItems.option_no_traps,
        options.Mods.internal_name: (),
    }
    return minsanity


class SVTestCase(unittest.TestCase):
    player: ClassVar[int] = 1
    """Set to False to not skip some 'extra' tests"""
    skip_extra_tests: bool = True
    """Set to False to run tests that take long"""
    skip_long_tests: bool = True
    """Set to False to run tests that take long"""
    skip_performance_tests: bool = True

    options = get_minsanity_options()

    def setUp(self) -> None:
        super().setUp()
        long_tests_key = "long"
        if long_tests_key in os.environ:
            self.skip_long_tests = not bool(os.environ[long_tests_key])
        performance_tests_key = "performance"
        if performance_tests_key in os.environ:
            self.skip_performance_tests = not bool(os.environ[performance_tests_key])


class SVTestBase(WorldTestBase, SVTestCase):
    game = "Stardew Valley"
    world: StardewValleyWorld

    def world_setup(self, *args, **kwargs):
        super().world_setup(*args, **kwargs)
        if self.constructed:
            self.world = self.multiworld.worlds[self.player]  # noqa

    @property
    def run_default_tests(self) -> bool:
        # world_setup is overridden, so it'd always run default tests when importing SVTestBase
        is_not_stardew_test = type(self) is not SVTestBase
        should_run_default_tests = is_not_stardew_test and super().run_default_tests
        return should_run_default_tests


@cache_argsless
def minimal_locations_maximal_items():
    min_max_options = {
        Goal.internal_name: Goal.option_bottom_of_the_mines,
        BundleRandomization.internal_name: BundleRandomization.option_vanilla,
        BundlePrice.internal_name: BundlePrice.option_very_cheap,
        SeasonRandomization.internal_name: SeasonRandomization.option_randomized,
        Cropsanity.internal_name: Cropsanity.option_shuffled,
        BackpackProgression.internal_name: BackpackProgression.option_vanilla,
        ToolProgression.internal_name: ToolProgression.option_vanilla,
        SkillProgression.internal_name: SkillProgression.option_vanilla,
        BuildingProgression.internal_name: BuildingProgression.option_vanilla,
        FestivalLocations.internal_name: FestivalLocations.option_disabled,
        ElevatorProgression.internal_name: ElevatorProgression.option_vanilla,
        ArcadeMachineLocations.internal_name: ArcadeMachineLocations.option_disabled,
        SpecialOrderLocations.internal_name: SpecialOrderLocations.option_disabled,
        HelpWantedLocations.internal_name: 0,
        Fishsanity.internal_name: Fishsanity.option_none,
        Museumsanity.internal_name: Museumsanity.option_none,
        Monstersanity.internal_name: Monstersanity.option_none,
        Shipsanity.internal_name: Shipsanity.option_none,
        Friendsanity.internal_name: Friendsanity.option_none,
        FriendsanityHeartSize.internal_name: 8,
        NumberOfMovementBuffs.internal_name: 12,
        NumberOfLuckBuffs.internal_name: 12,
        options.ExcludeGingerIsland.internal_name: ExcludeGingerIsland.option_true,
        options.TrapItems.internal_name: TrapItems.option_nightmare,
        options.Mods.internal_name: (),
    }
    return min_max_options


@cache_argsless
def minsanity_options():
    minsanity = {
        Goal.internal_name: Goal.option_bottom_of_the_mines,
        BundleRandomization.internal_name: BundleRandomization.option_vanilla,
        BundlePrice.internal_name: BundlePrice.option_very_cheap,
        SeasonRandomization.internal_name: SeasonRandomization.option_disabled,
        Cropsanity.internal_name: Cropsanity.option_disabled,
        BackpackProgression.internal_name: BackpackProgression.option_vanilla,
        ToolProgression.internal_name: ToolProgression.option_vanilla,
        SkillProgression.internal_name: SkillProgression.option_vanilla,
        BuildingProgression.internal_name: BuildingProgression.option_vanilla,
        FestivalLocations.internal_name: FestivalLocations.option_disabled,
        ElevatorProgression.internal_name: ElevatorProgression.option_vanilla,
        ArcadeMachineLocations.internal_name: ArcadeMachineLocations.option_disabled,
        SpecialOrderLocations.internal_name: SpecialOrderLocations.option_disabled,
        HelpWantedLocations.internal_name: 0,
        Fishsanity.internal_name: Fishsanity.option_none,
        Museumsanity.internal_name: Museumsanity.option_none,
        Monstersanity.internal_name: Monstersanity.option_none,
        Shipsanity.internal_name: Shipsanity.option_none,
        Friendsanity.internal_name: Friendsanity.option_none,
        FriendsanityHeartSize.internal_name: 8,
        NumberOfMovementBuffs.internal_name: 0,
        NumberOfLuckBuffs.internal_name: 0,
        ExcludeGingerIsland.internal_name: ExcludeGingerIsland.option_true,
        TrapItems.internal_name: TrapItems.option_no_traps,
        Mods.internal_name: (),
    }
    return minsanity


@cache_argsless
def default_options():
    default = {}
    return default


@cache_argsless
def allsanity_options_without_mods():
    allsanity = {
        Goal.internal_name: Goal.option_perfection,
        BundleRandomization.internal_name: BundleRandomization.option_shuffled,
        BundlePrice.internal_name: BundlePrice.option_expensive,
        SeasonRandomization.internal_name: SeasonRandomization.option_randomized,
        Cropsanity.internal_name: Cropsanity.option_shuffled,
        BackpackProgression.internal_name: BackpackProgression.option_progressive,
        ToolProgression.internal_name: ToolProgression.option_progressive,
        SkillProgression.internal_name: SkillProgression.option_progressive,
        BuildingProgression.internal_name: BuildingProgression.option_progressive,
        FestivalLocations.internal_name: FestivalLocations.option_hard,
        ElevatorProgression.internal_name: ElevatorProgression.option_progressive,
        ArcadeMachineLocations.internal_name: ArcadeMachineLocations.option_full_shuffling,
        SpecialOrderLocations.internal_name: SpecialOrderLocations.option_board_qi,
        HelpWantedLocations.internal_name: 56,
        Fishsanity.internal_name: Fishsanity.option_all,
        Museumsanity.internal_name: Museumsanity.option_all,
        Monstersanity.internal_name: Monstersanity.option_progressive_goals,
        Shipsanity.internal_name: ,
        Friendsanity.internal_name: Friendsanity.option_all_with_marriage,
        FriendsanityHeartSize.internal_name: 1,
        NumberOfMovementBuffs.internal_name: 12,
        NumberOfLuckBuffs.internal_name: 12,
        ExcludeGingerIsland.internal_name: ExcludeGingerIsland.option_false,
        TrapItems.internal_name: TrapItems.option_nightmare,
    }
    return allsanity


@cache_argsless
def allsanity_options_with_mods():
    allsanity = {}
    allsanity.update(allsanity_options_without_mods())
    all_mods = (
        ModNames.deepwoods, ModNames.tractor, ModNames.big_backpack,
        ModNames.luck_skill, ModNames.magic, ModNames.socializing_skill, ModNames.archaeology,
        ModNames.cooking_skill, ModNames.binning_skill, ModNames.juna,
        ModNames.jasper, ModNames.alec, ModNames.yoba, ModNames.eugene,
        ModNames.wellwick, ModNames.ginger, ModNames.shiko, ModNames.delores,
        ModNames.ayeisha, ModNames.riley, ModNames.skull_cavern_elevator
    )
    allsanity.update({Mods.internal_name: all_mods})
    return allsanity


pre_generated_worlds = {}


# Mostly a copy of test.general.setup_solo_multiworld, I just don't want to change the core.
def setup_solo_multiworld(test_options=None, seed=None, _cache: Dict[FrozenSet[Tuple[str, Any]], MultiWorld] = {}) -> MultiWorld:  # noqa
    if test_options is None:
        test_options = {}

    # Yes I reuse the worlds generated between tests, its speeds the execution by a couple seconds
    frozen_options = frozenset(test_options.items()).union({seed})
    if frozen_options in _cache:
        return _cache[frozen_options]

    multiworld = setup_base_solo_multiworld(StardewValleyWorld, ())
    multiworld.set_seed(seed)
    # print(f"Seed: {multiworld.seed}") # Uncomment to print the seed for every test
    args = Namespace()
    for name, option in StardewValleyWorld.options_dataclass.type_hints.items():
        value = option(test_options[name]) if name in test_options else option.from_any(option.default)
        setattr(args, name, {1: value})
    multiworld.set_options(args)
    for step in gen_steps:
        call_all(multiworld, step)

    _cache[frozen_options] = multiworld

    return multiworld


def setup_multiworld(test_options: Iterable[Dict[str, int]] = None, seed=None) -> MultiWorld:  # noqa
    if test_options is None:
        test_options = []

    multiworld = MultiWorld(len(test_options))
    multiworld.player_name = {}
    multiworld.set_seed(seed)
    multiworld.state = CollectionState(multiworld)
    for i in range(1, len(test_options) + 1):
        args = Namespace()
        multiworld.game[i] = StardewValleyWorld.game
        multiworld.player_name.update({i: f"Tester{i}"})
    for name, option in StardewValleyWorld.options_dataclass.type_hints.items():
        options = {}
        for i in range(1, len(test_options) + 1):
            player_options = test_options[i-1]
            value = option(player_options[name]) if name in player_options else option.from_any(option.default)
            options.update({i: value})
        setattr(args, name, options)
    multiworld.set_options(args)

    for step in gen_steps:
        call_all(multiworld, step)

    return multiworld
