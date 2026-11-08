import dataclasses

LAND = frozenset({0, 2, 3, 5, 6, 9, 11, 12, 24, 25, 27, 40, 41})
BEACH = frozenset({2})
WATER = frozenset({1, 4, 22, 23})

WONDER = 276
DOCK = 45
ARCHERY_RANGE = 87
TOWN_CENTER = 109
TRANSPORT_SHIP = 545
BOMBARD_CANNON = 36
PACKED_TREBUCHET = 331


FOOTPRINT = {ARCHERY_RANGE: 3, DOCK: 3, WONDER: 6}


@dataclasses.dataclass(frozen=True)
class Create:
    name: str
    unit_const: int
    owner: int
    foundation: bool
    search: tuple[int, int, int, int]
    prefer: tuple[int, int]
    tick: int = 1
    terrain: frozenset[int] = LAND
    needs_water: bool = False
    limit: int = 5
    radius: int = 8

    @property
    def footprint(self):
        return FOOTPRINT.get(self.unit_const, 1)


@dataclasses.dataclass(frozen=True)
class Probe:
    name: str
    expr: str
    expect: object = None
    note: str = ""
    forbid: object = None


@dataclasses.dataclass(frozen=True)
class Fork:
    key: str
    fork_id: int
    source: str
    scenario_id: int
    title: str
    checks: tuple[str, ...]
    look: tuple[str, ...]
    items: tuple[int, ...] = ()
    reveal: tuple[tuple[int, int, int], ...] = ()
    creates: tuple[Create, ...] = ()
    recipe_ops: tuple[dict, ...] = ()
    trigger_ops: tuple[dict, ...] = ()
    unit_pins: tuple[tuple[int, int, int], ...] = ()
    trigger_pins: tuple[str, ...] = ()
    globals: tuple[tuple[str, str], ...] = ()
    stage: tuple[tuple[int, tuple[str, ...]], ...] = ()
    probes: tuple[Probe, ...] = ()
    shorten: tuple[tuple[int, tuple[str, ...]], ...] = ()
    difficulties: tuple[str, ...] = ("any",)
    caveats: tuple[str, ...] = ()


JOAN_3_BOATS = 1011
ATTILA_3_RED_GOLD = 1005
ATTILA_3_GREEN_GOLD = 1006
JOAN_6_ARMY = 1023
JOAN_6_ARTILLERY = 4011
SKIRMISHER_LINE = 302
GALLEY_LINE = 333
DEMOLITION_LINE = 358
JIN_BLACKSMITHS = (10062, 10063, 10064, 10065, 10096, 10097, 10098, 10099, 10100)

ELITE_SKIRMISHER_TECH = 3652
WAR_GALLEY_TECH = 3621
DEMOLITION_SHIP_TECH = 3842


J3B = Fork(
    key="J3B",
    fork_id=1,
    source="AP_Joan_3",
    scenario_id=203,
    title="Joan 3: the boats trigger fires",
    checks=("#58",),
    items=(JOAN_3_BOATS,),
    reveal=((14, 86, 16),),
    unit_pins=((679, 527, 0),),
    trigger_pins=("AP Give Boats", "AP Find Boats", "[D0] Finding Boats"),
    probes=(
        Probe("transports_p1", "PT82Count(1, 545)", 2,
              "AP Give Boats creates two Transport Ships for P1"),
        Probe("boats_item", "PT82Bool(HasJoan3Boats())", 1),
        Probe("find_boats_sent", "PT82Bool(IsScenarioLocationComplete(20301))", 1),
        Probe("boat_679_alive", "PT82Bool(xsDoesUnitExist(679))"),
        Probe("boat_679_owner", "PT82Owner(679)"),
    ),
    look=(
        "Two Transport Ships stand at (14,85) and (15,85) in Joan's colour.",
        "'[D0] Finding Boats' puts up its message and nothing else: no units, no sound, no gift.",
        "The chat line 'PT82 J3B' reports what the sidecar recorded.",
    ),
)

