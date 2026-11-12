"""Recapture locations/connections/GameStrings.py from the game's own dat.

    python -m worlds.age2de.tools.recapture_string_ids        # from the repository root

Reading an object's vanilla description in game needs the extended tooltip string id, which is
the dat's name string id plus a fixed offset. The runtime attribute that looks like that id is
not it, so the ids are baked here instead of derived in XS, the way the game costs are baked in
`GameCosts.py`.

The ids move when the game patches, so rerun this after an update and read the diff: a line that
moved is an object the game renumbered, and a line that vanished is one this catalogue names and
the dat no longer carries, which is a bug in the catalogue rather than in the dump.

    --dat PATH    the empires dat to read; defaults to the Steam install
    --kit PATH    the aoe2kit binary; defaults to AOE2KIT, then `kit` on PATH
    --jobs N      how many dat reads to run at once

Every technology costs its own `kit dat tech` call and each one parses the whole dat, so the run
takes a few minutes even spread across cores. The objects come from one `kit dat units` call.

A handful of make-available technologies carry no name string of their own and only an extended
help id; those fall back to the help id less its own offset, which is the name string the game
shows for them.

The file it writes asserts at import that every technology, unit and building this world names
has an id, so a half-written dump fails on any test run rather than in a seed.

This writes LF where the working tree is CRLF, so `git status` calls the file modified even when
every id is identical. Ask `git diff`; the index stores LF either way.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys

from worlds.age2de.locations.Buildings import Age2BuildingData
from worlds.age2de.locations.EscortUnits import Age2EscortUnitData
from worlds.age2de.locations.Heroes import Age2HeroData
from worlds.age2de.locations.Techs import Age2TechData
from worlds.age2de.locations.Units import Age2UnitData
from worlds.age2de.locations.VillagerJobs import Age2VillagerJobData

MODULE = (pathlib.Path(__file__).resolve().parents[1] / "locations" / "connections"
          / "GameStrings.py")

STEAM_DAT = pathlib.Path(
    "C:/Program Files (x86)/Steam/steamapps/common/AoE2DE/resources/_common/dat"
    "/empires2_x2_p1.dat")

READ_CIV = 1

EXTENDED_TOOLTIP_OFFSET = 21000

HELP_OFFSET = 100000

OBJECT_KINDS = (
    ("UNIT_NAME_STRINGS", "Age2UnitData", Age2UnitData, lambda place: place.game_id),
    ("VILLAGER_JOB_NAME_STRINGS", "Age2VillagerJobData", Age2VillagerJobData,
     lambda place: place.game_id),
    ("HERO_NAME_STRINGS", "Age2HeroData", Age2HeroData, lambda place: place.game_id),
    ("ESCORT_NAME_STRINGS", "Age2EscortUnitData", Age2EscortUnitData,
     lambda place: place.game_id),
    ("BUILDING_NAME_STRINGS", "Age2BuildingData", Age2BuildingData,
     lambda place: place.item.type.game_id),
)

TAIL = '''
NAME_STRINGS_BY_KIND: dict[type, dict[DecoratedPlace, int]] = {
    Age2TechData: TECH_NAME_STRINGS,
    Age2UnitData: UNIT_NAME_STRINGS,
    Age2VillagerJobData: VILLAGER_JOB_NAME_STRINGS,
    Age2HeroData: HERO_NAME_STRINGS,
    Age2EscortUnitData: ESCORT_NAME_STRINGS,
    Age2BuildingData: BUILDING_NAME_STRINGS,
}


def extended_tooltip_id(place: DecoratedPlace) -> int:
    return NAME_STRINGS_BY_KIND[type(place)][place] + EXTENDED_TOOLTIP_OFFSET


for _kind, _names in NAME_STRINGS_BY_KIND.items():
    assert not [place for place in _kind if place not in _names], (
        f"a {_kind.__name__} member has no name string id; rerun recapture_string_ids")
'''


def kit_path(given: str | None) -> str:
    candidate = given or os.environ.get("AOE2KIT") or shutil.which("kit")
    if candidate is None:
        raise SystemExit("no aoe2kit binary: pass --kit, or set AOE2KIT")
    if not pathlib.Path(candidate).is_file():
        raise SystemExit(f"no aoe2kit binary at {candidate}")
    return candidate


def dat_path(given: str | None) -> pathlib.Path:
    path = pathlib.Path(given) if given else STEAM_DAT
    if not path.is_file():
        raise SystemExit(f"no game dat at {path}; pass --dat")
    return path


def read_json(kit: str, args: list[str]) -> dict:
    done = subprocess.run([kit, *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"{' '.join(args)} failed: {done.stderr.strip()}")
    return json.loads(done.stdout)


def object_name_strings(kit: str, dat: pathlib.Path) -> dict[int, int]:
    dump = read_json(kit, ["dat", "units", str(dat), "--civ", str(READ_CIV), "--all"])
    return {unit["id"]: unit["string_id"] for unit in dump["units"]}


def tech_name_strings(kit: str, dat: pathlib.Path, jobs: int) -> dict[int, int]:
    wanted = sorted({tech.item.type.game_id for tech in Age2TechData})

    def one(game_id: int) -> tuple[int, int]:
        record = read_json(kit, ["dat", "tech", str(dat), str(game_id)])
        name_string = record["language_dll_name"]
        if name_string < 1:
            name_string = record["language_dll_help"] - HELP_OFFSET
        return game_id, name_string

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        return dict(pool.map(one, wanted))


def rows(kind, name_of, strings: dict[int, int]) -> list[tuple[str, int]]:
    out = []
    for place in kind:
        name_string = strings.get(name_of(place))
        if name_string is None or name_string < 1:
            raise SystemExit(f"{kind.__name__}.{place.name} is not in the dat dump")
        out.append((f"{kind.__name__}.{place.name}", name_string))
    return out


def render_table(variable: str, annotation: str, body: list[tuple[str, int]]) -> str:
    lines = [f"{variable}: dict[{annotation}, int] = {{"]
    lines += [f"    {key}: {value}," for key, value in body]
    lines.append("}")
    return "\n".join(lines)


def render(source: str, techs: dict[int, int], objects: dict[int, int]) -> str:
    parts = [
        "from ..Buildings import Age2BuildingData",
        "from ..EscortUnits import Age2EscortUnitData",
        "from ..Heroes import Age2HeroData",
        "from ..Techs import Age2TechData",
        "from ..Units import Age2UnitData",
        "from ..VillagerJobs import Age2VillagerJobData",
        "",
        "DecoratedPlace = (Age2TechData | Age2UnitData | Age2VillagerJobData",
        "                  | Age2HeroData | Age2EscortUnitData | Age2BuildingData)",
        "",
        f'GAME_STRING_SOURCE = "{source}"',
        "",
        f"EXTENDED_TOOLTIP_OFFSET = {EXTENDED_TOOLTIP_OFFSET}",
        "",
        "NO_TOOLTIP = -1",
        "",
        render_table("TECH_NAME_STRINGS", "Age2TechData",
                     rows(Age2TechData, lambda tech: tech.item.type.game_id, techs)),
        "",
    ]
    for variable, annotation, kind, name_of in OBJECT_KINDS:
        parts.append(render_table(variable, annotation, rows(kind, name_of, objects)))
        parts.append("")
    return "\n".join(parts) + TAIL


def recapture(kit: str, dat: pathlib.Path, jobs: int) -> dict:
    objects = object_name_strings(kit, dat)
    techs = tech_name_strings(kit, dat, jobs)
    read_on = datetime.date.today().isoformat()
    source = f"{dat.name}, read {read_on} through aoe2kit"
    MODULE.write_text(render(source, techs, objects), encoding="utf-8", newline="\n")
    return {"path": MODULE, "techs": len(techs), "objects": len(objects), "source": source}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="recapture_string_ids")
    parser.add_argument("--dat")
    parser.add_argument("--kit")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    args = parser.parse_args(argv)
    written = recapture(kit_path(args.kit), dat_path(args.dat), args.jobs)
    print(f"wrote {written['path']}")
    print(f"source: {written['source']}")
    print(f"technologies: {written['techs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
