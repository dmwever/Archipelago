from pathlib import Path

from ..AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from .CampaignReader import Scenario

def inject_ap(scn: Scenario):
    
    scenario = AoE2DEScenario.from_file(f"output/{scn.fileName}")

    xs_manager = scenario.xs_manager
    xs_manager.add_script(xs_file_path=Path(__file__).parent.resolve().joinpath("xsscript/AP.xs"))
    
    # Add Trigger
    trigger_manager = scenario.trigger_manager
    trigger = trigger_manager.add_trigger("Ping AP Client")
    
    trigger.looping = True
    
    write_AP = trigger.new_effect.script_call(
        message="AP_Write()"
    )
    out_file_name = f"out{scn.fileName}"
    scenario.write_to_file(filename=f"output/{out_file_name}")

def copy_ai(filename, target):
    
    scenario = AoE2DEScenario.from_file(f"output/{filename}")
    
    ai_files = scenario.sections['Files'].ai_files
    
    scenario2 = AoE2DEScenario.from_file(target)
    
    ai_files2 = scenario.sections['Files'].ai_files
    
    scenario2.sections['Files'].ai_files = ai_files
    
    pass
    
    