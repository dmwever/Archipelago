import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

RECORDS = 256
FIELDS = 8

REC_BOOT, REC_SEED, REC_ROW, REC_CASE, REC_STAGE = 1, 2, 3, 4, 5
REC_RES, REC_COUNT, REC_LOC, REC_WONDER, REC_DONE, REC_DIAG = 6, 7, 8, 9, 10, 11
REC_TRACE = 12

UPGRADE_CASES = [(3, 548, 363), (4, 588, 376), (5, 77, 320), (6, 359, 341)]


def encode_string(text):
    raw = text.encode("utf-8")
    return struct.pack("<I", len(raw)) + raw


def encode_int(value):
    return struct.pack("<i", value)


def good_records(leitis_upgrade_item=-1, leitis_elite=10, leitis_militia=0,
                  siege_ram_location_sent=1, wonder_build_points=1000,
                  wonder_owner_in_game=1, siege_ram_pre_state=0,
                  destroyed_slot_released=True):
    rows = []

    def add(kind, a=0, b=0, c=0, d=0, e=0):
        rows.append((kind, len(rows), len(rows), a, b, c, d, e))

    add(REC_BOOT, 2, 1, 3, 107, 3)
    add(REC_SEED, 58234, 33548, 2, 28, 1)
    add(REC_ROW, 1236, 441, 868, 1, leitis_upgrade_item)
    add(REC_ROW, 548, 363, 869, 2, 3684)
    add(REC_ROW, 588, 376, 825, 2, 3694)
    add(REC_ROW, 77, 320, 815, 2, 3663)
    add(REC_ROW, 359, 341, 817, 2, 3721)

    add(REC_CASE, 0, 101, 0, 0, 0)
    add(REC_RES, 1000, 1000, 1000, 1000, 0)
    add(REC_RES, 1000, 1000, 1000, 1000, 1)

    add(REC_CASE, 1, 105, 0, 0, 0)
    add(REC_RES, 1000, 1000, 1000, 1000, 2)
    add(REC_RES, 8000, 2000, 1500, 8250, 3)

    add(REC_CASE, 2, 1236, 10, 7, 3)
    add(REC_COUNT, 2, leitis_elite, leitis_militia, 10, 1)
    add(REC_LOC, 441, 1, 4, 2, 0)

    for case_id, upgraded_type, location_id in UPGRADE_CASES:
        sent = siege_ram_location_sent if case_id == 3 else 1
        pre = siege_ram_pre_state if case_id == 3 else 0
        add(REC_CASE, case_id, 0, 3, 4, pre)
        add(REC_LOC, location_id, 0, 4, case_id, 0)
        add(REC_STAGE, case_id, 1, 4, 2, 0)
        add(REC_COUNT, case_id, 0, 3, 5, 3)
        add(REC_LOC, location_id, sent, 5, case_id, 0)

    add(REC_CASE, 7, 276, 900, 2, 0)
    for slot in range(8):
        add(REC_WONDER, slot, 200 if slot == 0 else 0, 1, 0, 0)
    add(REC_STAGE, 7, 1, 1, 1, 200)
    add(REC_DIAG, 7, 1, wonder_owner_in_game, wonder_build_points, 1000)
    add(REC_TRACE, 7, 1, 2, 2, 0)
    add(REC_TRACE, 7, 101, 1, 200, 1)
    for slot in range(8):
        add(REC_WONDER, slot, [198, 200][slot] if slot < 2 else 0, 2, 0, 0)
    add(REC_STAGE, 7, 2, 2, 2, 200)
    add(REC_DIAG, 7, 2, wonder_owner_in_game, wonder_build_points, 1000)
    add(REC_TRACE, 7, 2, 2, 2, 0)
    add(REC_TRACE, 7, 102, 1, 200, 1)
    for slot in range(8):
        add(REC_WONDER, slot, [298, 300][slot] if slot < 2 else 0, 3, 0, 0)
    add(REC_STAGE, 7, 3, 2, 2, 200)
    add(REC_DIAG, 7, 3, wonder_owner_in_game, wonder_build_points, 1000)
    add(REC_TRACE, 7, 3, 2, 2, 0)
    add(REC_TRACE, 7, 103, 1, 200, 1)
    for slot in range(8):
        add(REC_WONDER, slot, 299 if slot == 1 else 0, 4, 0, 0)
    add(REC_STAGE, 7, 4, 1, 2, 200)
    add(REC_DIAG, 7, 4, wonder_owner_in_game, wonder_build_points, 1000)
    add(REC_TRACE, 7, 4, 2, -1, (-1 if destroyed_slot_released else 0))
    add(REC_TRACE, 7, 104, 0, 200, 1)

    add(REC_DONE, 8, len(rows), 0, 0, 0)
    return rows


def build(path, rows):
    body = []
    for row in rows:
        body.extend(row)
    body.extend([0] * (RECORDS * FIELDS - len(body)))

    blob = encode_string("AP78") + encode_int(1) + encode_int(RECORDS)
    for value in body[:RECORDS * FIELDS]:
        blob += encode_int(value)
    blob += encode_string("<2>Burgundy Wonder <TIMER>")
    blob += encode_string("<2>Burgundy Wonder <TIMER>")
    blob += encode_string("END")
    blob += encode_int(len(rows))
    blob += encode_int(424242)
    path.write_bytes(blob)


def run(path):
    proc = subprocess.run([sys.executable, str(HERE / "read.py"), str(path)],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def main():
    temp = Path(tempfile.mkdtemp(prefix="ap78-selftest-"))
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
        print(out.strip().splitlines()[-1])

    cases = [
        ("stale install (upgradeItemId 3800)", {"leitis_upgrade_item": 3800}),
        ("Leitis cavemanified", {"leitis_elite": 0, "leitis_militia": 10}),
        ("Siege Ram location not sent", {"siege_ram_location_sent": 0}),
        ("Siege Ram tech already Done at case entry", {"siege_ram_pre_state": 3}),
        ("an incomplete Wonder", {"wonder_build_points": 10}),
        ("the Wonder owner already defeated", {"wonder_owner_in_game": 0}),
        ("the destroyed Wonder's slot was not released", {"destroyed_slot_released": False}),
    ]
    for label, kwargs in cases:
        bad = temp / "bad.xsdat"
        build(bad, good_records(**kwargs))
        code, out = run(bad)
        if code == 0:
            failures += 1
            print(f"FAIL: {label} was not caught")
        else:
            caught = [line for line in out.splitlines() if line.startswith("[FAIL]")]
            print(f"ok: {label} caught -> {len(caught)} failing row(s)")

    print()
    if failures:
        print(f"{failures} selftest failure(s)")
        return 1
    print("selftest passed: the reader accepts a good run and rejects each seeded fault")
    return 0


if __name__ == "__main__":
    sys.exit(main())