A3G = Fork(
    key="A3G",
    fork_id=2,
    source="AP_Attila_3",
    scenario_id=103,
    title="Attila 3: both gold tributes pay P1 the full 3000, out of Constantinople",
    checks=("#66",),
    items=(ATTILA_3_RED_GOLD, ATTILA_3_GREEN_GOLD),
    reveal=((93, 23, 20),),
    unit_pins=((852, 109, 4), (2705, 109, 3)),
    trigger_pins=("AP Give Green TC Gold", "AP Give Red TC Gold"),
    globals=(("pt82P1Before", "-1"), ("pt82P2Before", "-1"), ("pt82P3Before", "-1"),
             ("pt82P4Before", "-1"), ("pt82P1AtTribute", "-1"), ("pt82P2AtTribute", "-1")),
    stage=(
        (4, (
            "pt82P1Before = PT82Gold(1);",
            "pt82P2Before = PT82Gold(2);",
            "pt82P3Before = PT82Gold(3);",
            "pt82P4Before = PT82Gold(4);",
            'xsChatData("<YELLOW>PT82 A3G: gold at the start - P1 " + pt82P1Before'
            ' + " P2 " + pt82P2Before + " P3 " + pt82P3Before + " P4 " + pt82P4Before);',
        )),
        (7, (
            "pt82P1AtTribute = PT82Gold(1);",
            "pt82P2AtTribute = PT82Gold(2);",
            'xsChatData("<YELLOW>PT82 A3G: Constantinople holds " + pt82P2AtTribute'
            ' + " gold. Both Town Centers fall next second; P1 should gain 6000.");',
        )),
    ),
    trigger_ops=(
        {"op": "add_trigger", "name": "PT82 Raze Both Town Centers", "enabled": True,
         "conditions": [{"op": "timer", "timer": 8}],
         "effects": [
             {"op": "kill_object", "source_player": 4, "selected_object_ids": [852]},
             {"op": "kill_object", "source_player": 3, "selected_object_ids": [2705]},
         ]},
    ),
    probes=(
        Probe("p1_gold_at_tribute", "pt82P1AtTribute"),
        Probe("p1_gold_now", "PT82Gold(1)", None,
              "6000 above p1_gold_at_tribute, give or take what the villagers mined, means"
              " both tributes paid in full"),
        Probe("p2_gold_at_tribute", "pt82P2AtTribute", None,
              "Constantinople, the payer; starts on 50000"),
        Probe("p2_gold_now", "PT82Gold(2)", None, "6000 lighter if both tributes came from here"),
        Probe("p3_gold_at_start", "pt82P3Before", None, "Marcianopolis; a control, should not pay"),
        Probe("p3_gold_now", "PT82Gold(3)"),
        Probe("p4_gold_at_start", "pt82P4Before", None, "Philippopolis; a control, should not pay"),
        Probe("p4_gold_now", "PT82Gold(4)"),
        Probe("red_item", "PT82Bool(HasAttila3RedGold())", 1),
        Probe("green_item", "PT82Bool(HasAttila3GreenGold())", 1),
        Probe("red_tc_852_alive", "PT82Bool(xsDoesUnitExist(852))", 0),
        Probe("green_tc_2705_alive", "PT82Bool(xsDoesUnitExist(2705))", 0),
    ),
    caveats=(
        "Both Town Centers are razed eight seconds in by an added trigger using the editor's own"
        " kill_object effect, which is the earliest the tribute can ever run.",
        "The payer is P2 Constantinople, who starts on 50000 gold, so the purse is no longer the"
        " question #66 asked. What is under test now is that both tributes fire and pay 3000"
        " each, and that P3 and P4 are not touched.",
        "The two vanilla tributes in the shipped set - Joan 3's [D9] Fastolf Attacks and Genghis"
        " 6's [D1] T - 20 - source Gaia instead. P2 is the maintainer's call and holds ample"
        " gold; it just means the gold is finite where Gaia's would not be.",
    ),
    look=(
        "P1's gold counter jumps 3000 as each Town Center falls, 6000 in all.",
        "Constantinople's purse is what drops; the chat prints it before and the sidecar after.",
    ),
)

