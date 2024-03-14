from .. import APGOWorld

options_to_exclude = ["progression_balancing", "accessibility", "start_inventory", "start_hints", "death_link"]
options_to_include = [option for option_name, option in APGOWorld.options_dataclass.type_hints.items()
                      if option_name not in options_to_exclude]
