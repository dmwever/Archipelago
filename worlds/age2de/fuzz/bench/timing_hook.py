"""Fuzzer hook: one JSON line per generation with its wall time and the options that shape it."""
import glob
import json
import os
import shutil
import time

from fuzz import OUT_DIR, BaseHook

SHAPE = ("enabled_campaigns", "starting_campaigns", "scenario_branching", "shuffle_unique_techs",
         "existing_techs", "include_unique_units", "unitsanity_items", "caveman", "local_start",
         "trap_difficulty", "tech_behavior")


class Hook(BaseHook):
    def before_generate(self, args):
        self.yaml_dir = args.player_files_path
        self.start = time.perf_counter()

    def after_generate(self, mw, _output_path):
        row = {"seconds": round(time.perf_counter() - self.start, 2), "ok": mw is not None}
        if mw is not None:
            row["seed"] = mw.seed
            kept = os.path.join(OUT_DIR, "yamls", str(mw.seed))
            os.makedirs(kept, exist_ok=True)
            for yaml in glob.glob(os.path.join(self.yaml_dir, "*.yaml")):
                shutil.copy(yaml, kept)
            row["locations"] = len(mw.get_locations())
            world = next(iter(mw.worlds.values()))
            options = world.options
            for name in SHAPE:
                value = getattr(options, name, None)
                if value is not None:
                    value = value.value
                    row[name] = sorted(value) if isinstance(value, (set, frozenset)) else value
        with open(os.path.join(OUT_DIR, "timings.jsonl"), "a", encoding="utf-8") as out:
            out.write(json.dumps(row) + "\n")