J5V = Fork(
    key="J5V",
    fork_id=3,
    source="AP_Joan_5",
    scenario_id=205,
    title="Joan 5: six refugees without Joan do not win",
    checks=("#68", "#79"),
    reveal=((177, 131, 14),),
    unit_pins=((18125, 83, 0), (18117, 83, 0), (18121, 83, 0),
               (18120, 293, 0), (18116, 83, 0), (18122, 83, 0),
               (14871, 629, 1)),
    trigger_pins=("AP Victory", "Joan in Area", "Refugees in Area 1", "Refugees in Area 6"),
    recipe_ops=(
        {"op": "edit_unit", "reference_id": 18125, "set_player": 1, "x": 175.5, "y": 129.5},
        {"op": "edit_unit", "reference_id": 18117, "set_player": 1, "x": 176.5, "y": 129.5},
        {"op": "edit_unit", "reference_id": 18121, "set_player": 1, "x": 177.5, "y": 129.5},
        {"op": "edit_unit", "reference_id": 18120, "set_player": 1, "x": 178.5, "y": 129.5},
        {"op": "edit_unit", "reference_id": 18116, "set_player": 1, "x": 175.5, "y": 130.5},
        {"op": "edit_unit", "reference_id": 18122, "set_player": 1, "x": 176.5, "y": 130.5},
        {"op": "edit_unit", "reference_id": 14871, "x": 172.5, "y": 131.5},
    ),
    probes=(
        Probe("joan_alive", "PT82Bool(xsDoesUnitExist(14871))", 1),
        Probe("refugee_men_p1", "PT82Count(1, 83)", 5, "the five male refugees moved in"),
        Probe("refugee_women_p1", "PT82Count(1, 293)", 1, "the one female refugee moved in"),
        Probe("victory_sent", "PT82Bool(IsScenarioLocationComplete(20500))"),
        Probe("has_victory", "PT82Bool(HasVictory())"),
    ),
    look=(
        "Six refugees already stand inside Compiegne and Joan starts three tiles west of it.",
        "Nothing wins while Joan is outside: no victory banner, no AP victory chat.",
        "Walk Joan into the marked ground and the scenario declares victory then, not before.",
    ),
    caveats=(
        "The six refugees are handed to P1 in the file, so 'Locate Refugee 1-6' fire at once."
        " What is under test is the escorted count (variable 1) against Joan (variable 2),"
        " which is what #79 repointed AP Victory at.",
        "The six are the ones 'Locate Refugee 1' through '6' name: 18125, 18117, 18121, 18120,"
        " 18116 and 18122. Refugees 7 to 10 are left where the scenario puts them.",
        "Joan stands alone three tiles from Compiegne with the rest of the army still at the"
        " start, so walk her in promptly; nothing here protects her.",
    ),
)

