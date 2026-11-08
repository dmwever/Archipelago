import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILE = Path(os.environ.get(
    "AOE2_PROFILE",
    r"C:\Users\dmwev\Games\Age of Empires 2 DE\76561199655318799\profile"))

RECORDS = 256
FIELDS = 8

REC_DONE = 10
REC_FSETUP, REC_FDEF, REC_FUNIT = 18, 19, 20
REC_FSLOT, REC_FSCAN, REC_FCOUNT, REC_FPOS = 21, 22, 23, 24
REC_FGAP = 25
REC_FWONDERS = 26
REC_FREVEAL = 27

WONDER = 276
BUILDING_CLASS = 903
MISC_BUILDING_CLASS = 960
FLAG_CLASS_BUILDING = 1256
ALL_UNITS = -1

QUERIES = [
    (WONDER, "xsGetPlayerUnitIds(2, WONDER)"),
    (BUILDING_CLASS, "xsGetPlayerUnitIds(2, cBuildingClass)"),
    (MISC_BUILDING_CLASS, "xsGetPlayerUnitIds(2, cMiscBuildingClass)"),
    (FLAG_CLASS_BUILDING, "xsGetPlayerUnitIds(2, cFlagClassBuilding)"),
    (ALL_UNITS, "xsGetPlayerUnitIds(2, -1)  [every unit, then filtered]"),
]

FOUNDATION, COMPLETED = 0, 1
WHICH = {FOUNDATION: "foundation", COMPLETED: "completed"}

STAGES = {
    0: "baseline, nothing created yet",
    1: "foundation alone",
    2: "+ a completed Wonder beside it",
    3: "+ the first foundation 10% built",
    4: "+ a second, untouched foundation",
    5: "+ build points driven to full",
}

WONDER_COLLISION_X100 = 250
WONDER_FOOTPRINT_TILES = 6

results = []


def check(name, ok, detail):
    results.append((name, "PASS" if ok else "FAIL", detail))


class WrongSidecar(Exception):
    pass


class Cursor:
    def __init__(self, blob):
        self.blob = blob
        self.pos = 0

    def take_int(self):
        if self.pos + 4 > len(self.blob):
            raise WrongSidecar(f"the file stops at {len(self.blob)} bytes, mid-record")
        value = struct.unpack_from("<i", self.blob, self.pos)[0]
        self.pos += 4
        return value

    def take_string(self):
        if self.pos + 4 > len(self.blob):
            raise WrongSidecar(f"the file stops at {len(self.blob)} bytes, mid-string")
        length = struct.unpack_from("<I", self.blob, self.pos)[0]
        if self.pos + 4 + length > len(self.blob):
            raise WrongSidecar(f"the file stops at {len(self.blob)} bytes, mid-string")
        self.pos += 4
        text = self.blob[self.pos:self.pos + length].decode("utf-8", "replace")
        self.pos += length
        return text


def records(path):
    cursor = Cursor(path.read_bytes())
    header = cursor.take_string()
    if header != "AP78":
        raise WrongSidecar(
            f"header is {header!r}, not 'AP78' - this sidecar is from another harness")
    version = cursor.take_int()
    if version < 2:
        raise WrongSidecar(
            f"the harness wrote format version {version}; the #84 case needs version 2 or later,"
            " so this run predates the probe")
    declared = cursor.take_int()
    body = [cursor.take_int() for _ in range(declared * FIELDS)]

    for _ in range(8):
        if cursor.take_string() == "END":
            break
    else:
        raise WrongSidecar("no END marker - the run ended before it closed the file")
    written = cursor.take_int()
    magic = cursor.take_int()
    if magic != 424242:
        raise WrongSidecar(f"footer is {magic}, not 424242 - the run did not finish")

    rows = []
    for n in range(min(written, declared)):
        kind, tick, gtime, a, b, c, d, e = body[n * FIELDS:(n + 1) * FIELDS]
        rows.append({"kind": kind, "tick": tick, "time": gtime, "v": (a, b, c, d, e)})
    return rows, written


