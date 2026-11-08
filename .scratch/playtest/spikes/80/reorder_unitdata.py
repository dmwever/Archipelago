import os
import re
import shutil
import sys
from pathlib import Path

XS = Path(os.environ.get(
    "AP_XS_DIR",
    r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files\resources\_common\xs"))
TARGET = XS / "UnitData.xs"
BACKUP = XS / "UnitData.xs.preorder"

ADD_UNIT = re.compile(
    r"^\s*addUnit\(\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*\)")


def split_blocks(lines, start, end):
    blocks = []
    current = None
    for index in range(start, end):
        match = ADD_UNIT.match(lines[index])
        if match:
            location, type_id, line_id, age, tier, upgrade, exempt = (
                int(v) for v in match.groups())
            current = {"key": (line_id, tier, location), "lines": [lines[index]]}
            blocks.append(current)
        elif current is not None:
            current["lines"].append(lines[index])
        else:
            raise SystemExit(f"line {index + 1} sits before any addUnit: {lines[index]!r}")
    return blocks


def main():
    if "--restore" in sys.argv:
        if not BACKUP.exists():
            print(f"no backup at {BACKUP}")
            return 2
        shutil.copyfile(BACKUP, TARGET)
        print(f"restored {TARGET.name} from {BACKUP.name}")
        return 0

    text = TARGET.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    try:
        open_at = next(i for i, l in enumerate(lines) if l.startswith("void LoadUnitTable()"))
    except StopIteration:
        print("no LoadUnitTable() in the file")
        return 2
    close_at = next(i for i in range(open_at + 1, len(lines)) if lines[i].rstrip() == "}")

    first = next((i for i in range(open_at + 1, close_at) if ADD_UNIT.match(lines[i])), None)
    if first is None:
        print("LoadUnitTable() holds no rows")
        return 2

    blocks = split_blocks(lines, first, close_at)
    before = [b["key"] for b in blocks]
    blocks.sort(key=lambda b: b["key"])
    after = [b["key"] for b in blocks]

    if before == after:
        print("already in (line, tier) order; nothing to do")
        return 0

    if not BACKUP.exists():
        shutil.copyfile(TARGET, BACKUP)
        print(f"backed up to {BACKUP.name}")

    body = []
    for block in blocks:
        body.extend(block["lines"])
    out = lines[:first] + body + lines[close_at:]
    TARGET.write_text("\n".join(out) + "\n", encoding="utf-8")

    moved = sum(1 for a, b in zip(before, after) if a != b)
    print(f"reordered {len(blocks)} rows by (line, tier); {moved} changed position")
    print(f"restore with: py -3 {Path(__file__).name} --restore")
    return 0


if __name__ == "__main__":
    sys.exit(main())
