"""Generate one seed and print what the budget says, to compare across processes.

Run with the checkout as cwd:  python determinism.py <yaml_dir> <seed>
String hashing is salted per process, so anything that depends on set or dict order over strings
only shows up between runs, never within one.
"""
import argparse
import json
import sys
import tempfile

sys.path.insert(0, ".")
yaml_dir, seed = sys.argv[1], int(sys.argv[2])
sys.argv = [sys.argv[0]]

import Main  # noqa: E402
import settings  # noqa: E402
from BaseClasses import CollectionState, PlandoOptions  # noqa: E402
from Generate import main as generate_main  # noqa: E402

with tempfile.TemporaryDirectory() as out:
    args = argparse.Namespace(**{
        "weights_file_path": settings.get_settings().generator.weights_file_path,
        "sameoptions": False, "player_files_path": yaml_dir, "seed": seed, "multi": 1,
        "spoiler": 0, "outputpath": out, "race": False, "meta_file_path": "meta-doesnt-exist.yaml",
        "log_level": "error", "yaml_output": 0,
        "plando": PlandoOptions.items | PlandoOptions.connections | PlandoOptions.texts
                  | PlandoOptions.bosses,
        "skip_prog_balancing": False, "skip_output": True, "csv_output": False,
        "log_time": False, "spoiler_only": False,
    })
    erargs, used_seed = generate_main(args)
    mw = Main.main(erargs, used_seed)
    world = mw.worlds[1]
    from worlds.age2de.locations.Scenarios import Age2ScenarioData
    from worlds.age2de.locations.Buildings import Age2BuildingData
    from worlds.age2de.logic.budget.BudgetTotal import BudgetTotal

    order = world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1).budget.order
    empty = CollectionState(mw)
    resolved = BudgetTotal(scenario=Age2ScenarioData.AP_ATTILA_1,
                           location=Age2BuildingData.MARKET).resolve(world)
    report = {
        "sample": sorted(location.name for location in world.pool.budget.entries),
        "attila1_order": [entry.location.name for entry in order.order],
        "market_total_empty": dict((r.name, a) for r, a in resolved.table.total(empty).cost)
            if hasattr(resolved, "table") else None,
        "market_by_mask": [
            {"waivers_on": [w.description for bit, w in enumerate(resolved.table.waivers) if mask >> bit & 1],
             "cost": dict((r.name, a) for r, a in total.cost)}
            for mask, total in enumerate(resolved.table.totals_by_mask)
        ] if hasattr(resolved, "table") else None,
        "market_per_scenario": {
            sc.name: ([sorted(set(tuple((r.name, a) for r, a in t.cost) for t in BudgetTotal(scenario=sc, location=Age2BuildingData.MARKET).resolve(world).table.totals_by_mask))]
                      if hasattr(BudgetTotal(scenario=sc, location=Age2BuildingData.MARKET).resolve(world), "table") else "not in budget")
            for sc in world.pool.scenarios.included
        },
        "ut_seed": world.fill_slot_data().get("ut_seed"),
        "matching_locations": sorted({
            entry.location.location_name
            for entry in order.order
            if hasattr(entry.location, "location_name")
            and hasattr((bt := BudgetTotal(scenario=Age2ScenarioData.AP_ATTILA_1, location=entry.location).resolve(world)), "table")
            and dict((r.name, a) for r, a in bt.table.total(empty).cost) == {"WOOD": 960, "FOOD": 650, "STONE": 100}
        }),
        "placements": sorted(f"{loc.name}={loc.item.name}" for loc in mw.get_locations(1) if loc.item)[:40],
    }
    print("REPORT " + json.dumps(report), flush=True)