J6S = Fork(
    key="J6S",
    fork_id=4,
    source="AP_Joan_6",
    scenario_id=206,
    title="Joan 6: the difficulty siege spawns as Gaia and the AP grants take it",
    checks=("#70",),
    items=(JOAN_6_ARMY, JOAN_6_ARTILLERY),
    reveal=((108, 120, 14), (136, 125, 14), (133, 115, 10), (109, 118, 10)),
    unit_pins=((8171, 448, 0), (8105, 5, 0)),
    trigger_pins=("AP Give Army", "AP Give Artillery", "Easy", "Easy and Moderate"),
    recipe_ops=(
        {"op": "move_units_in_area", "target_player": 1,
         "target_area_x1": 130, "target_area_y1": 60,
         "target_area_x2": 145, "target_area_y2": 72,
         "target_x": 131, "target_y": 118},
    ),
    probes=(
        Probe("army_item", "PT82Bool(HasJoan6Army())", 1),
        Probe("artillery_item", "PT82Bool(HasJoan6Artillery())", 1),
        Probe("p1_bombard_cannons", "PT82Count(1, 36)"),
        Probe("p1_packed_trebuchets", "PT82Count(1, 331)"),
        Probe("gaia_bombard_cannons", "PT82Count(0, 36)", 0,
              "any left on Gaia means a grant missed it; -1 means Gaia would not enumerate,"
              " so the screen decides"),
        Probe("gaia_packed_trebuchets", "PT82Count(0, 331)", 0,
              "-1 means Gaia would not enumerate, so the screen decides"),
    ),
    difficulties=("Easy", "Moderate"),
    look=(
        "On Easy: a Bombard Cannon at (108,120) and a Packed Trebuchet at (136,125).",
        "On Moderate: Bombard Cannons at (107,120) and (103,120), no Trebuchet.",
        "Each one appears in Gaia's colour first, then flips to Joan's when the grant area sees it.",
        "Nothing is left standing in Gaia's colour once both grants have run.",
    ),
    caveats=(
        "Difficulty is chosen in the launch menu, not in the file, so this fork is played twice."
        " 'Easy' fires on Easy only; 'Easy and Moderate' fires on both, so Moderate is the run"
        " that separates them.",
    ),
)

