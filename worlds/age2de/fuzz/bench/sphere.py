"""Generate one saved seed in the current checkout and print the locations in one sphere as JSON.

Run with the checkout as cwd:  python sphere.py <yaml_dir> <seed> [sphere, default 1]
"""
import argparse
import json
import sys
import tempfile

sys.path.insert(0, ".")
yaml_dir, seed = sys.argv[1], int(sys.argv[2])
wanted = int(sys.argv[3]) if len(sys.argv) > 3 else 1
sys.argv = [sys.argv[0]]

import Main  # noqa: E402
import settings  # noqa: E402
from BaseClasses import PlandoOptions  # noqa: E402
from Generate import main as generate_main  # noqa: E402

with tempfile.TemporaryDirectory() as out:
    args = argparse.Namespace(**{
        "weights_file_path": settings.get_settings().generator.weights_file_path,
        "sameoptions": False, "player_files_path": yaml_dir, "seed": seed, "multi": 1,
        "spoiler": 1, "outputpath": out, "race": False, "meta_file_path": "meta-doesnt-exist.yaml",
        "log_level": "error", "yaml_output": 0,
        "plando": PlandoOptions.items | PlandoOptions.connections | PlandoOptions.texts
                  | PlandoOptions.bosses,
        "skip_prog_balancing": False, "skip_output": True, "csv_output": False,
        "log_time": False, "spoiler_only": False,
    })
    erargs, used_seed = generate_main(args)
    mw = Main.main(erargs, used_seed)
    spheres = list(mw.get_spheres())
    rows = sorted(
        ({"location": loc.name, "item": loc.item.name if loc.item else None} for loc in spheres[wanted]),
        key=lambda row: row["location"],
    )
    print("SPHERE " + json.dumps(rows), flush=True)
    start = sorted(item.name for item in mw.precollected_items[1])
    print("START " + json.dumps(start), flush=True)
