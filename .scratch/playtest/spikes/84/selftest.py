import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

RECORDS = 256
FIELDS = 8

REC_BOOT, REC_DONE = 1, 10
REC_FSETUP, REC_FDEF, REC_FUNIT = 18, 19, 20
REC_FSLOT, REC_FSCAN, REC_FCOUNT, REC_FPOS = 21, 22, 23, 24
REC_FGAP, REC_FWONDERS = 25, 26
REC_FREVEAL = 27

WONDER = 276
QUERY_IDS = [WONDER, 903, 960, 1256, -1]
ALL_UNITS = -1

FOUNDATION, COMPLETED = 0, 1
FOUNDATION_ID, COMPLETED_ID = 4211, 4212
TRAIN_TIME = 3503
SCENARIO_FOUNDATIONS = 1


def encode_string(text):
    raw = text.encode("utf-8")
    return struct.pack("<I", len(raw)) + raw


def encode_int(value):
    return struct.pack("<i", value)


def good_records(foundation_seen_by=(), collision_x100=250, control_enumerates=True,
                 foundation_complete=0, control_complete=1, revealer=991,
                 foundation_slot=2, object_count_total_sees_it=True,
                 counter_route_works=True, scenario_foundations=SCENARIO_FOUNDATIONS,
                 all_units_finds_foundations=True, reveal_waits=True, owner_alive=True,
                 begun_gets_grid=True,
                 foundation_id=FOUNDATION_ID):
    rows = []

    def add(kind, a=0, b=0, c=0, d=0, e=0):
        rows.append((kind, len(rows), len(rows), a, b, c, d, e))

    add(REC_BOOT, 2, 1, 3, 107, 3)
    add(REC_FSETUP, 0, foundation_id, -1, 5, 2)
    add(REC_FDEF, collision_x100, collision_x100, 250, 250, TRAIN_TIME)

    for tag in (1, 2, 3, 4, 5):
        standing = [] if tag == 5 else [FOUNDATION]
        if tag >= 2:
            standing.append(COMPLETED)

        progress = {1: 0, 2: 0, 3: 350, 4: 350, 5: TRAIN_TIME}[tag]
        points = {FOUNDATION: progress, COMPLETED: TRAIN_TIME}
        complete = {FOUNDATION: foundation_complete if tag < 5 else 1,
                    COMPLETED: control_complete}
        for which, unit_id in ((FOUNDATION, foundation_id), (COMPLETED, COMPLETED_ID)):
            if which not in standing and not (which == FOUNDATION and tag == 5):
                add(REC_FUNIT, tag, which, 0, -1, -1)
                add(REC_FSLOT, tag, which, -1, -1, -1)
                add(REC_FPOS, tag, which, -1, -1, 0)
                add(REC_FREVEAL, tag, which, -1, -1, -1)
                continue
            add(REC_FUNIT, tag, which, 1, WONDER, points[which])
            held = foundation_slot if which == FOUNDATION else 0
            if which == FOUNDATION:
                kind = 0
                if points[which] >= TRAIN_TIME:
                    kind = 2
                elif points[which] > 0:
                    kind = 1 if begun_gets_grid else 2
                if not reveal_waits and points[which] == 0:
                    kind = 2
            else:
                kind = 2
            add(REC_FREVEAL, tag, which, held, kind, points[which])
            add(REC_FSLOT, tag, which, held, complete[which], 2)
            add(REC_FPOS, tag, which, 120 + which * 12, 140, 0)

        for query_id in QUERY_IDS:
            holds_foundation = 1 if (query_id in foundation_seen_by and tag < 5) else 0
            holds_completed = 0
            if tag >= 2 and (query_id != WONDER or control_enumerates):
                holds_completed = 1
            size = holds_foundation + holds_completed
            if query_id == 1256:
                size = -1
            add(REC_FSCAN, tag, query_id, size, holds_foundation, holds_completed)

        standing_count = {1: 0, 2: 1, 3: 1, 4: 1, 5: 2}[tag]
        pending = {1: 1, 2: 1, 3: 1, 4: 2, 5: 1}[tag]
        if not object_count_total_sees_it:
            pending = 0
        if not counter_route_works:
            pending = 1
        total = scenario_foundations + standing_count + pending
        add(REC_FCOUNT, tag, standing_count, total, standing_count, -1)
        add(REC_FGAP, tag, total - standing_count, 0, 1 if owner_alive else 0, 12)
        filtered = total if all_units_finds_foundations else standing_count
        add(REC_FWONDERS, tag, filtered, 20 + total, 0, 0)

        if tag == 2:
            add(REC_FSETUP, 2, revealer, 0, 0, 0)
        if tag == 3:
            add(REC_FSETUP, 5, 4301, 7, 4302, 1)
        if tag == 4:
            add(REC_FSETUP, 3, 1, TRAIN_TIME, 0, 0)

    add(REC_DONE, 14, len(rows), 0, 0, 0)
    return rows