G3W = Fork(
    key="G3W",
    fork_id=5,
    source="AP_Genghis_3",
    scenario_id=303,
    title="Genghis 3: the Wonder reveal, the timer, and what expiry does",
    checks=("#60", "#84"),
    reveal=(),
    creates=(
        Create("pt82Foundation", WONDER, 4, True,
               search=(120, 163, 130, 173), prefer=(125, 168), tick=5),
        Create("pt82Wonder", WONDER, 4, False,
               search=(162, 160, 172, 170), prefer=(167, 165), tick=35),
    ),
    unit_pins=((18274, TOWN_CENTER, 4),) + tuple((ref, 103, 4) for ref in JIN_BLACKSMITHS),
    recipe_ops=tuple({"op": "remove_unit", "reference_id": ref} for ref in JIN_BLACKSMITHS),
    globals=(
        ("pt82Shortened", "-1"),
        ("pt82FoundSlotIdle", "-1"),
        ("pt82FoundRevealIdle", "-1"),
        ("pt82FoundBegun", "-1"),
        ("pt82FoundRevealBuilt", "-1"),
        ("pt82WonderSlotArmed", "-1"),
        ("pt82WonderRevealArmed", "-1"),
        ("pt82WonderCounting", "-1"),
        ("pt82WonderYearsArmed", "-1"),
    ),
    stage=(
        (5, (
            'xsChatData("<YELLOW>PT82 G3W: a Jin Wonder foundation is going up on the Jin"'
            ' + " building plot. Nothing has been built on it yet, so nothing should light up.");',
        )),
        (10, (
            "pt82FoundSlotIdle = PT82Slot(pt82Foundation);",
            "pt82FoundRevealIdle = PT82RevealKind(pt82Foundation);",
            'xsChatData("<YELLOW>PT82 G3W: the untouched foundation holds slot "'
            ' + pt82FoundSlotIdle + " with reveal kind " + pt82FoundRevealIdle'
            ' + ", where 0 is no reveal at all. Ten seconds to look.");',
        )),
        (20, (
            "pt82FoundBegun = PT82BuildTo(pt82Foundation, 4, 276, 10);",
            'xsChatData("<YELLOW>PT82 G3W: the foundation is now 10% built, so its construction"'
            ' + " site should light up and nothing beyond it.");',
        )),
        (30, (
            "pt82FoundRevealBuilt = PT82RevealKind(pt82Foundation);",
            'xsChatData("<YELLOW>PT82 G3W: the part-built foundation reads reveal kind "'
            ' + pt82FoundRevealBuilt + ", where 1 is the footprint grid.");',
        )),
        (35, (
            'xsChatData("<YELLOW>PT82 G3W: a finished Jin Wonder is going up well clear of the"'
            ' + " first. Its countdown should arm within a second.");',
        )),
        (45, (
            "pt82WonderSlotArmed = PT82Slot(pt82Wonder);",
            "pt82WonderRevealArmed = PT82RevealKind(pt82Wonder);",
            "pt82WonderCounting = PT82Counting(pt82Wonder);",
            "pt82WonderYearsArmed = PT82Years(pt82WonderSlotArmed);",
            'xsChatData("<YELLOW>PT82 G3W: the finished Wonder holds slot "'
            ' + pt82WonderSlotArmed + " with reveal kind " + pt82WonderRevealArmed'
            ' + ", counting " + pt82WonderCounting + " and "'
            ' + pt82WonderYearsArmed + " years on its timer.");',
        )),
    ),
    shorten=(
        (50, (
            "pt82Shortened = PT82Slot(pt82Wonder);",
            "if (pt82Shortened >= 0) {",
            '    xsDisplayTimer(pt82Shortened, "<RED>Shortened Jin Wonder <TIMER>", 3,'
            " cTimerUnitYears, true, -1);",
            '    xsChatData("<RED>PT82 G3W: slot " + pt82Shortened + " rewritten to three years."'
            ' + " Expiry must defeat P1.");',
            "} else {",
            '    xsChatData("<RED>PT82 G3W: the Wonder holds no countdown slot, so there is'
            ' nothing to shorten.");',
            "}",
        )),
    ),
    probes=(
        Probe("foundation_alive", "PT82Bool(xsDoesUnitExist(pt82Foundation))"),
        Probe("wonder_alive", "PT82Bool(xsDoesUnitExist(pt82Wonder))"),
        Probe("p4_wonders", "PT82Count(4, 276)"),
        Probe("foundation_slot_idle", "pt82FoundSlotIdle", None,
              "latched five seconds after the foundation appeared and before any build"
              " points: -1 is #84 unfixed, the foundation never reaching a slot at all", -1),
        Probe("foundation_reveal_idle", "pt82FoundRevealIdle", 0,
              "0 is no reveal. A foundation nobody has started on renders no construction site,"
              " so a reveal there would light empty ground"),
        Probe("foundation_begun", "pt82FoundBegun", 1,
              "xsSetUnitBuildPoints accepted 10% of cTrainTime; 0 means the part-built readings"
              " below mean nothing"),
        Probe("foundation_reveal_built", "pt82FoundRevealBuilt", 1,
              "latched ten seconds after construction began: 1 is the footprint grid, which"
              " is what TickWonderSlot lays once build points rise"),
        Probe("foundation_years", "PT82Years(PT82Slot(pt82Foundation))", None,
              "recorded only: an un-armed slot reads whatever the engine left in that timer,"
              " so the absence of a countdown is the eye\'s call, not this number\'s"),
        Probe("wonder_slot_armed", "pt82WonderSlotArmed", None,
              "latched ten seconds after the finished Wonder appeared", -1),
        Probe("wonder_reveal_armed", "pt82WonderRevealArmed", 2,
              "2 is the radius-9 circle. The grid is for foundations; a Wonder that is standing"
              " is what the countdown is about, so it keeps the generous view"),
        Probe("wonder_counting", "pt82WonderCounting", 1,
              "the other half of criterion 5: wonderSlotCounting is set by StartWonderCountdown"
              " and by nothing else, so 1 is the countdown armed. The circle alone does not"
              " prove it - RevealWonderSlot lays that before StartWonderCountdown is reached"),
        Probe("wonder_years_armed", "pt82WonderYearsArmed", None,
              "recorded only: THREAT_BASE_YEARS is 200 before the Hun bonus is applied"),
        Probe("shortened_slot", "pt82Shortened", None, "-1 unless built with --shorten"),
    ),
    look=(
        "Nothing lights up when the foundation appears. It has no build points, so the game"
        " renders no construction site and there is nothing to show.",
        "Fifteen seconds later the fork drives it to 10% built. A patch the size of the"
        " construction site lights up then - the site lit to its fence, solid black a tile"
        " beyond - and a top-panel message names the Jin and says they have begun a Wonder.",
        "No countdown arms for the foundation: a foundation is not a complete Wonder.",
        "The finished Wonder arms a timer that reads \'<colour>Jin Wonder\' and starts near 200"
        " years, under a far wider patch of lifted fog than the foundation\'s - four"
        " THREAT_REVEAL_RADIUS revealers in a block at its centre, so the light sits on"
        " the building rather than beside it.",
        "Destroy it: the timer and its objective line disappear and the fog around it closes.",
        "Run again with --shorten to watch expiry defeat P1 without waiting 200 years.",
    ),
    caveats=(
        "--shorten rewrites the armed timer to a few years with xsDisplayTimer. It proves that"
        " expiry calls LoseToThreat; it does not prove the engine counts 200 years correctly.",
        "A slot is only looked up through PT82Slot, which answers -1 for a unit that never"
        " placed. FindWonderSlot(-1) returns the first *free* slot, which is how TrackWonder"
        " allocates, so asking it directly about a failed creation would name somebody else\'s"
        " countdown.",
        "The Jin keep nine Blacksmiths in a 3x3 grid at x 122/125/128 by y 165/168/171 - three"
        " tiles apart, which is a Blacksmith\'s own footprint. That block is the plot the AI"
        " builds its Wonder on once it is cleared, so the fork removes those nine and puts the"
        " foundation at its centre. The tenth Blacksmith, ref 9959, is outside the block and"
        " stays.",
        "The two Wonders stand about forty tiles apart because the Jin town has no clear flat"
        " ground any nearer: the finished one carries a block of THREAT_REVEAL_RADIUS"
        " revealers reaching eight or so tiles, the foundation a patch reaching about"
        " three, so anything closer would have the two read as one lit area and the first"
        " check would be unreadable.",
        "Genghis 3 arms the Wonder threat for player 4 only, and the Jin own no Wonder of their"
        " own, so the two created here take slots 0 and 1 in that order.",
        "The Jin are an AI player, and a foundation on their own plot is theirs to finish."
        " Their villagers working on it ahead of the fork reads as a failing probe for the"
        " right behaviour: foundation_reveal_idle goes to 1 if they start it before tick 10,"
        " and foundation_reveal_built goes to 2 if they finish it before tick 30. Both are the"
        " mod working. The idle reading is latched five seconds after the foundation appears"
        " to keep the first window as short as the 1 Hz watch allows.",
        "Construction is started with xsSetUnitBuildPoints, not by a villager, which is the only"
        " way XS can begin a building. What a player\'s own untouched foundation does before a"
        " villager reaches it is unstageable at either layer; the reveal waits on build points"
        " either way, so the worst case is a reveal that arrives late rather than one that never"
        " arrives.",
        "Neither alive probe carries an expectation, because the look asks the player to"
        " destroy the finished Wonder. A creation that never placed is caught by the two slot"
        " probes, which forbid -1, and by PT82CreateNear's own red chat line.",
        "A Wonder occupies 6x6 tiles, measured in game. THREAT_FOUNDATION_ROWS is the 4 rows of"
        " line-of-sight 1 revealers that covers it, settled by eye over several runs of #84 and"
        " not derived from the dat - 2 x collision_size_x gives 5, and it is wrong for this one"
        " building.",
    ),
)