def first(rows, kind, predicate=None):
    for row in rows:
        if row["kind"] == kind and (predicate is None or predicate(row["v"])):
            return row
    return None


def unit(rows, tag, which):
    return first(rows, REC_FUNIT, lambda v: v[0] == tag and v[1] == which)


def slot(rows, tag, which):
    return first(rows, REC_FSLOT, lambda v: v[0] == tag and v[1] == which)


def scan(rows, tag, query_id):
    return first(rows, REC_FSCAN, lambda v: v[0] == tag and v[1] == query_id)


def counts(rows, tag):
    return first(rows, REC_FCOUNT, lambda v: v[0] == tag)


REVEAL = {-1: "-", 0: "none", 1: "footprint grid", 2: "wonder block"}


def reveal(rows, tag, which):
    return first(rows, REC_FREVEAL, lambda v: v[0] == tag and v[1] == which)


def wonders(rows, tag):
    return first(rows, REC_FWONDERS, lambda v: v[0] == tag)


def gap(rows, tag):
    return first(rows, REC_FGAP, lambda v: v[0] == tag)


def setup(rows, tag):
    return first(rows, REC_FSETUP, lambda v: v[0] == tag)


def stages_present(rows):
    return sorted({row["v"][0] for row in rows if row["kind"] == REC_FUNIT})


def check_run(rows, written):
    created = setup(rows, 0)
    done = first(rows, REC_DONE)
    if created is None:
        check("the #84 case ran at all", False,
              "no REC_FSETUP record - Test.xs did not reach CASE_FOUNDATION")
        return False
    foundation_id = created["v"][1]
    check("the #84 case ran and closed the file", done is not None,
          f"{written} records written")
    check("xsCreateUnit placed a Wonder foundation for P2", foundation_id >= 0,
          f"foundation unit id {foundation_id}")
    control = unit(rows, 2, COMPLETED)
    check("xsCreateUnit placed the completed control Wonder for P2",
          control is not None and control["v"][2] == 1,
          f"build points {control['v'][4]} at stage 2" if control is not None
          else "no stage 2 record - the control never existed")
    return foundation_id >= 0


def check_definition(rows):
    row = first(rows, REC_FDEF)
    if row is None:
        check("the Wonder's footprint is readable from XS", False, "no REC_FDEF record")
        return
    size_x, size_y, clear_x, clear_y, train = row["v"]
    check("cUnitSizeX reads the Wonder's collision radius, 2.5 tiles",
          size_x == WONDER_COLLISION_X100 and size_y == WONDER_COLLISION_X100,
          f"cUnitSizeX={size_x / 100} cUnitSizeY={size_y / 100}"
          f" - the dat agrees, but 2 x collision_size_x is NOT the tile footprint:"
          f" a Wonder occupies {WONDER_FOOTPRINT_TILES}x{WONDER_FOOTPRINT_TILES} tiles,"
          " measured in game 2026-11-07")
    check("cTrainTime is the build points a finished Wonder reaches", train > 0,
          f"cTrainTime={train}, cClearanceSizeX={clear_x / 100}"
          f" cClearanceSizeY={clear_y / 100}")


def check_completeness(rows):
    foundation = slot(rows, 1, FOUNDATION)
    points = unit(rows, 1, FOUNDATION)
    if foundation is None or points is None:
        check("the foundation reads as incomplete", False, "stage 1 records missing")
    else:
        check("the foundation reads as incomplete",
              foundation["v"][3] == 0,
              f"IsWonderComplete={foundation['v'][3]}, buildPoints={points['v'][4]}")
    control = slot(rows, 2, COMPLETED)
    control_points = unit(rows, 2, COMPLETED)
    if control is None or control_points is None:
        check("the control Wonder reads as complete", False, "stage 2 records missing")
    else:
        check("the control Wonder reads as complete", control["v"][3] == 1,
              f"IsWonderComplete={control['v'][3]}, buildPoints={control_points['v'][4]}")


