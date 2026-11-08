import collections
import os
import re
import sys
from pathlib import Path

XS = Path(os.environ.get(
    "AP_XS_DIR",
    r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files\resources\_common\xs"))

ADD_UNIT = re.compile(
    r"addUnit\(\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*\)")
ADD_TECH = re.compile(r"addTech\(\s*(-?\d+),\s*(-?\d+)")
ADD_UNTRAINABLE = re.compile(r"addUnitUntrainable\(\s*(-?\d+),\s*(-?\d+)\s*\)")
CONST = re.compile(r"extern const int (\w+)\s*=\s*(-?\d+)")

HARNESS_ROWS = {
    1236: (441, "Elite Leitis"),
    548: (363, "Siege Ram"),
    588: (376, "Siege Onager"),
    77: (320, "Long Swordsman"),
    359: (341, "Halberdier"),
    422: (343, "Capped Ram"),
    550: (364, "Onager"),
    75: (319, "Man-at-Arms"),
    358: (340, "Pikeman"),
}

Row = collections.namedtuple("Row", "location type line age tier upgrade exempt")

results = []


def check(ticket, name, ok, detail):
    results.append((ticket, name, bool(ok), detail))


def read(stem):
    return (XS / stem).read_text(encoding="utf-8", errors="replace")


def constants(text):
    return {name: int(value) for name, value in CONST.findall(text)}


def main():
    if not XS.exists():
        print(f"xs folder not found at {XS}")
        return 2

    slot = constants(read("SlotData.xs"))
    unit_text = read("UnitData.xs")
    tech_text = read("TechData.xs")
    unit_const = constants(unit_text)
    tech_const = constants(tech_text)

    rows = [Row(*(int(v) for v in m)) for m in ADD_UNIT.findall(unit_text)]
    techs = {int(item): int(tid) for item, tid in ADD_TECH.findall(tech_text)}
    untrainable = collections.defaultdict(set)
    for type_id, civ in ADD_UNTRAINABLE.findall(unit_text):
        untrainable[int(type_id)].add(int(civ))

    seed = (slot.get("AP_SEED_HIGH"), slot.get("AP_SEED_LOW"))
    check("78", "UnitData and TechData are from the installed seed",
          (unit_const.get("US_SEED_HIGH"), unit_const.get("US_SEED_LOW")) == seed
          and (tech_const.get("TS_SEED_HIGH"), tech_const.get("TS_SEED_LOW")) == seed,
          f"slot={seed} units=({unit_const.get('US_SEED_HIGH')}, {unit_const.get('US_SEED_LOW')})"
          f" techs=({tech_const.get('TS_SEED_HIGH')}, {tech_const.get('TS_SEED_LOW')})")

    check("78", "the seed is unitsanity all, techsanity all, caveman on",
          slot.get("AP_US_MODE") == 2 and slot.get("AP_TS_MODE") == 3
          and slot.get("AP_US_CAVEMAN") == 1,
          f"unitsanity={slot.get('AP_US_MODE')} techsanity={slot.get('AP_TS_MODE')}"
          f" caveman={slot.get('AP_US_CAVEMAN')} rows={len(rows)} techs={len(techs)}")

    phantom = [r for r in rows if r.upgrade != -1 and r.upgrade not in techs]
    check("73", "no row asks for an upgrade item the seed never created",
          not phantom,
          "clean across %d rows" % len(rows) if not phantom
          else ", ".join(f"location {r.location} type {r.type} wants {r.upgrade}" for r in phantom))

    leitis = next((r for r in rows if r.type == 1236), None)
    check("73", "the Elite Leitis row carries no upgrade item",
          leitis is not None and leitis.upgrade == -1,
          f"upgradeItemId={leitis.upgrade}" if leitis else "row missing")

    lines = collections.defaultdict(list)
    for row in rows:
        if row.line >= 0:
            lines[row.line].append(row)

    civs = set()
    for blocked in untrainable.values():
        civs |= blocked

    def trainable_for(row):
        return civs - untrainable.get(row.type, set())

    headless = []
    for line, members in sorted(lines.items()):
        if any(m.tier == 0 for m in members):
            continue
        if all(m.exempt == 1 for m in members):
            continue
        headless.append((line, members))

    if headless:
        note = "; ".join(
            "line %d: %s" % (line, ", ".join(
                "type %d tier %d trainableFor %s"
                % (m.type, m.tier, sorted(trainable_for(m)) or "nobody")
                for m in sorted(members, key=lambda m: m.tier)))
            for line, members in headless)
        print(f"[NOTE] #74  lines with no tier-0 row: {note}")
        print("            Not a fault. cEnableObject is gated to tier 0, but setObjectDisable")
        print("            clears the disabled flag for every row, so the vanilla tech tree")
        print("            decides. Engine-verified in spikes/80 run 2. See issue #80.")
        print()

    by_type = {r.type: r for r in rows}
    missing = []
    for type_id, (location, label) in sorted(HARNESS_ROWS.items()):
        row = by_type.get(type_id)
        if row is None or row.location != location:
            missing.append(f"{label} ({type_id})")
    check("78", "every row the layer-2 harness drives is where it expects",
          not missing, ", ".join(missing) or "all %d present" % len(HARNESS_ROWS))

    width = max(len(name) for _, name, _, _ in results)
    failed = 0
    for ticket, name, ok, det in results:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{mark}] #{ticket}  {name.ljust(width)}  {det}")
    print()
    print(f"{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
