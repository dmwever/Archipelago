import sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\DavidWever\Documents\GitHub\Archipelago-ResourceBudget\worlds\age2de")
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES=False
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
s=AoE2DEScenario.from_file(sys.argv[1])
mm=s.map_manager; W=mm.map_size
for p in range(9):
    for u in s.unit_manager.units[p]:
        if u.unit_const in (805,45):
            x,y=int(u.x),int(u.y)
            ts=set()
            for dx in range(-2,3):
                for dy in range(-2,3):
                    try: ts.add(mm.get_tile(x+dx,y+dy).terrain_id)
                    except Exception: pass
            print(p,u.unit_const,x,y,sorted(ts))
