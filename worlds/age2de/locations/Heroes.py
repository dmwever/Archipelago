import enum


@enum.unique
class Age2HeroData(enum.IntEnum):
    """The named characters a scenario hands the player, for unitsanity: all.

    Scoped to heroes a scenario actually grants rather than to everything the game flags as one -
    the unit data marks 244 heroes across every campaign, and all but these twelve belong to
    campaigns this world does not carry. A campaign added later brings its own.

    Locations only. A hero is never trainable, never an item, never caveman'd, belongs to no line
    and needs no upgrade token, so none of the invariants that hold over Age2UnitData apply. That
    is why these sit in their own enum rather than as units with a hero exemption bolted onto
    every one of those rules - the same reasoning as Age2VillagerJobData.

    Which scenario hands over which hero, and whether at the start or by a trigger, lives in
    connections/ScenarioStartupUnits.py and ScenarioTriggerUnits.py.
    """

    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, hero_name: str, game_id: int) -> None:
        self.id = id
        self.location_name = location_name
        self.hero_name = hero_name
        self.game_id = game_id

    # 584 - 799 = Heroes, picking up after the villager jobs. Ordered by game id.
    JOAN_THE_MAID       = 584, "Own Joan the Maid", "Joan the Maid", 430
    JOAN_OF_ARC         = 585, "Own Joan of Arc", "Joan of Arc", 629
    SIEUR_DE_METZ       = 586, "Own Sieur de Metz", "Sieur de Metz", 634
    SIEUR_BERTRAND      = 587, "Own Sieur Bertrand", "Sieur Bertrand", 636
    DUKE_D_ALENCON      = 588, "Own Duke d'Alençon", "Duke d'Alençon", 638
    LA_HIRE             = 589, "Own La Hire", "La Hire", 640
    LORD_DE_GRAVILLE    = 590, "Own Lord de Graville", "Lord de Graville", 642
    JEAN_DE_LORRAIN     = 591, "Own Jean de Lorrain", "Jean de Lorrain", 644
    CONSTABLE_RICHEMONT = 592, "Own Constable Richemont", "Constable Richemont", 646
    GUY_JOSSELYNE       = 593, "Own Guy Josselyne", "Guy Josselyne", 648
    JEAN_BUREAU         = 594, "Own Jean Bureau", "Jean Bureau", 650
    ATTILA_THE_HUN      = 595, "Own Attila the Hun", "Attila the Hun", 777


NAME_TO_HERO: dict[str, Age2HeroData] = {hero.hero_name: hero for hero in Age2HeroData}
GAME_ID_TO_HERO: dict[int, Age2HeroData] = {hero.game_id: hero for hero in Age2HeroData}
