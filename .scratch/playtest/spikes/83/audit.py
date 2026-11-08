import json
import os
import re
import subprocess
import sys

KIT = os.environ.get("AOE2KIT", r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe")
SCEN_DIR = os.environ.get(
    "AP_SCENARIO_DIR",
    r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files\resources\_common\scenario")

STEMS = [f"AP_{campaign}_{chapter}"
         for campaign in ("Attila", "Joan", "Genghis") for chapter in range(1, 7)]

GAIA = 0
KNOWN_FIELD = re.compile(r"(\w+):(\[[^\]]*\]|\S+)")
EFFECT_HEAD = re.compile(r"^- trigger=(\d+) effect=(\d+) (\d+)/(\w+)")


def run_kit(*args):
    proc = subprocess.run([KIT, *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(" ".join(args) + "\n" + proc.stdout + proc.stderr)
    return proc.stdout


def effects(stem, where):
    out = run_kit("scen", "effects", os.path.join(SCEN_DIR, stem + ".aoe2scenario"),
                  "--where", where, "--limit", "500", "--text")
    found = []
    current = None
    for line in out.splitlines():
        head = EFFECT_HEAD.match(line)
        if head:
            current = {"trigger": int(head.group(1)), "effect": int(head.group(2)),
                       "type_name": head.group(4), "trigger_name": "", "fields": {}}
            found.append(current)
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith("trigger_name:"):
            current["trigger_name"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("known_fields: map["):
            body = stripped[len("known_fields: map["):-1]
            for key, raw in KNOWN_FIELD.findall(body):
                if raw.startswith("["):
                    current["fields"][key] = [int(n) for n in raw[1:-1].split()]
                elif raw.lstrip("-").isdigit():
                    current["fields"][key] = int(raw)
                else:
                    current["fields"][key] = raw
    return found


def trigger_gates(stem):
    data = json.loads(run_kit("scen", "triggers",
                              os.path.join(SCEN_DIR, stem + ".aoe2scenario"), "--limit", "4000"))
    matches = data.get("matches") or []
    if data.get("total_matches", len(matches)) > len(matches):
        raise RuntimeError(f"{stem}: trigger listing was truncated")
    gates = {}
    for match in matches:
        names = []
        for condition in match.get("condition_data") or []:
            name = condition.get("type_name", "?")
            xs = (condition.get("known_fields") or {}).get("xs_function")
            names.append(f"{name}:{xs.rstrip(';()')}" if xs else name)
        gates[match["trigger_index"]] = names
    return gates


def inside(area, x, y):
    return area[0] <= x <= area[2] and area[1] <= y <= area[3]


def audit(stem):
    gates = trigger_gates(stem)
    spawns = [row for row in effects(stem, "create_object")
              if row["fields"].get("source_player", 0) == GAIA]
    for spawn in spawns:
        spawn["gate"] = gates.get(spawn["trigger"], [])
    handovers = [row for row in effects(stem, "change_ownership")
                 if row["fields"].get("source_player") == GAIA]

    rows = []
    for spawn in spawns:
        tile = spawn["fields"].get("location", [])
        unit = spawn["fields"].get("unit_const")
        covering = []
        for grant in handovers:
            area = grant["fields"].get("area")
            if area is None or not tile or not inside(area, tile[0], tile[1]):
                continue
            listed = grant["fields"].get("object_list_unit_id")
            if listed is not None and listed not in (-1, unit):
                continue
            covering.append(grant)
        rows.append((spawn, covering))
    return rows, handovers


def main():
    total_spawns = 0
    total_covered = 0
    for stem in STEMS:
        rows, handovers = audit(stem)
        if not rows:
            continue
        print(f"## {stem}  ({len(handovers)} Gaia->player handover effect(s))")
        for spawn, covering in rows:
            total_spawns += 1
            tile = spawn["fields"].get("location", [])
            unit = spawn["fields"].get("unit_const")
            gate = ", ".join(spawn["gate"]) or "nothing"
            item_gated = any(part.startswith("script_call:Has") for part in spawn["gate"])
            if covering and not item_gated:
                total_covered += 1
                for grant in covering:
                    filters = {key: value for key, value in grant["fields"].items()
                               if key in ("object_type", "object_list_unit_id")}
                    print(f"  IN SCOPE  unit {unit} at {tile}"
                          f'  spawned by "{spawn["trigger_name"]}" on [{gate}]'
                          f'  but handed over by "{grant["trigger_name"]}"'
                          f" -> p{grant['fields'].get('target_player')}"
                          f"  area={grant['fields'].get('area')}"
                          + (f"  filters={filters}" if filters else ""))
            elif covering:
                print(f"  item-gated unit {unit} at {tile}"
                      f'  spawned by "{spawn["trigger_name"]}" on [{gate}]'
                      "  - the item is already required for it to exist")
            else:
                print(f"  not AP    unit {unit} at {tile}"
                      f'  spawned by "{spawn["trigger_name"]}" on [{gate}]'
                      "  (no AP handover covers that tile)")
        print()
    print(f"{total_covered} of {total_spawns} Gaia create_object effects land where an AP"
          f" handover would otherwise deliver them, without the item gating the spawn")
    return 0


if __name__ == "__main__":
    sys.exit(main())
