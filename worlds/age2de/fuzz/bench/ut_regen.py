"""Rebuild a seed the way Universal Tracker does - a seed of its own, options from the YAML, the
server's slot data passed through - and print Build Market's budget per scenario.

Run with the checkout as cwd:  python ut_regen.py <yaml_dir> <multidata zip>
"""
import json
import pickle
import random
import sys
import zipfile
import zlib

sys.path.insert(0, ".")
yaml_dir, archive = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0]]

from BaseClasses import CollectionState, MultiWorld  # noqa: E402
from Generate import main as generate_main  # noqa: E402
from worlds import AutoWorld  # noqa: E402

with zipfile.ZipFile(archive) as z:
    name = next(n for n in z.namelist() if n.endswith(".archipelago"))
    multidata = pickle.loads(zlib.decompress(z.read(name)[1:]))
slot_data = multidata["slot_data"][1]

import Generate  # noqa: E402
args = Generate.mystery_argparse()
args.player_files_path = yaml_dir
args.skip_output = True
g_args, seed = generate_main(args)

game = g_args.game[1]
multiworld = MultiWorld(1)
multiworld.generation_is_fake = True
multiworld.re_gen_passthrough = {game: slot_data}
multiworld.set_seed(random.getrandbits(64), False, None)   # UT's own, never the server's
multiworld.game = g_args.game.copy()
multiworld.player_name = g_args.name.copy()
multiworld.set_options(g_args)
multiworld.state = CollectionState(multiworld)
for step in ("generate_early", "create_regions", "create_items", "set_rules"):
    AutoWorld.call_all(multiworld, step)

world = multiworld.worlds[1]
from worlds.age2de.locations.Buildings import Age2BuildingData  # noqa: E402
from worlds.age2de.logic.budget.BudgetTotal import BudgetTotal  # noqa: E402
report = {"ut_seed_used": world.ut_seed, "ut_seed_served": slot_data.get("ut_seed"), "market": {}}
for scenario in world.pool.scenarios.included:
    resolved = BudgetTotal(scenario=scenario, location=Age2BuildingData.MARKET).resolve(world)
    report["market"][scenario.name] = (
        sorted({tuple((r.name, a) for r, a in t.cost) for t in resolved.table.totals_by_mask})
        if hasattr(resolved, "table") else "not in budget")
print("REPORT " + json.dumps(report), flush=True)
