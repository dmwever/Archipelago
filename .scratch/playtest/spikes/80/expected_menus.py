import collections
import os
import re
import sys
from pathlib import Path

XS = Path(os.environ.get(
    "AP_XS_DIR",
    r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files\resources\_common\xs"))

CIV = int(os.environ.get("AP_CIV", "12"))
CIV_NAMES = {2: "Franks", 12: "Mongols", 17: "Huns"}

Row = collections.namedtuple("Row", "location type line age tier upgrade exempt")


def unit_table():
    text = (XS / "UnitData.xs").read_text(encoding="utf-8", errors="replace")
    rows = [Row(*(int(v) for v in m)) for m in re.findall(
        r"addUnit\(\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*\)",
        text)]
    untrainable = collections.defaultdict(set)
    for type_id, civ in re.findall(r"addUnitUntrainable\(\s*(-?\d+),\s*(-?\d+)\s*\)", text):
        untrainable[int(type_id)].add(int(civ))
    return rows, untrainable


def tech_by_item():
    text = (XS / "TechData.xs").read_text(encoding="utf-8", errors="replace")
    found = re.findall(r"addTech\(\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)", text)
    by_item = {int(i): int(t) for i, t, _ in found}
    umbrella = {int(i) for i, _, effect in found if int(effect) == -1}
    return by_item, umbrella


def main():
    rows, untrainable = unit_table()
    techs, umbrella = tech_by_item()

    def trainable(row):
        return CIV not in untrainable.get(row.type, set())

    def forced(row):
        return row.upgrade in umbrella

    lines = collections.defaultdict(list)
    loose = []
    for row in rows:
        if row.line >= 0 and row.exempt == 0:
            lines[row.line].append(row)
        else:
            loose.append(row)

    civ_name = CIV_NAMES.get(CIV, f"civ {CIV}")
    print(f"Expected train menus for {civ_name}, from {len(rows)} installed rows")
    print(f"{len(lines)} unit lines, {len(loose)} rows that are granted-only or a profession")
    print()
    print("A line shares one train button, so one line is one thing to look at.")
    print("Phase 1 is every line item delivered and no upgrade researched.")
    print("Phase 2 is every upgrade researched as well.")
    print()

    unchanged = 0
    moves = 0
    blank = 0
    untestable = []
    print(f"{'line':>5}  {'phase 1':>8}  {'phase 2':>8}   ladder")
    for line in sorted(lines):
        members = sorted(lines[line], key=lambda r: r.tier)
        civ_ok = [r for r in members if trainable(r)]
        sweep_ok = [r for r in members if trainable(r) or not forced(r)]
        ladder = " -> ".join(
            "t%d:%d%s" % (r.tier, r.type,
                          "" if trainable(r) else ("(umbrella, gated)" if forced(r) else "(no)"))
            for r in members)
        if not civ_ok:
            blank += 1
            print(f"{line:>5}  {'nothing':>8}  {'nothing':>8}   {ladder}")
            continue
        low = civ_ok[0]
        sweep_high = sweep_ok[-1] if sweep_ok else low
        civ_high = civ_ok[-1]
        if sweep_high.type != civ_high.type:
            untestable.append((line, civ_high.type, sweep_high.type))
        if low.type == sweep_high.type:
            unchanged += 1
        else:
            moves += 1
        print(f"{line:>5}  {low.type:>8}  {sweep_high.type:>8}   {ladder}")

    print()
    print(f"{moves} lines should change unit between the phases, {unchanged} should stay put, "
          f"{blank} should stay empty.")
    print()
    print("Phase 2 is what the SWEEP produces, which is not always what a player would see.")
    print("The sweep writes every upgrade tech to Done, and a tech the civ lacks reports NotReady")
    print("rather than Disabled, so the write goes through and the line runs past the civ's")
    print("real top tier. Only an explicit gate in the mod stops it - the umbrella rows.")
    if untestable:
        print()
        print("Lines the sweep cannot judge, because it forces a tech this civ could not research:")
        for line, civ_top, sweep_top in untestable:
            print(f"  line {line}: a player would stop at {civ_top}, the sweep reaches {sweep_top}")
        print("Those rows prove nothing either way. Every other line is a real test of the gate.")
    print()

    upgrades = sorted({r.upgrade for r in rows if r.upgrade >= 0})
    missing = [u for u in upgrades if u not in techs]
    print(f"{len(upgrades)} distinct upgrade items across the table; "
          f"{len(missing)} have no tech in the seed {missing}")
    print("The spike researches every tech the table names, straight out of TechData, so no "
          "list is hardcoded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
