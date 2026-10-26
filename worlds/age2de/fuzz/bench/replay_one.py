"""Generate one saved seed in the current Archipelago checkout and print one JSON line of metrics.

Run with the checkout as cwd:  python replay_one.py <yaml_dir> <seed>
"""
import json
import sys
import time

sys.path.insert(0, ".")
yaml_dir, seed = sys.argv[1], int(sys.argv[2])
sys.argv = [sys.argv[0]]

import Generate  # noqa: E402
import Main  # noqa: E402
from Generate import main as generate_main  # noqa: E402
from BaseClasses import PlandoOptions  # noqa: E402
import settings  # noqa: E402
import argparse  # noqa: E402
import tempfile  # noqa: E402

row = {"seed": seed, "ok": False}
start = time.perf_counter()
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
    try:
        erargs, used_seed = generate_main(args)
        mw = Main.main(erargs, used_seed)
        row["ok"] = True
        row["seconds"] = round(time.perf_counter() - start, 2)
        spheres = list(mw.get_spheres())
        row["spheres"] = len(spheres)
        row["sphere1"] = len(spheres[1]) if len(spheres) > 1 else 0
        row["sphere0"] = len(spheres[0]) if spheres else 0
    except BaseException as e:  # noqa: BLE001
        row["seconds"] = round(time.perf_counter() - start, 2)
        row["error"] = f"{type(e).__name__}: {e}"[:300]
print("ROW " + json.dumps(row), flush=True)