A6W = Fork(
    key="A6W",
    fork_id=6,
    source="AP_Attila_6",
    scenario_id=106,
    title="Attila 6: defeating Aquileia clears its Wonder countdown",
    checks=("#60",),
    creates=(
        Create("pt82WonderP2", WONDER, 2, False,
               search=(211, 19, 221, 29), prefer=(216, 24), tick=6),
    ),
    unit_pins=((1154, TOWN_CENTER, 2),),
    trigger_pins=("P2 has a wonder", "AP Defeat Aquileia"),
    globals=(("pt82Defeated", "0"), ("pt82SlotBefore", "-1"), ("pt82YearsBefore", "-1")),
    stage=(
        (6, (
            'xsChatData("<YELLOW>PT82 A6W: a finished Wonder is going up for Aquileia (P2, Red)."'
            ' + " Let its countdown arm.");',
        )),
        (38, (
            "pt82SlotBefore = PT82Slot(pt82WonderP2);",
            "pt82YearsBefore = PT82Years(pt82SlotBefore);",
            'xsChatData("<YELLOW>PT82 A6W: slot " + pt82SlotBefore + " reads " + pt82YearsBefore'
            ' + " years. Aquileia falls in two seconds.");',
        )),
        (40, (
            "pt82Defeated = 1;",
            "xsDeclareVictory(2, false);",
            'xsChatData("<YELLOW>PT82 A6W: Aquileia is defeated. The Wonder still stands."'
            ' + " The countdown must not.");',
        )),
    ),
    probes=(
        Probe("wonder_alive", "PT82Bool(xsDoesUnitExist(pt82WonderP2))", 1,
              "the Wonder must outlive the city"),
        Probe("p2_in_game", "PT82Bool(xsGetPlayerInGame(2))", 0),
        Probe("defeated", "pt82Defeated", 1),
        Probe("slot_before_defeat", "pt82SlotBefore", None, "0 or above means it was counting"),
        Probe("years_before_defeat", "pt82YearsBefore"),
        Probe("wonder_slot_now", "PT82Slot(pt82WonderP2)", -1,
              "the slot must be released although the Wonder stands"),
        Probe("wonder_years_now", "PT82Years(PT82Slot(pt82WonderP2))", -1),
        Probe("loc_10603_defeat_aquileia", "PT82Bool(IsScenarioLocationComplete(10603))", 1,
              "P2 Red; AP Defeat Aquileia fires on player_defeated"),
        Probe("loc_10609_red_wonder", "PT82Bool(IsScenarioLocationComplete(10609))", 1,
              "the same effect sends this one: prevent or destroy"),
        Probe("loc_10601_defeat_patavium", "PT82Bool(IsScenarioLocationComplete(10601))", 0,
              "P5 Purple; untouched"),
        Probe("loc_10602_defeat_mediolanum", "PT82Bool(IsScenarioLocationComplete(10602))", 0,
              "P3 Green; untouched"),
        Probe("loc_10604_defeat_verona", "PT82Bool(IsScenarioLocationComplete(10604))", 0,
              "P4 Orange; untouched"),
        Probe("loc_10607_purple_wonder", "PT82Bool(IsScenarioLocationComplete(10607))", 0),
        Probe("loc_10608_green_wonder", "PT82Bool(IsScenarioLocationComplete(10608))", 0),
        Probe("loc_10610_orange_wonder", "PT82Bool(IsScenarioLocationComplete(10610))", 0),
        Probe("loc_10611_purple_wonder_2", "PT82Bool(IsScenarioLocationComplete(10611))", 0),
    ),
    look=(
        "A Wonder finishes for Aquileia and its countdown arms.",
        "At forty seconds Aquileia is defeated outright while the Wonder is still standing.",
        "The countdown and its objective line must go, although the building has not fallen.",
        "Aquileia's Defeat and Red Wonder locations must both credit; the other seven must not.",
    ),
    caveats=(
        "Attila 6's cities are P2 Aquileia (Red), P3 Mediolanum (Green), P4 Verona (Orange) and"
        " P5 Patavium (Purple). P6 is the Western Roman Empire (Blue).",
        "The Wonder goes at (216,24), which is where the scenario's own 'Red Constructs Wonder'"
        " trigger places P2's foundation. The other designated plots are (33,55) for Green,"
        " (136,178) for Orange and (123,72) and (129,78) for Purple's two.",
        "'Prevent or destroy' is one effect, not two paths: AP Defeat Aquileia is a single"
        " player_defeated condition whose script_call runs DefeatAquileia() and"
        " DestroyRedWonder() together. That is why both locations are asserted.",
        "P2 is defeated with xsDeclareVictory rather than by being fought down, which is the only"
        " way to take a player out of the game on cue. What the mod reads is xsGetPlayerInGame,"
        " and the scenario reads player_defeated; both are the same either way.",
    ),
)

