"""For one saved seed: which precollected buildings could any included scenario's civilisation build?

Run with the checkout as cwd:  python start_check.py <yaml_dir> <seed>
"""
import argparse
import sys
import tempfile

sys.path.insert(0, ".")
yaml_dir, seed = sys.argv[1], int(sys.argv[2])
sys.argv = [sys.argv[0]]

import Main  # noqa: E402
import settings  # noqa: E402
from BaseClasses import PlandoOptions  # noqa: E402
from Generate import main as generate_main  # noqa: E402

with tempfile.TemporaryDirectory() as out:
    args = argparse.Namespace(**{
        "weights_file_path": settings.get_settings().generator.weights_file_path,
        "sameoptions": False, "player_files_path": yaml_dir, "seed": seed, "multi": 1,
        "spoiler": 0, "outputpath": out, "race": False, "meta_file_path": "meta-doesnt-exist.yaml",
        "log_level": "error", "yaml_output": 0,
        "plando": PlandoOptions.items | PlandoOptions.connections | PlandoOptions.texts
                  | PlandoOptions.bosses,
        "skip_prog_balancing": True, "skip_output": True, "csv_output": False,
        "log_time": False, "spoiler_only": False,
    })
    erargs, used_seed = generate_main(args)
    mw = Main.main(erargs, used_seed)
    world = mw.worlds[1]
    from worlds.age2de.locations.Buildings import Age2BuildingData

    names = {item.name for item in mw.precollected_items[1]}
    scenarios = world.rules.logic.scenarios
    for building in Age2BuildingData:
        if building.item.item_name not in names:
            continue
        builders = [s.scenario.scenario_name for s in scenarios if s.civilization.can_build(building)]
        print(f"CHECK {building.name:<18} buildable in: {builders or 'none'}", flush=True)
