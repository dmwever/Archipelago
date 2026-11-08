import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import forks as catalog

KIT = Path(os.environ.get("AOE2KIT", r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe"))
AGE2_FILES = Path(os.environ.get(
    "AP_AGE2_FILES", r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files"))
XS_DIR = Path(os.environ.get("AP_XS_DIR", AGE2_FILES / "resources/_common/xs"))
SCEN_DIR = Path(os.environ.get("AP_SCENARIO_DIR", AGE2_FILES / "resources/_common/scenario"))
PROFILE = Path(os.environ.get("AP_PROFILE_DIR", AGE2_FILES / "profile"))
XS_CHECK = Path(os.environ.get("AP_XS_CHECK", XS_DIR / "xs-check.exe"))

PREFIX = "PT82_"
CONST = re.compile(r"extern const int (\w+)\s*=\s*(-?\d+)")
PROFILE_LEFTOVERS = ("AP.xsdat", "items.xsdat", "locations.xsdat", "buildings.xsdat",
                     "techs.xsdat", "units.xsdat", "messages.xsdat", "startup.xsdat",
                     "mercenaries.xsdat")
SIDECAR = "default1.xsdat"


class BuildError(Exception):
    pass


def run_kit(*args):
    proc = subprocess.run([str(KIT), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise BuildError(" ".join(str(a) for a in args) + "\n" + proc.stdout + proc.stderr)
    return proc.stdout


def source_path(fork):
    return SCEN_DIR / (fork.source + ".aoe2scenario")


def fork_stem(fork):
    return PREFIX + fork.key


def scenario_units(path):
    data = json.loads(run_kit("scen", "units", str(path)))
    found = {}
    for section in data["sections"]:
        for unit in section.get("units") or []:
            found[unit["reference_id"]] = (section["player"], unit["unit_const"],
                                           unit["x"], unit["y"])
    return found


def scenario_terrain(path):
    data = json.loads(run_kit("scen", "terrain", str(path), "--tiles"))
    return {(tile["x"], tile["y"]): tile["terrain_id"] for tile in data["tiles"]}


def scenario_trigger_names(path):
    data = json.loads(run_kit("scen", "triggers", str(path), "--limit", "4000"))
    matches = data.get("matches") or []
    if data.get("total_matches", len(matches)) > len(matches):
        raise BuildError(
            f"{path.name} has {data['total_matches']} triggers but the listing showed"
            f" {len(matches)}; raise the limit before trusting a missing-trigger report")
    names = set()
    for match in matches:
        name = match.get("trigger_name")
        if name:
            names.add(name)
    return names


def installed_seed():
    text = (XS_DIR / "SlotData.xs").read_text(encoding="utf-8", errors="replace")
    return {name: int(value) for name, value in CONST.findall(text)}


def check_seed(problems):
    try:
        seed = installed_seed()
    except OSError as error:
        problems.append(f"SlotData.xs unreadable: {error}")
        return
    if seed.get("AP_SLOT_ID", -1) == -1:
        problems.append("SlotData.xs has no slot. Run spikes/78/install_seed.py first.")
    for name, want in catalog.REQUIRED_SEED.items():
        got = seed.get(name)
        if got != want:
            problems.append(f"installed seed has {name}={got}, the forks need {want}")


def verify(fork):
    path = source_path(fork)
    if not path.is_file():
        raise BuildError(f"{path} is missing")
    problems = []

    if fork.unit_pins:
        units = scenario_units(path)
        for ref, unit_const, player in fork.unit_pins:
            actual = units.get(ref)
            if actual is None:
                problems.append(f"unit {ref} is not in {fork.source}")
            elif (actual[0], actual[1]) != (player, unit_const):
                problems.append(
                    f"unit {ref} is p{actual[0]} type {actual[1]}, pinned as p{player}"
                    f" type {unit_const}")

    if fork.trigger_pins:
        names = scenario_trigger_names(path)
        for name in fork.trigger_pins:
            if name not in names:
                problems.append(f'trigger "{name}" is not in {fork.source}')

    if fork.reveal:
        terrain = scenario_terrain(path)
        for x, y, _radius in fork.reveal:
            if (x, y) not in terrain:
                problems.append(f"reveal point ({x},{y}) is off the map")

    if problems:
        raise BuildError(f"{fork.key}: " + "\n       ".join(problems))


def footprint_tiles(create, x, y):
    low = (create.footprint - 1) // 2
    return [(x + dx, y + dy)
            for dx in range(-low, create.footprint - low)
            for dy in range(-low, create.footprint - low)]


def choose_tiles(fork, patched):
    if not fork.creates:
        return {}
    terrain = scenario_terrain(patched)
    taken = {(int(x), int(y))
             for _player, _const, x, y in scenario_units(patched).values()}

    chosen = {}
    problems = []
    for create in fork.creates:
        x1, y1, x2, y2 = create.search
        usable = []
        allowed = create.terrain | catalog.WATER if create.needs_water else create.terrain
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                spot = footprint_tiles(create, x, y)
                kinds = [terrain.get(tile) for tile in spot]
                if any(kind not in allowed for kind in kinds):
                    continue
                if any(tile in taken for tile in spot):
                    continue
                if create.needs_water and not (
                        any(kind in create.terrain for kind in kinds)
                        and any(kind in catalog.WATER for kind in kinds)):
                    continue
                usable.append((x, y))
        if not usable:
            problems.append(
                f"{create.name} ({create.footprint}x{create.footprint}) has nowhere clear in"
                f" {create.search}: every footprint hits the wrong terrain or a placed unit")
            continue
        usable.sort(key=lambda tile: (tile[0] - create.prefer[0]) ** 2
                    + (tile[1] - create.prefer[1]) ** 2)
        chosen[create.name] = usable[:create.limit]

    if problems:
        raise BuildError(f"{fork.key}: " + "\n       ".join(problems))
    return chosen


def xs_literal(value):
    return str(value).lower() if isinstance(value, bool) else str(value)


def helper_block():
    return """int pt82Tick = 0;

int PT82Bool(bool value = false) {
    if (value) {
        return (1);
    }
    return (0);
}

int PT82Live(int arrayId = -1) {
    int total = xsArrayGetSize(arrayId);
    int live = 0;
    for (i = 0; < total) {
        if (xsArrayGetInt(arrayId, i) >= 0) {
            live = live + 1;
        }
    }
    return (live);
}

int PT82Slot(int unitId = -1) {
    if (unitId < 0) {
        return (-1);
    }
    return (FindWonderSlot(unitId));
}

int PT82Counting(int unitId = -1) {
    int slot = PT82Slot(unitId);
    if (slot < 0) {
        return (-1);
    }
    return (PT82Bool(IsWonderCounting(slot)));
}

int PT82RevealKind(int unitId = -1) {
    int slot = PT82Slot(unitId);
    if (slot < 0) {
        return (-1);
    }
    return (WonderSlotRevealKind(slot));
}

int PT82BuildTo(int unitId = -1, int owner = -1, int typeId = -1, int percent = 0) {
    if (unitId < 0 || xsDoesUnitExist(unitId) == false) {
        return (-1);
    }
    float points = 0.01 * percent * xsGetObjectAttribute(owner, typeId, cTrainTime, 0);
    return (PT82Bool(xsSetUnitBuildPoints(unitId, points)));
}

int PT82Owner(int unitId = -1) {
    if (xsDoesUnitExist(unitId) == false) {
        return (-1);
    }
    return (xsGetUnitOwner(unitId));
}

int PT82Gold(int player = -1) {
    return (xsCeilToInt(xsPlayerAttribute(player, cAttributeGold)));
}

int PT82Years(int timerId = -1) {
    if (timerId < 0) {
        return (-1);
    }
    return (xsCeilToInt(xsUnsyncGetTimerTimeRemaining(timerId, cTimerUnitYears, -1)));
}

void PT82Reveal(int x = 0, int y = 0, int radius = 0) {
    RevealAround(xsVectorSet(1.0 * x, 1.0 * y, 0.0), radius);
}

int PT82Create(int typeId = -1, int owner = -1, bool foundation = false,
               int x = 0, int y = 0) {
    return (xsCreateUnit(typeId, owner, xsVectorSet(1.0 * x, 1.0 * y, 0.0),
                         foundation, false, true));
}

int PT82CreateNear(int typeId = -1, int owner = -1, bool foundation = false,
                   int cx = 0, int cy = 0, int radius = 0) {
    xsEffectAmount(cEnableObject, typeId, cAttributeEnable, 1.0, owner);
    for (ring = 0; < radius + 1) {
        int span = 2 * ring + 1;
        for (i = 0; < span) {
            for (j = 0; < span) {
                if (i != 0 && i != span - 1 && j != 0 && j != span - 1) {
                    continue;
                }
                int created = PT82Create(typeId, owner, foundation,
                                         cx - ring + i, cy - ring + j);
                if (created != -1) {
                    xsChatData("<GREY>PT82: placed " + typeId + " for p" + owner + " at "
                               + (cx - ring + i) + "," + (cy - ring + j));
                    return (created);
                }
            }
        }
    }
    return (-1);
}
"""


COUNT_CALL = re.compile(r"PT82Count\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def count_queries(fork):
    queries = {}
    sources = [probe.expr for probe in fork.probes]
    for _tick, lines in (*fork.stage, *fork.shorten):
        sources.extend(lines)
    for text in sources:
        for player, type_id in COUNT_CALL.findall(text):
            key = (int(player), int(type_id))
            if key not in queries:
                queries[key] = f"PT82CountP{player}T{type_id}"
    return queries


def count_block(queries):
    blocks = []
    for (player, type_id), name in queries.items():
        scan = f"pt82Scan{name[len('PT82Count'):]}"
        last = f"pt82Last{name[len('PT82Count'):]}"
        blocks.append(
            f"int {scan} = -1;\n"
            f"int {last} = -1;\n"
            f"int {name}() {{\n"
            f"    int found = xsGetPlayerUnitIds({player}, {type_id}, {scan});\n"
            f"    if (found >= 0) {{\n"
            f"        {scan} = found;\n"
            f"        {last} = PT82Live(found);\n"
            f"    }}\n"
            f"    return ({last});\n"
            f"}}")
    return "\n\n".join(blocks)


def with_counts(text, queries):
    return COUNT_CALL.sub(
        lambda match: queries[(int(match.group(1)), int(match.group(2)))] + "()", text)


def record_block(fork, queries):
    lines = ["void PT82Record() {",
             "    bool created = xsCreateFile(false);",
             "    if (created == false) {",
             "        return;",
             "    }",
             f"    xsWriteInt({catalog.MAGIC});",
             f"    xsWriteInt({fork.fork_id});",
             f"    xsWriteInt({fork.scenario_id});",
             "    xsWriteInt(AP_SLOT_ID);",
             "    xsWriteInt(AP_US_MODE);",
             "    xsWriteInt(AP_TS_MODE);",
             "    xsWriteInt(AP_US_CAVEMAN);",
             "    xsWriteInt(xsGetGameTime());",
             "    xsWriteInt(pt82Tick);",
             f"    xsWriteInt({len(fork.probes)});"]
    for probe in fork.probes:
        lines.append(f"    xsWriteInt({with_counts(probe.expr, queries)});")
    lines.append(f"    xsWriteInt({catalog.FOOTER});")
    lines.append("    xsCloseFile();")
    lines.append("}")
    return "\n".join(lines)


def create_lines(create, tiles):
    x, y = tiles[0]
    out = [f"    {create.name} = PT82CreateNear({create.unit_const}, {create.owner},"
           f" {xs_literal(create.foundation)}, {x}, {y}, {create.radius});"]
    out.append(f"    if ({create.name} == -1) {{")
    out.append(f'        xsChatData("<RED>PT82: could not place {create.name} anywhere within "'
               f'\n                   + {create.radius} + " tiles of {x},{y}.");')
    out.append("    }")
    return out


def stage_block(fork, shorten, tiles, queries):
    steps = collections.defaultdict(list)

    opening = ["    GiveStartupBuildings();",
               "    GiveStartupTechs();",
               "    GiveStartupUnits();",
               "    GiveScenarioItems();"]
    for x, y, radius in fork.reveal:
        opening.append(f"    PT82Reveal({x}, {y}, {radius});")
    opening.append(f'    xsChatData("<GREEN>PT82 {fork.key} staged: {fork.title}");')
    steps[1].extend(opening)

    for create in fork.creates:
        steps[create.tick].extend(create_lines(create, tiles[create.name]))
    for tick, lines in fork.stage:
        steps[tick].extend("    " + with_counts(line, queries) for line in lines)
    if shorten:
        for tick, lines in fork.shorten:
            steps[tick].extend("    " + with_counts(line, queries) for line in lines)

    body = ["rule PT82Stage", "    inactive", "    minInterval 1", "    maxInterval 1", "{",
            "    pt82Tick = pt82Tick + 1;"]
    for tick in sorted(steps):
        body.append(f"    if (pt82Tick == {tick}) {{")
        body.extend("    " + line for line in steps[tick])
        body.append("    }")
    body.append("    PT82Record();")
    body.append("}")
    return "\n".join(body)


def init_block():
    return """void PT82Init() {
    xsDisableRule("ConnectAP");
    xsDisableRule("WriteAP");
    xsEnableRule("PT82Stage");
}
"""


def generate_xs(fork, shorten, tiles):
    source = (XS_DIR / (fork.source + ".xs")).read_text(encoding="utf-8")

    items = "\n".join(f"  GiveItem({item});" for item in fork.items) or "  return;"
    give, count = re.subn(r"void GiveScenarioItems\(\) \{.*?\n\}",
                          "void GiveScenarioItems() {\n" + items + "\n}",
                          source, count=1, flags=re.DOTALL)
    if count != 1:
        raise BuildError(f"{fork.source}.xs: GiveScenarioItems() was not where it was expected")

    main_match = re.search(r"void main\(\) \{(.*?)\n\}", give, flags=re.DOTALL)
    if main_match is None:
        raise BuildError(f"{fork.source}.xs: main() was not where it was expected")
    if f"SetScenarioId({fork.scenario_id})" not in main_match.group(1):
        raise BuildError(
            f"{fork.source}.xs: main() does not set scenario id {fork.scenario_id}")

    declarations = [f"int {name} = {value};" for name, value in fork.globals]
    declarations += [f"int {create.name} = -1;" for create in fork.creates]
    queries = count_queries(fork)

    block = "\n\n".join(part for part in (
        helper_block(),
        count_block(queries),
        "\n".join(declarations),
        record_block(fork, queries),
        init_block(),
        stage_block(fork, shorten, tiles, queries),
    ) if part)

    new_main = ("void main() {\n"
                f"  SetScenarioId({fork.scenario_id});\n"
                "  InitAP();\n"
                "  PT82Init();\n"
                "}")
    rebuilt = give[:main_match.start()] + block + "\n\n" + new_main + give[main_match.end():]

    victory, count = re.subn(r"(void Victory\(\) \{\n)(.*?)(\n\})",
                             r"\1\2\n  PT82Record();\3", rebuilt, count=1, flags=re.DOTALL)
    if count != 1:
        raise BuildError(
            f"{fork.source}.xs: Victory() was not where it was expected."
            " GiveVictory() calls AP_Write(), which would overwrite the fork's sidecar.")
    return victory


ANSI = re.compile(r"\x1b\[[0-9;]*m")
XS_ERROR = re.compile(r"^Error: (\S+)", re.MULTILINE)


def lint(path):
    if not XS_CHECK.is_file():
        return f"skipped, no xs-check at {XS_CHECK}"
    proc = subprocess.run([str(XS_CHECK), "-I", ".", "--", path.name],
                          cwd=str(XS_DIR), capture_output=True, text=True)
    output = ANSI.sub("", proc.stdout + proc.stderr).strip()
    errors = XS_ERROR.findall(output)
    if proc.returncode != 0 or errors:
        raise BuildError(f"xs-check rejected {path.name}:\n{output}")
    warnings = output.count("This function")
    return "clean" if not warnings else f"{warnings} warning(s)"


def patch_scenario(fork):
    recipe = {"xs": {"name": fork_stem(fork), "mode": "attachment"}}
    if fork.recipe_ops:
        recipe["units"] = [dict(op) for op in fork.recipe_ops]
    if fork.trigger_ops:
        recipe["triggers"] = [dict(op) for op in fork.trigger_ops]
    target = SCEN_DIR / (fork_stem(fork) + ".aoe2scenario")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as handle:
        json.dump(recipe, handle)
        recipe_path = handle.name
    try:
        run_kit("scen", "patch", str(source_path(fork)), str(target), "--recipe", recipe_path)
    finally:
        os.unlink(recipe_path)
    report = json.loads(run_kit("scen", "xs", str(target)))
    attached = report["xs"]["script_name"]
    if not attached.startswith(fork_stem(fork)):
        raise BuildError(f"{target.name} points at {attached}, not {fork_stem(fork)}")
    return target


def build(fork, shorten):
    verify(fork)
    scenario = patch_scenario(fork)
    tiles = choose_tiles(fork, scenario)
    xs_path = XS_DIR / (fork_stem(fork) + ".xs")
    xs_path.write_text(generate_xs(fork, shorten, tiles), encoding="utf-8")
    note = lint(xs_path)
    return xs_path, scenario, note


def clean():
    removed = []
    for folder, suffix in ((XS_DIR, ".xs"), (SCEN_DIR, ".aoe2scenario")):
        for path in sorted(folder.glob(PREFIX + "*" + suffix)):
            path.unlink()
            removed.append(path.name)
    return removed


def holds_a_fork_run(path):
    try:
        with open(path, "rb") as handle:
            head = handle.read(4)
    except OSError:
        return False
    return len(head) == 4 and int.from_bytes(head, "little", signed=True) == catalog.MAGIC


def clear_profile(force):
    removed = []
    kept = []
    for name in PROFILE_LEFTOVERS:
        path = PROFILE / name
        if path.is_file():
            path.unlink()
            removed.append(name)
    for path in sorted(PROFILE.glob("*.xsdat")):
        if path.name.startswith(("ATT", "JOAN", "GEN")):
            path.unlink()
            removed.append(path.name)
    sidecar = PROFILE / SIDECAR
    if sidecar.is_file():
        if holds_a_fork_run(sidecar) and not force:
            kept.append(SIDECAR)
        else:
            sidecar.unlink()
            removed.append(SIDECAR)
    return removed, kept


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build the #82 fork scenarios from the live AP scenarios.")
    parser.add_argument("keys", nargs="*", help="fork keys to build; default is all of them")
    parser.add_argument("--clean", action="store_true",
                        help="delete every PT82_* file from the xs and scenario folders")
    parser.add_argument("--clear-profile", action="store_true",
                        help="delete the client's leftover xsdat files before a run")
    parser.add_argument("--force", action="store_true",
                        help="with --clear-profile, delete an unread fork sidecar as well")
    parser.add_argument("--shorten", action="store_true",
                        help="include the timer-shortening step where a fork has one")
    parser.add_argument("--list", action="store_true", help="print the catalog and stop")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        for fork in catalog.FORKS:
            print(f"{fork.key}  {fork.source:<14} {', '.join(fork.checks):<10} {fork.title}")
        return 0

    if args.clean:
        removed = clean()
        print(f"removed {len(removed)} file(s)" + (": " + ", ".join(removed) if removed else ""))
        return 0

    if args.clear_profile:
        removed, kept = clear_profile(args.force)
        print(f"cleared {len(removed)} file(s) from {PROFILE}"
              + (": " + ", ".join(removed) if removed else ""))
        if kept:
            print(f"kept {SIDECAR}: it holds a fork run nobody has read yet."
                  " Decode it with read.py, or pass --force to drop it.")
        return 0

    if not KIT.is_file():
        print(f"aoe2kit not found at {KIT}")
        return 2

    problems = []
    check_seed(problems)
    if problems:
        for problem in problems:
            print(f"[SEED] {problem}")
        return 2

    chosen = catalog.FORKS
    if args.keys:
        unknown = [key for key in args.keys if key not in catalog.BY_KEY]
        if unknown:
            print(f"unknown fork(s): {', '.join(unknown)}")
            return 2
        chosen = [catalog.BY_KEY[key] for key in args.keys]

    failed = 0
    for fork in chosen:
        try:
            xs_path, scenario, note = build(fork, args.shorten)
        except BuildError as error:
            failed += 1
            print(f"[FAIL] {error}")
            continue
        print(f"[OK]   {fork.key}  {scenario.name}  +  {xs_path.name}  (xs-check: {note})")

    print()
    print(f"{len(chosen) - failed}/{len(chosen)} built into {SCEN_DIR}")
    if failed == 0:
        print("clear the profile before the first run: py -3 build.py --clear-profile")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