def check_counter_route(rows):
    born, grown, done = counts(rows, 3), counts(rows, 4), counts(rows, 5)
    if born is None or grown is None or done is None:
        check("a new foundation moves only xsGetObjectCountTotal", False,
              "stage 3, 4 or 5 count record missing")
        return
    standing, total = grown["v"][1] - born["v"][1], grown["v"][2] - born["v"][2]
    check("a new foundation moves only xsGetObjectCountTotal",
          standing == 0 and total == 1,
          f"xsGetObjectCount {standing:+d}, xsGetObjectCountTotal {total:+d}"
          " (WatchOwnerFoundations reads the gap between them)")
    standing, total = done["v"][1] - grown["v"][1], done["v"][2] - grown["v"][2]
    check("a finished foundation moves only xsGetObjectCount",
          standing == 1 and total == 0,
          f"xsGetObjectCount {standing:+d}, xsGetObjectCountTotal {total:+d}"
          " (so the gap closes again and the warning does not repeat)")

    rows_all = [(tag, wonders(rows, tag), counts(rows, tag)) for tag in sorted(STAGES)]
    rows_all = [(tag, w, c) for tag, w, c in rows_all if w is not None and c is not None]
    if rows_all:
        series = " ".join(f"{tag}:{w['v'][1]}/{c['v'][2]}" for tag, w, c in rows_all)
        agrees = all(w["v"][1] == c["v"][2] for _, w, c in rows_all)
        check("the all-units scan, filtered by object id, finds every Wonder including "
              "foundations", agrees,
              f"filtered count / xsGetObjectCountTotal by stage: {series}"
              + ("" if agrees else "  [the filtered scan misses some]"))

    readings = [(tag, gap(rows, tag), counts(rows, tag)) for tag in sorted(STAGES)]
    readings = [(tag, g, c) for tag, g, c in readings if g is not None and c is not None]
    if not readings:
        return
    agrees = all(g["v"][1] == c["v"][2] - c["v"][1] for _, g, c in readings)
    series = " ".join(f"{tag}:{g['v'][1]}" for tag, g, _ in readings)
    check("CountOwnerFoundations is the gap between the two counters", agrees,
          f"the shipped function read {series} by stage")
    rises = [tag for (tag, g, _), (_, prev, _) in zip(readings[1:], readings)
             if g["v"][1] > prev["v"][1]]
    check("the gap rises when a foundation is laid, which is what fires the warning",
          bool(rises), f"rose at stage(s) {rises}" if rises else "never rose")
    mine = [g["v"][2] for _, g, _ in readings]
    check("an unarmed player's gap stays at zero", set(mine) == {0},
          f"P1 read {mine} - nothing is announced for a player with no Wonder under way")

    alive = [(tag, g["v"][3], g["v"][4]) for tag, g, _ in readings]
    if any(flag not in (0, 1) for _, flag, _ in alive):
        return
    lost = [tag for tag, flag, _ in alive if flag == 0]
    check("the Wonder's owner stays in the game", not lost,
          "xsGetPlayerInGame(2) / that player's total object count by stage: "
          + " ".join(f"{tag}:{flag}/{count}" for tag, flag, count in alive)
          + ("" if not lost else
             f"  [P2 drops out at stage {lost[0]} - WonderThreatWatch then calls"
             " RetireWonderOwner, which disarms the owner and releases every slot, so nothing"
             " is tracked from that point on and the engine razes what P2 owned]"))



def check_reveal_waits(rows):
    seen = [(tag, reveal(rows, tag, FOUNDATION)) for tag in sorted(STAGES)]
    seen = [(tag, row) for tag, row in seen if row is not None and row["v"][2] >= 0]
    if not seen:
        check("the reveal waits until the Wonder is actually being built", False,
              "no stage recorded the foundation in a slot")
        return
    series = " ".join(f"{tag}:{row['v'][4]}pts/{REVEAL.get(row['v'][3], row['v'][3])}"
                      for tag, row in seen)
    idle = [row["v"][3] for _, row in seen if row["v"][4] == 0]
    check("an untouched foundation carries no reveal", all(k == 0 for k in idle),
          f"build points / reveal by stage: {series}")
    begun = [row["v"][3] for _, row in seen if 0 < row["v"][4] < 3500]
    check("a foundation under construction carries the footprint grid, not the circle",
          bool(begun) and all(k == 1 for k in begun),
          f"reveal while part-built: {[REVEAL.get(k, k) for k in begun]}"
          if begun else "no stage caught it part-built")
    done = [row["v"][3] for _, row in seen if row["v"][4] >= 3500]
    check("a completed Wonder swaps to the wide completed-Wonder reveal",
          bool(done) and all(k == 2 for k in done),
          f"reveal once complete: {[REVEAL.get(k, k) for k in done]}"
          if done else "no stage caught it complete")