J4M = Fork(
    key="J4M",
    fork_id=7,
    source="AP_Joan_4",
    scenario_id=204,
    title="Joan 4: the train menu offers the base tier, not the upgrade",
    checks=("#74",),
    items=(SKIRMISHER_LINE, GALLEY_LINE, DEMOLITION_LINE,
           ELITE_SKIRMISHER_TECH, WAR_GALLEY_TECH, DEMOLITION_SHIP_TECH),
    reveal=((87, 114, 14),),
    creates=(
        Create("pt82Range", ARCHERY_RANGE, 1, False,
               search=(82, 112, 98, 128), prefer=(91, 118)),
        Create("pt82Dock", DOCK, 1, False,
               search=(80, 108, 96, 116), prefer=(88, 112),
               terrain=BEACH, needs_water=True),
    ),
    recipe_ops=(
        {"op": "move_units_in_area", "target_player": 1,
         "target_area_x1": 80, "target_area_y1": 124,
         "target_area_x2": 88, "target_area_y2": 135,
         "target_x": 82, "target_y": 115},
    ),
    probes=(
        Probe("range_alive", "PT82Bool(xsDoesUnitExist(pt82Range))", 1),
        Probe("dock_alive", "PT82Bool(xsDoesUnitExist(pt82Dock))", 1),
        Probe("castle_age", "PT82Bool(ageReached(CASTLE_AGE))", 1),
        Probe("elite_skirmisher_tech", "xsGetTechState(98, 1)", forbid=3,
              note="3 is Done; the check needs it unresearched"),
        Probe("war_galley_tech", "xsGetTechState(34, 1)", forbid=3,
              note="3 is Done; the check needs it unresearched"),
        Probe("demolition_ship_tech", "xsGetTechState(905, 1)", forbid=3,
              note="3 is Done; the check needs it unresearched"),
    ),
    look=(
        "The Archery Range offers Skirmisher, not Elite Skirmisher.",
        "The Dock offers Galley and Demolition Raft, not War Galley and Demolition Ship.",
        "Elite Skirmisher, War Galley and Demolition Ship each sit on the building as a research"
        " button that has not been researched.",
        "The Barracks, if one is reachable, still offers Militia and Spearman: the control.",
    ),
    caveats=(
        "The sidecar records each upgrade tech's state (2 is available, 3 is done). A 3 here"
        " would mean the research ran and the check is reading the wrong thing.",
        "XS cannot read whether an object is enabled, which is why this one is an eye at all.",
        "The Archery Range and the Dock are placed on tiles the build picks out of the patched"
        " scenario, after P1's army has been moved, so they cannot land under it. Building"
        " footprints in FOOTPRINT are measured in game; 2 x collision_size_x gives 5 for a"
        " Wonder and the real footprint is 6.",
    ),
)

FORKS = (J3B, A3G, J5V, J6S, G3W, A6W, J4M)
BY_KEY = {fork.key: fork for fork in FORKS}
BY_ID = {fork.fork_id: fork for fork in FORKS}

MAGIC = 424282
FOOTER = 424242
HEADER_FIELDS = ("magic", "fork_id", "scenario_id", "slot_id", "unitsanity", "techsanity",
                 "caveman", "game_time", "tick", "probe_count")

REQUIRED_SEED = {"AP_US_MODE": 2, "AP_TS_MODE": 3, "AP_US_CAVEMAN": 1}
