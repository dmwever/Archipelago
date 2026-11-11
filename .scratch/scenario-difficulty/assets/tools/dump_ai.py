"""Extract every embedded AI script from the AP scenarios into ../ai-scripts/ as
<scenario>_p<N>.per plus index.json. The output is proprietary game content and is gitignored;
rerun this whenever ai-scripts/ is missing. Needs the Ageipelago repo checked out beside Archipelago."""
import sys, json, pathlib
sys.path.insert(0, r"C:\Users\DavidWever\Documents\GitHub\Archipelago\worlds\age2de")
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES = False
settings.NOTIFY_UNKNOWN_BYTES = False
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
src = pathlib.Path(r"C:\Users\DavidWever\Documents\GitHub\Ageipelago\age 2 files\resources\_common\scenario")
out = pathlib.Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago\.scratch\scenario-difficulty\assets\ai-scripts")
out.mkdir(exist_ok=True)
index = []
for f in sorted(src.glob("AP_*.aoe2scenario")):
    sc = AoE2DEScenario.from_file(str(f))
    for p in sc.player_manager.players:
        s = p.ai_script or ""
        if not s.strip():
            continue
        name = f"{f.stem}_p{int(p.player_id)}.per"
        (out / name).write_text(s, encoding="utf-8", newline="")
        attrs = {a: str(getattr(p, a, None)) for a in ("personality", "ai_type", "active", "human")}
        index.append({"scenario": f.stem, "player": int(p.player_id), "file": name, "len": len(s), **attrs})
(out / "index.json").write_text(json.dumps(index, indent=1))
print(len(index))