def check_foundation_is_tracked(rows):
    held = [(tag, slot(rows, tag, FOUNDATION)) for tag in (1, 2, 3, 4)]
    held = [(tag, row) for tag, row in held if row is not None and row["v"][3] == 0]
    if not held:
        check("the mod tracks a Wonder while it is still a foundation", False,
              "no stage recorded the first foundation as incomplete")
        return
    slots = {tag: row["v"][2] for tag, row in held}
    tracked = [tag for tag, taken in slots.items() if taken >= 0]
    check("the mod tracks a Wonder while it is still a foundation", bool(tracked),
          f"FindWonderSlot on the foundation by stage: {slots}"
          + ("" if tracked else "  [-1 throughout: ScanOwnerFoundations did not reach it,"
                                " which is the #84 bug unfixed]"))


def check_control_enumerates(rows):
    row = scan(rows, 2, WONDER)
    if row is None:
        check("the completed Wonder is enumerated by object id", False,
              "stage 2 scan record missing")
        return
    check("the completed Wonder is enumerated by object id", row["v"][4] == 1,
          f"xsGetPlayerUnitIds(2, WONDER) size={row['v'][2]}, holds the completed Wonder="
          f"{row['v'][4]}"
          + ("" if row["v"][4] == 1 else "  [INVALID RUN: the control is not enumerable either,"
                                         " so nothing can be concluded about the foundation]"))