def build(path, rows, version=2, magic=424242):
    body = []
    for row in rows:
        body.extend(row)
    body.extend([0] * (RECORDS * FIELDS - len(body)))

    blob = encode_string("AP78") + encode_int(version) + encode_int(RECORDS)
    for value in body[:RECORDS * FIELDS]:
        blob += encode_int(value)
    blob += encode_string("")
    blob += encode_string("")
    blob += encode_string("END")
    blob += encode_int(len(rows))
    blob += encode_int(magic)
    path.write_bytes(blob)


def run(path):
    proc = subprocess.run([sys.executable, str(HERE / "read.py"), str(path)],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def main():
    temp = Path(tempfile.mkdtemp(prefix="ap84-selftest-"))
    failures = 0

    good = temp / "good.xsdat"
    build(good, good_records())
    code, out = run(good)
    if code != 0:
        failures += 1
        print("FAIL: a known-good run did not pass")
        print(out)
    else:
        print("ok: a known-good run passes")
        print("    " + out.strip().splitlines()[-1])

    verdicts = [
        ("no query sees the foundation", {},
         "an object-id scan cannot find a Wonder that is still a foundation"),
        ("the building class sees it", {"foundation_seen_by": (903,)},
         "xsGetPlayerUnitIds(2, cBuildingClass)"),
        ("the object-id scan sees it", {"foundation_seen_by": (WONDER,)},
         "ScanOwnerWonders can be repointed"),
        ("only the all-units scan sees it", {"foundation_seen_by": (ALL_UNITS,)},
         "xsGetPlayerUnitIds(2, -1)"),
        ("the foundation was tracked into a slot", {"foundation_slot": 3},
         "put the foundation in slot 3"),
        ("a scenario with no pre-placed foundation", {"scenario_foundations": 0},
         "an object-id scan cannot find a Wonder that is still a foundation"),
    ]
    for label, kwargs, expect in verdicts:
        path = temp / "verdict.xsdat"
        build(path, good_records(**kwargs))
        code, out = run(path)
        if code != 0:
            failures += 1
            print(f"FAIL: {label} did not pass its checks")
            continue
        if expect is not None and expect not in out:
            failures += 1
            print(f"FAIL: {label} did not produce its verdict line")
            continue
        if expect is None and "does count it" in out:
            failures += 1
            print(f"FAIL: {label} still claimed the engine counts the foundation")
            continue
        print(f"ok: {label} -> the right verdict")

    faults = [
        ("the case never ran", {"records": []}),
        ("the control Wonder is not enumerable", {"control_enumerates": False}),
        ("the foundation already reads as complete", {"foundation_complete": 1}),
        ("the control Wonder reads as incomplete", {"control_complete": 0}),
        ("cUnitSizeX disagrees with the dat", {"collision_x100": 200}),
        ("the foundation was never created", {"foundation_id": -1}),
        ("objectCountTotal does not count foundations either",
         {"object_count_total_sees_it": False}),
        ("the counter gap never moves", {"counter_route_works": False}),
        ("the all-units scan misses foundations too",
         {"all_units_finds_foundations": False}),
        ("the foundation is never tracked, the original bug", {"foundation_slot": -1}),
        ("an untouched foundation is revealed anyway", {"reveal_waits": False}),
        ("a part-built foundation gets the radius-10 circle", {"begun_gets_grid": False}),
        ("the Wonder's owner is defeated mid-run", {"owner_alive": False}),
    ]
    for label, kwargs in faults:
        path = temp / "bad.xsdat"
        rows = kwargs.pop("records", None)
        build(path, good_records(**kwargs) if rows is None else rows)
        code, out = run(path)
        if code == 0:
            failures += 1
            print(f"FAIL: {label} was not caught")
        else:
            caught = [line for line in out.splitlines() if line.startswith("[FAIL]")]
            print(f"ok: {label} caught -> {len(caught)} failing row(s)")

    for label, kwargs in [("a run from before the probe", {"version": 1}),
                          ("a run that never closed its file", {"magic": 0})]:
        path = temp / "stale.xsdat"
        build(path, good_records(), **kwargs)
        code, out = run(path)
        if code != 2:
            failures += 1
            print(f"FAIL: {label} was not rejected outright")
        else:
            print(f"ok: {label} rejected outright")

    print()
    if failures:
        print(f"{failures} selftest failure(s)")
        return 1
    print("selftest passed: the reader accepts a good run, reaches the right verdict on each")
    print("detection outcome, and rejects every seeded fault")
    return 0


if __name__ == "__main__":
    sys.exit(main())
