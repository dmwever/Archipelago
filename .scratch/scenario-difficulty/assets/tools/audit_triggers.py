"""Dump every trigger whose conditions include Difficulty Level (id 19), with all its
conditions and effects, plus any trigger/XS text mentioning difficulty. Run from Archipelago root."""
import sys, json, pathlib, re
sys.path.insert(0, r"C:\Users\DavidWever\Documents\GitHub\Archipelago\worlds\age2de")
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES = False
settings.NOTIFY_UNKNOWN_BYTES = False
settings.SHOW_STATUS_UPDATES = False if hasattr(settings, "SHOW_STATUS_UPDATES") else None
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.conditions import ConditionId
from AoE2ScenarioParser.datasets.effects import EffectId

src = pathlib.Path(r"C:\Users\DavidWever\Documents\GitHub\Ageipelago\age 2 files\resources\_common\scenario")
out = pathlib.Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago\.scratch\scenario-difficulty\assets")

CF = ["quantity", "condition_type", "comparison", "inverted", "source_player", "unit_object",
      "object_list", "object_type", "object_group", "area_x1", "area_y1", "area_x2", "area_y2",
      "timer", "variable", "technology", "attribute", "xs_function"]
EF = ["source_player", "target_player", "quantity", "object_list_unit_id", "object_type", "object_group",
      "selected_object_ids", "location_x", "location_y", "location_object_reference", "area_x1", "area_y1",
      "area_x2", "area_y2", "trigger_id", "technology", "message", "string_id", "object_attributes",
      "operation", "item_id", "variable", "message", "display_time", "diplomacy", "resource", "attack_stance",
      "armour_attack_quantity", "armour_attack_class", "number_of_units_selected", "xs_function",
      "flash_object", "max_units_affected", "object_state"]

def attrs(obj, fields):
    d = {}
    for f in fields:
        v = getattr(obj, f, None)
        if v in (None, -1, "", [], [-1]) :
            continue
        if f == "inverted" and v == 0: continue
        d[f] = v if isinstance(v, (int, str, list)) else str(v)
    return d

def name_of(enum, i):
    try: return enum(i).name
    except Exception: return str(i)

rows, xs_hits = [], []
for f in sorted(src.glob("AP_*.aoe2scenario")):
    sc = AoE2DEScenario.from_file(str(f))
    tm = sc.trigger_manager
    trigs = tm.triggers
    for t in trigs:
        conds = t.conditions
        if not any(c.condition_type == ConditionId.DIFFICULTY_LEVEL for c in conds):
            continue
        rows.append({
            "scenario": f.stem, "trigger_id": t.trigger_id, "name": t.name, "enabled": t.enabled,
            "looping": t.looping, "description": (t.description or "")[:200],
            "conditions": [{"type": name_of(ConditionId, c.condition_type), **attrs(c, CF)} for c in conds],
            "effects": [{"type": name_of(EffectId, e.effect_type), **attrs(e, EF)} for e in t.effects],
        })
    # any other mention of difficulty in trigger names / XS
    for t in trigs:
        blob = " ".join([t.name or "", t.description or ""] +
                        [getattr(e, "message", "") or "" for e in t.effects] +
                        [getattr(c, "xs_function", "") or "" for c in t.conditions] +
                        [getattr(e, "xs_function", "") or "" for e in t.effects])
        if re.search(r"difficult|easy|hard\b", blob, re.I) and not any(r["scenario"] == f.stem and r["trigger_id"] == t.trigger_id for r in rows):
            xs_hits.append({"scenario": f.stem, "trigger_id": t.trigger_id, "name": t.name, "text": blob[:300]})
    xs = getattr(sc, "xs_manager", None)
    script = getattr(xs, "script", "") if xs else ""
    if script and re.search(r"[Dd]ifficult", script):
        xs_hits.append({"scenario": f.stem, "xs": [l for l in script.splitlines() if re.search(r"[Dd]ifficult", l)]})

(out / "difficulty-triggers.json").write_text(json.dumps({"triggers": rows, "other_mentions": xs_hits}, indent=1, default=str))
print(len(rows), len(xs_hits))
