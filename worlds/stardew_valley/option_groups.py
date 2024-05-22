from Options import OptionGroup, DeathLink, ProgressionBalancing, Accessibility
from .options import Goal, StartingMoney, ProfitMargin, BundleRandomization, BundlePrice, EntranceRandomization, \
    SeasonRandomization, Cropsanity, \
    BackpackProgression, ToolProgression, ElevatorProgression, SkillProgression, BuildingProgression, FestivalLocations, \
    ArcadeMachineLocations, \
    SpecialOrderLocations, QuestLocations, Fishsanity, Museumsanity, Friendsanity, FriendsanityHeartSize, \
    NumberOfMovementBuffs, NumberOfLuckBuffs, \
    ExcludeGingerIsland, TrapItems, MultipleDaySleepEnabled, MultipleDaySleepCost, ExperienceMultiplier, \
    FriendshipMultiplier, DebrisMultiplier, QuickStart, \
    Gifting, FarmType, Monstersanity, Shipsanity, Cooksanity, Chefsanity, Craftsanity, Mods

sv_option_groups = [
    OptionGroup('General', [
        Goal,
        FarmType,
        BundleRandomization,
        BundlePrice,
        EntranceRandomization,
        ExcludeGingerIsland,
    ]),
    OptionGroup('Major Unlocks', [
        SeasonRandomization,
        Cropsanity,
        BackpackProgression,
        ToolProgression,
        ElevatorProgression,
        SkillProgression,
        BuildingProgression,
    ]),
    OptionGroup('Extra Shuffling', [
        FestivalLocations,
        ArcadeMachineLocations,
        SpecialOrderLocations,
        QuestLocations,
        Fishsanity,
        Museumsanity,
        Friendsanity,
        FriendsanityHeartSize,
        Monstersanity,
        Shipsanity,
        Cooksanity,
        Chefsanity,
        Craftsanity
    ]),
    OptionGroup('Multipliers and Buffs', [
        StartingMoney,
        ProfitMargin,
        ExperienceMultiplier,
        FriendshipMultiplier,
        DebrisMultiplier,
        NumberOfMovementBuffs,
        NumberOfLuckBuffs,
        TrapItems,
        MultipleDaySleepEnabled,
        MultipleDaySleepCost,
        QuickStart,
    ]),
    OptionGroup('Advanced Options', [
        Gifting,
        DeathLink,
        Mods,
        ProgressionBalancing,
        Accessibility,
    ]),
]
