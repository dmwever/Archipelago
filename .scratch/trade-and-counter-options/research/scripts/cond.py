import sys, tempfile, importlib.util
from pathlib import Path
AGE = Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago-ResourceBudget\worlds\age2de")
sys.path.insert(0, str(AGE))
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES = False
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.conditions import ConditionId
spec = importlib.util.spec_from_file_location("cr", AGE / "campaign" / "CampaignReader.py")
cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
want = {"AP_Attila_1": [153], "AP_Joan_2": [55, 70, 68], "AP_Genghis_4": [33]}
def go(name, body):
    if name not in want: return
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "s.aoe2scenario"); p.write_bytes(body); s = AoE2DEScenario.from_file(str(p))
    for t in s.trigger_manager.triggers:
        if t.trigger_id in want[name]:
            print(name, t.trigger_id, t.name)
            for c in t.conditions:
                print("   ", ConditionId(c.condition_type).name, "xs=", getattr(c, "xs_function", None), "p=", c.source_player, "q=", c.quantity, "obj=", c.object_list, "inv=", c.inverted)
for a in sys.argv[1:]:
    if a.endswith(".aoe2campaign"):
        for scn in cr.Campaign(a).scenarios: go(scn.file_name.replace(".aoe2scenario",""), scn.body)
    else: go(Path(a).stem, Path(a).read_bytes())
