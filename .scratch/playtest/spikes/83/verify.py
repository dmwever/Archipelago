import argparse
import os
import sys
from pathlib import Path

AGE2DE = Path(os.environ.get(
    "AP_AGE2DE", r"C:\Users\dmwev\Documents\GitHub\Archipelago\worlds\age2de"))
sys.path.insert(0, str(AGE2DE))

from AoE2ScenarioParser.helper import printers

printers.rprint = lambda *args, **kwargs: None
printers.s_print = lambda *args, **kwargs: None

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

import fix

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def load(path):
    return AoE2DEScenario.from_file(str(path))


def never_count(scenario):
    return sum(1 for unit in scenario.unit_manager.units[fix.GAIA] if unit.capture_flag == 0)


def at_tile(scenario, player, unit_const, x, y):
    for unit in scenario.unit_manager.units[player]:
        if unit.unit_const == unit_const and int(unit.x) == x and int(unit.y) == y:
            return unit
    return None


def trigger_names(scenario):
    return [trigger.name for trigger in scenario.trigger_manager.triggers]


def main():
    parser = argparse.ArgumentParser(
        description="Read the rewritten Joan 6 back and prove the fix landed.")
    parser.add_argument("--out", default=str(fix.SCEN_DIR / (fix.STEM + ".fixed.aoe2scenario")))
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_file():
        print(f"no rewritten scenario at {out}; run fix.py first")
        return 2

    before = load(fix.SCEN_DIR / (fix.STEM + ".aoe2scenario"))
    after = load(out)

    base = never_count(before)
    now = never_count(after)
    check("Gaia's Capture Flag Never count goes from 60 to 64",
          base == 60 and now == 64, f"{base} -> {now}")

    wanted = [(unit_const, x, y) for spawns in fix.SPAWNS.values() for unit_const, x, y in spawns]
    for unit_const, x, y in wanted:
        unit = at_tile(after, fix.GAIA, unit_const, x, y)
        check(f"unit {unit_const} stands at ({x},{y}) for Gaia with Capture Flag Never",
              unit is not None and unit.capture_flag == 0,
              f"capture_flag={unit.capture_flag}" if unit else "not on the map")

    for trigger_name in fix.SPAWNS:
        trigger = fix.trigger_by_name(after, trigger_name)
        check(f'"{trigger_name}" creates nothing for Gaia any more',
              not fix.gaia_creates(trigger), f"{len(fix.gaia_creates(trigger))} left")

    before_names = trigger_names(before)
    after_names = trigger_names(after)
    check("no existing trigger moved, so trigger ids still point where they did",
          after_names[:len(before_names)] == before_names,
          f"{len(before_names)} -> {len(after_names)}")

    for trigger_name, (remover_name, difficulty) in fix.REMOVERS.items():
        if remover_name not in after_names:
            check(f'"{remover_name}" exists', False, "missing")
            continue
        remover = fix.trigger_by_name(after, remover_name)
        condition = remover.conditions[0] if len(remover.conditions) == 1 else None
        check(f'"{remover_name}" fires exactly when "{trigger_name}" does not',
              condition is not None and condition.condition_type == 19
              and condition.quantity == difficulty and condition.inverted == 1,
              f"conditions={len(remover.conditions)}"
              + (f" quantity={condition.quantity} inverted={condition.inverted}"
                 if condition else ""))

        effect = remover.effects[0] if len(remover.effects) == 1 else None
        expected = sorted(
            at_tile(after, fix.GAIA, unit_const, x, y).reference_id
            for unit_const, x, y in fix.SPAWNS[trigger_name])
        check(f'"{remover_name}" removes exactly the pieces "{trigger_name}" used to create',
              effect is not None and effect.effect_type == 15
              and effect.source_player == fix.GAIA
              and sorted(effect.selected_object_ids) == expected,
              f"selected={sorted(effect.selected_object_ids) if effect else None}"
              f" expected={expected}")

    shipped = fix.shipped_color_mood(fix.SCEN_DIR / (fix.STEM + ".aoe2scenario"))
    written = fix.shipped_color_mood(out)
    check("the map colour mood is not quietly lowercased by the round trip",
          written == shipped, f"{shipped!r} -> {written!r}")

    before_refs = {unit.reference_id
                   for section in before.unit_manager.units for unit in section}
    after_refs = {unit.reference_id
                  for section in after.unit_manager.units for unit in section}
    check("every existing reference id survives, so trigger object references still resolve",
          before_refs <= after_refs, f"{len(before_refs)} -> {len(after_refs)}")

    width = max(len(name) for name, _, _ in results)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name.ljust(width)}  {detail}")
    print()
    print(f"{len(results) - failed}/{len(results)} passed")
    print()
    print("Structure only. The editor and the game are still the oracle:"
          " open it, check the four pieces, then swap it in.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