def answer(rows):
    print("the question: does any XS query see a Wonder FOUNDATION?")
    print()
    for query_id, label in QUERIES:
        print(f"  {label}")
        print(f"  {'stage':<43}  {'size':>6}  {'foundation':>11}  {'completed':>10}")
        for tag in sorted(STAGES):
            row = scan(rows, tag, query_id)
            if row is None:
                continue
            size = row["v"][2]
            size_text = "refused" if size < 0 else str(size)
            print(f"    {STAGES[tag]:<41}  {size_text:>6}  {str(row['v'][3]):>11}"
                  f"  {str(row['v'][4]):>10}")
        print()

    print("  xsGetObjectCount vs xsGetObjectCountTotal, P2")
    print("  what matters is the step between rows, not the absolute number: the scenario's own")
    print("  pre-placed objects sit under all of them.")
    print(f"  {'stage':<43}  {'count':>6}  {'total':>6}  {'byClass':>8}  {'revealers':>9}")
    for tag in sorted(STAGES):
        row = counts(rows, tag)
        if row is None:
            continue
        print(f"    {STAGES[tag]:<41}  {row['v'][1]:>6}  {row['v'][2]:>6}"
              f"  {row['v'][3]:>8}  {row['v'][4]:>9}")
    print()

    print("  what the mod itself did with each object")
    print(f"  {'stage':<43}  {'object':<11}  {'exists':>6}  {'objectId':>8}"
          f"  {'points':>6}  {'slot':>5}")
    for tag in sorted(STAGES):
        for which in (FOUNDATION, COMPLETED):
            row, held = unit(rows, tag, which), slot(rows, tag, which)
            if row is None or held is None:
                continue
            print(f"    {STAGES[tag]:<41}  {WHICH[which]:<11}  {row['v'][2]:>6}"
                  f"  {row['v'][3]:>8}  {row['v'][4]:>6}  {held['v'][2]:>5}")
    print()

    revealer = setup(rows, 2)
    if revealer is not None:
        print(f"  xsSetUnitBuildPoints(foundation, {revealer['v'][2]}) to start construction"
              f" returned {'true' if revealer['v'][1] else 'false'}")
    finished = setup(rows, 3)
    if finished is not None:
        print(f"  xsSetUnitBuildPoints(foundation, {finished['v'][2]}) returned "
              f"{'true' if finished['v'][1] else 'false'}")
    grid = setup(rows, 5)
    if grid is not None:
        second, held, lone, los = grid["v"][1], grid["v"][2], grid["v"][3], grid["v"][4]
        print(f"  RevealFootprint ran over a second foundation (unit {second}) in slot {held};"
              f" a lone line-of-sight {los} revealer (unit {lone}) sits 20 tiles south of it")
        print("  -> an eye answers these two: is the whole construction site lit and how far")
        print("     past it does the light go, and how many tiles does the lone revealer light")
    position = first(rows, REC_FPOS, lambda v: v[0] == 1 and v[1] == FOUNDATION)
    if position is not None:
        print(f"  xsGetUnitPosition(foundation) = ({position['v'][2]}, {position['v'][3]})"
              + ("  (readable, so a reveal can be placed on it)" if position["v"][2] >= 0
                 else "  (unreadable)"))
    print()

    print("  verdict")
    seen = []
    for query_id, label in QUERIES:
        for tag in (1, 2, 3, 4):
            row = scan(rows, tag, query_id)
            if row is not None and row["v"][3] == 1:
                seen.append(label)
                break
    if seen:
        print("  these queries DID return the foundation:")
        for label in seen:
            print(f"    - {label}")
        print("  -> ScanOwnerWonders can be repointed at one of them, which gives an id and so")
        print("     a position: the footprint reveal is reachable after all.")
    else:
        print("  no query returned the foundation. The deduction in #84 is confirmed:")
        print("  an object-id scan cannot find a Wonder that is still a foundation, so the")
        print("  scenario has to say so (the place_foundation script_call route).")
    born = counts(rows, 3)
    grown = counts(rows, 4)
    if born is not None and grown is not None:
        standing = grown["v"][1] - born["v"][1]
        total = grown["v"][2] - born["v"][2]
        print(f"  creating one more foundation moved xsGetObjectCount by {standing:+d} and"
              f" xsGetObjectCountTotal by {total:+d}")
        if standing == 0 and total == 1:
            print("  -> xsGetObjectCountTotal counts foundations and xsGetObjectCount does not,")
            print("     so it detects that a Wonder is being built - but it hands back no id,")
            print("     and so no position to reveal.")
    finished_at = counts(rows, 5)
    if grown is not None and finished_at is not None:
        standing = finished_at["v"][1] - grown["v"][1]
        total = finished_at["v"][2] - grown["v"][2]
        print(f"  finishing a foundation moved xsGetObjectCount by {standing:+d} and"
              f" xsGetObjectCountTotal by {total:+d}")
    held = slot(rows, 2, FOUNDATION)
    if held is not None:
        print(f"  WonderThreatWatch put the foundation in slot {held['v'][2]}, so it carries a"
              " footprint reveal" if held["v"][2] >= 0 else
              "  WonderThreatWatch never tracked the foundation, which is the reported bug.")
    print()


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROFILE / "default1.xsdat"
    if not path.exists():
        print(f"no sidecar at {path}")
        return 2

    try:
        rows, written = records(path)
    except WrongSidecar as problem:
        print(f"sidecar {path}")
        print(f"cannot read it: {problem}")
        print()
        print("Boot XsTesting with the AP84 Test.xs, wait for the green line, quit,")
        print("then re-run this script.")
        return 2

    print(f"sidecar {path}")
    print(f"stages recorded: {stages_present(rows)}")
    print()

    if check_run(rows, written):
        check_definition(rows)
        check_completeness(rows)
        check_control_enumerates(rows)
        check_counter_route(rows)
        check_foundation_is_tracked(rows)
        check_reveal_waits(rows)
        answer(rows)

    width = max(len(name) for name, _, _ in results)
    failed = sum(1 for _, mark, _ in results if mark == "FAIL")
    for name, mark, detail in results:
        print(f"[{mark}] #84  {name.ljust(width)}  {detail}")
    print()
    print(f"{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
