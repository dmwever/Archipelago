import sys, tempfile, json, importlib.util
from pathlib import Path

AGE = Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago-ResourceBudget\worlds\age2de")
sys.path.insert(0, str(AGE))
from AoE2ScenarioParser import settings
settings.PRINT_STATUS_UPDATES = False
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.effects import EffectId

spec = importlib.util.spec_from_file_location("cr", AGE / "campaign" / "CampaignReader.py")
cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)

TARGET = {84: "Market", 45: "Dock", 805: "DockAddon", 128: "TradeCart", 204: "TradeCartFull", 17: "TradeCog"}
STANCE = {0: "ally", 1: "neutral", 3: "enemy"}
OUTDIR = Path(sys.argv[1])

def valid(v):
    return v is not None and v != -1

def scan(label, body):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "s.aoe2scenario"); p.write_bytes(body)
        s = AoE2DEScenario.from_file(str(p))
    lines = [f"##### {label}"]
    pm = s.player_manager
    for pid in range(1, 9):
        pl = pm.players[pid]
        if not pl.active:
            continue
        script = pl.ai_script or ""
        fn = OUTDIR / f"{label.replace(':', '_')}_P{pid}.per"
        if script.strip():
            fn.write_text(script, encoding="utf-8")
        dis = [b for b in (pl.disabled_buildings or []) if b in TARGET]
        lines.append(f"P{pid} ai_name={pl.personality!r} ai_type={pl.ai_type} embedded_len={len(script)} disabled_target_bldgs={dis}")
    # unit reference id -> (player, const)
    ref = {}
    for pid in range(9):
        for u in s.unit_manager.units[pid]:
            ref[u.reference_id] = (pid, u.unit_const)
    trigs = s.trigger_manager.triggers
    activators = {}
    for t in trigs:
        for e in t.effects:
            if e.effect_type in (EffectId.ACTIVATE_TRIGGER, EffectId.DEACTIVATE_TRIGGER) and valid(e.trigger_id):
                activators.setdefault(e.trigger_id, []).append(("+" if e.effect_type == EffectId.ACTIVATE_TRIGGER else "-") + f"[{t.trigger_id}]{t.name}")
    for t in trigs:
        hits = []
        for e in t.effects:
            et = e.effect_type
            name = EffectId(et).name if et in EffectId._value2member_map_ else str(et)
            ids = {getattr(e, "object_list_unit_id", None), getattr(e, "object_list_unit_id_2", None)}
            sel = [ref.get(i) for i in (e.selected_object_ids or [])]
            sel_t = [f"P{p}:{TARGET[c]}" for p, c in [x for x in sel if x] if c in TARGET]
            tid = [TARGET[i] for i in ids if i in TARGET]
            if et == EffectId.CHANGE_DIPLOMACY:
                hits.append(f"DIPLO P{e.source_player}->P{e.target_player}={STANCE.get(e.diplomacy, e.diplomacy)}")
            elif et == EffectId.AI_SCRIPT_GOAL:
                hits.append(f"AI_GOAL P{e.player_source if hasattr(e,'player_source') else e.source_player} goal={e.ai_script_goal}")
            elif et == EffectId.SCRIPT_CALL:
                msg = (e.message or "").strip().replace("\n", " ")
                if any(k in msg for k in ("84", "45", "Market", "Dock", "Ownership", "Diplom")):
                    hits.append(f"XS {msg[:120]}")
            elif tid or sel_t:
                area = ""
                if valid(getattr(e, "area_x1", None)):
                    area = f" area=({e.area_x1},{e.area_y1})-({e.area_x2},{e.area_y2})"
                hits.append(f"{name} ids={tid} sel={sel_t} P{e.source_player}->P{e.target_player}{area}")
            elif et == EffectId.CHANGE_OWNERSHIP:
                # area or class based ownership change without a target unit: check area for markets/docks
                inarea = []
                if valid(getattr(e, "area_x1", None)):
                    for pid in range(9):
                        if valid(e.source_player) and pid != e.source_player:
                            continue
                        for u in s.unit_manager.units[pid]:
                            if u.unit_const in TARGET and (not valid(e.object_list_unit_id) or e.object_list_unit_id == u.unit_const) and e.area_x1 <= u.x <= e.area_x2 + 1 and e.area_y1 <= u.y <= e.area_y2 + 1:
                                inarea.append(f"P{pid}:{TARGET[u.unit_const]}")
                if inarea or not sel:
                    hits.append(f"CHANGE_OWNERSHIP(generic) unit={e.object_list_unit_id} P{e.source_player}->P{e.target_player} area=({e.area_x1},{e.area_y1})-({e.area_x2},{e.area_y2}) targets_in_area={inarea}")
        if hits:
            lines.append(f"T[{t.trigger_id}] {t.name!r} enabled={t.enabled} looping={t.looping} activated_by={activators.get(t.trigger_id, [])}")
            lines += ["    " + h for h in hits]
            if any("P" in h and (":Market" in h or ":Dock" in h) for h in hits):
                from AoE2ScenarioParser.datasets.conditions import ConditionId
                for c in t.conditions:
                    cn = ConditionId(c.condition_type).name if c.condition_type in ConditionId._value2member_map_ else c.condition_type
                    lines.append(f"      COND {cn} var={c.variable} q={c.quantity} cmp={c.comparison} unit={c.object_list} p={c.source_player} inv={c.inverted}")
    return "\n".join(lines)

for kind, path in [a.split("=", 1) for a in sys.argv[2:]]:
    if path.endswith(".aoe2campaign"):
        for scn in cr.Campaign(path).scenarios:
            print(scan(f"{kind}:{scn.file_name.replace('.aoe2scenario','')}", scn.body))
    else:
        print(scan(f"{kind}:{Path(path).stem}", Path(path).read_bytes()))
