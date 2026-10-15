import enum


@enum.unique
class Age2HeroData(enum.IntEnum):
    """The named characters a scenario hands the player"""

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
    
    # Attila the Hun
    ATTILA_THE_HUN      = 595, "Own Attila the Hun", "Attila the Hun", 777
    
    # Genghis Khan.
    SUBOTAI             = 602, "Own Subotai", "Subotai", 698
    SABOTEUR            = 603, "Own Saboteur", "Saboteur", 706
    KHAN                = 604, "Own Khan", "Khan", 1275          # scenario-only unit, not a hero
    HUNTING_WOLF        = 605, "Own Hunting Wolf", "Hunting Wolf", 700


NAME_TO_HERO: dict[str, Age2HeroData] = {hero.hero_name: hero for hero in Age2HeroData}
GAME_ID_TO_HERO: dict[int, Age2HeroData] = {hero.game_id: hero for hero in Age2HeroData}
