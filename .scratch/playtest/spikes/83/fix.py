import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

KIT = Path(os.environ.get("AOE2KIT", r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe"))

AGE2DE = Path(os.environ.get(
    "AP_AGE2DE", r"C:\Users\dmwev\Documents\GitHub\Archipelago\worlds\age2de"))
sys.path.insert(0, str(AGE2DE))

from AoE2ScenarioParser.helper import printers

printers.rprint = lambda *args, **kwargs: None
printers.s_print = lambda *args, **kwargs: None

from AoE2ScenarioParser.datasets.trigger_lists.capture_flag import CaptureFlag
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

SCEN_DIR = Path(os.environ.get(
    "AP_SCENARIO_DIR",
    r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files\resources\_common\scenario"))
STEM = "AP_Joan_6"
GAIA = 0
BOMBARD_CANNON = 36
PACKED_TREBUCHET = 331

SPAWNS = {
    "Easy": ((BOMBARD_CANNON, 108, 120), (PACKED_TREBUCHET, 136, 125)),
    "Easy and Moderate": ((BOMBARD_CANNON, 107, 120), (BOMBARD_CANNON, 103, 120)),
}
REMOVERS = {
    "Easy": ("Not Easy", 3),
    "Easy and Moderate": ("Not Easy or Moderate", 2),
}
SIBLINGS = {BOMBARD_CANNON: 8108, PACKED_TREBUCHET: 10542}


class FixError(Exception):
    pass


def shipped_color_mood(path):
    proc = subprocess.run([str(KIT), "scen", "settings", str(path)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise FixError("could not read the shipped map colour mood:\n" + proc.stderr)
    return json.loads(proc.stdout)["map"]["color_mood"]


def trigger_by_name(scenario, name):
    found = [trigger for trigger in scenario.trigger_manager.triggers
             if trigger.name == name]
    if len(found) != 1:
        raise FixError(f'expected exactly one trigger named "{name}", found {len(found)}')
    return found[0]


def gaia_creates(trigger):
    return [effect for effect in trigger.effects
            if effect.effect_type == 11 and effect.source_player == GAIA]


def sibling(scenario, reference_id):
    for unit in scenario.unit_manager.units[GAIA]:
        if unit.reference_id == reference_id:
            return unit
    raise FixError(f"map-placed sibling {reference_id} is gone")


def apply(scenario):
    placed = {}
    for trigger_name, spawns in SPAWNS.items():
        trigger = trigger_by_name(scenario, trigger_name)
        creates = gaia_creates(trigger)
        seen = sorted((effect.object_list_unit_id, effect.location_x, effect.location_y)
                      for effect in creates)
        want = sorted(spawns)
        if seen != want:
            raise FixError(
                f'"{trigger_name}" creates {seen} for Gaia, expected {want}.'
                " The scenario changed; re-read it before running this.")

        ids = []
        for unit_const, x, y in spawns:
            model = sibling(scenario, SIBLINGS[unit_const])
            unit = scenario.unit_manager.add_unit(
                player=GAIA,
                unit_const=unit_const,
                tile=(x, y),
                rotation=model.rotation,
                animation_frame=model.initial_animation_frame,
                status=model.status,
                capture_flag=CaptureFlag.NEVER,
            )
            ids.append(unit.reference_id)
            placed[(unit_const, x, y)] = unit.reference_id

        trigger.effects = [effect for effect in trigger.effects if effect not in creates]

        remover_name, difficulty = REMOVERS[trigger_name]
        remover = scenario.trigger_manager.add_trigger(remover_name)
        remover.new_condition.difficulty_level(quantity=difficulty, inverted=1)
        remover.new_effect.remove_object(source_player=GAIA, selected_object_ids=ids)
    return placed


def parse_args():
    parser = argparse.ArgumentParser(
        description="Give Joan 6's difficulty siege Capture Flag Never, by placing it on the map"
                    " and removing it again where it does not belong. Writes a new file beside"
                    " the original; never overwrites it.")
    parser.add_argument("--out", default=str(SCEN_DIR / (STEM + ".fixed.aoe2scenario")),
                        help="where to write the rewritten scenario")
    return parser.parse_args()


def main():
    args = parse_args()
    source = SCEN_DIR / (STEM + ".aoe2scenario")
    out = Path(args.out)
    if out.resolve() == source.resolve():
        print("refusing to overwrite the original; pick another --out")
        return 2
    if not source.is_file():
        print(f"{source} is missing")
        return 2

    scenario = AoE2DEScenario.from_file(str(source))
    try:
        scenario.map_manager.map_color_mood = shipped_color_mood(source)
        placed = apply(scenario)
    except FixError as error:
        print(f"[FAIL] {error}")
        return 2

    scenario.write_to_file(str(out))
    print(f"wrote {out}")
    for (unit_const, x, y), reference_id in sorted(placed.items()):
        print(f"  unit {unit_const} at ({x}.5,{y}.5)  reference_id {reference_id}"
              "  capture_flag 0")
    print()
    print("Check it in the editor and swap it in. Verify first: py -3 verify.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
