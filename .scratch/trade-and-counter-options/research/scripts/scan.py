import sys, tempfile, json
from pathlib import Path
from collections import Counter

AGE = Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago-ResourceBudget\worlds\age2de")
sys.path.insert(0, str(AGE))
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES = False
settings.NOTIFY_UNKNOWN_BYTES = False
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.effects import EffectId

sys.path.insert(0, str(AGE / "campaign"))
import importlib.util
spec = importlib.util.spec_from_file_location("cr", AGE / "campaign" / "CampaignReader.py")
cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)

MARKET = {84, 116, 137}
DOCK = {45, 47, 51, 133, 805, 806, 807, 808, 1189, 2172}
COLORS = ["blue", "red", "green", "yellow", "cyan", "purple", "grey", "orange"]
STANCE = {0: "ally", 1: "neutral", 2: "?2", 3: "enemy"}

def scan(label, body):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "s.aoe2scenario"); p.write_bytes(body)
        s = AoE2DEScenario.from_file(str(p))
    pm = s.player_manager
    um = s.unit_manager
    out = {"label": label, "players": []}
    p1 = pm.players[PlayerId.ONE]
    for pid in range(1, 9):
        pl = pm.players[pid]
        if not pl.active:
            continue
        units = um.units[pid]
        c = Counter(u.unit_const for u in units)
        mk = {k: v for k, v in c.items() if k in MARKET}
        dk = {k: v for k, v in c.items() if k in DOCK}
        out["players"].append(dict(
            pid=pid, name=pl.tribe_name, color=COLORS[pl.color] if 0 <= pl.color < 8 else pl.color,
            p1_to=STANCE.get(p1.diplomacy[pid - 1], p1.diplomacy[pid - 1]) if pid != 1 else "-",
            to_p1=STANCE.get(pl.diplomacy[0], pl.diplomacy[0]) if pid != 1 else "-",
            market=mk, dock=dk))
    # gaia
    c = Counter(u.unit_const for u in um.units[0])
    out["gaia"] = {"market": {k: v for k, v in c.items() if k in MARKET}, "dock": {k: v for k, v in c.items() if k in DOCK}}
    # change diplomacy effects
    dip = []
    for t in s.trigger_manager.triggers:
        for e in t.effects:
            if e.effect_type == EffectId.CHANGE_DIPLOMACY:
                dip.append(f"{t.name!r}(en={t.enabled}): P{e.source_player}->P{e.target_player}={STANCE.get(e.diplomacy, e.diplomacy)}")
    out["dip_triggers"] = dip
    return out

results = []
for kind, path in [a.split("=", 1) for a in sys.argv[1:]]:
    if path.endswith(".aoe2campaign"):
        camp = cr.Campaign(path)
        for scn in camp.scenarios:
            results.append(scan(f"{kind}:{scn.file_name}", scn.body))
    else:
        results.append(scan(f"{kind}:{Path(path).name}", Path(path).read_bytes()))
print(json.dumps(results, default=str))
