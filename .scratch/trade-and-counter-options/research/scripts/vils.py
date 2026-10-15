import sys, tempfile, importlib.util
from pathlib import Path
AGE = Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago-ResourceBudget\worlds\age2de")
sys.path.insert(0, str(AGE))
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES = False
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
spec = importlib.util.spec_from_file_location("cr", AGE / "campaign" / "CampaignReader.py")
cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
V = {83,293,56,57,118,120,122,123,124,212,214,216,218,220,222,259,354,579,580,581,590,591,592}
def go(name, body):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "s.aoe2scenario"); p.write_bytes(body); s = AoE2DEScenario.from_file(str(p))
    row = []
    for pid in range(2, 9):
        pl = s.player_manager.players[pid]
        if not pl.active: continue
        us = s.unit_manager.units[pid]
        row.append(f"P{pid}: vils={sum(u.unit_const in V for u in us)} TC={sum(u.unit_const==109 for u in us)} age={pl.starting_age} w={pl.wood} g={pl.gold}")
    print(name, " | ".join(row))
for a in sys.argv[1:]:
    if a.endswith(".aoe2campaign"):
        for scn in cr.Campaign(a).scenarios: go(scn.file_name.replace(".aoe2scenario",""), scn.body)
    else: go(Path(a).stem, Path(a).read_bytes())
