import json
import os
import re
import subprocess
import sys

KIT = os.environ.get("AOE2KIT", r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe")
SCEN_DIR = os.environ.get(
    "AP_SCENARIO_DIR",
    r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files\resources\_common\scenario",
)

GOLD = 3
TRANSPORT_SHIP = 545
BOMBARD_CANNON = 36
PACKED_TREBUCHET = 331

results = []


def scen_path(stem):
    return os.path.join(SCEN_DIR, stem + ".aoe2scenario")


def run_kit(*args):
    proc = subprocess.run([KIT, *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(" ".join(args) + "\n" + proc.stdout + proc.stderr)
    return proc.stdout


def triggers(stem, grep):
    out = run_kit("scen", "triggers", scen_path(stem), "--grep", grep, "--json")
    return json.loads(out)["matches"]


def trigger_header(stem, name):
    for match in triggers(stem, name):
        if match["trigger_name"] == name and "effect_index" not in match:
            if "condition_index" not in match:
                return match
    return None


KNOWN_FIELD = re.compile(r"(\w+):(\[[^\]]*\]|\S+)")
EFFECT_HEAD = re.compile(r"^- trigger=(\d+) effect=(\d+) (\d+)/(\w+)")


def effects(stem, where):
    out = run_kit(
        "scen", "effects", scen_path(stem), "--where", where, "--limit", "200", "--text"
    )
    found = []
    current = None
    for line in out.splitlines():
        head = EFFECT_HEAD.match(line)
        if head:
            current = {
                "trigger": int(head.group(1)),
                "effect": int(head.group(2)),
                "type": int(head.group(3)),
                "type_name": head.group(4),
                "trigger_name": "",
                "fields": {},
            }
            found.append(current)
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith("trigger_name:"):
            current["trigger_name"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("known_fields: map["):
            body = stripped[len("known_fields: map[") : -1]
            for key, raw in KNOWN_FIELD.findall(body):
                if raw.startswith("["):
                    current["fields"][key] = [int(n) for n in raw[1:-1].split()]
                elif raw.lstrip("-").isdigit():
                    current["fields"][key] = int(raw)
                else:
                    current["fields"][key] = raw
    return found


def check(ticket, name, ok, detail):
    results.append((ticket, name, bool(ok), detail))


def by_trigger_name(items, name):
    return [item for item in items if item["trigger_name"] == name]


def check_58():
    stem = "AP_Joan_3"
    creates = by_trigger_name(effects(stem, "create_object"), "AP Give Boats")
    seen = sorted(
        (e["fields"].get("unit_const"), e["fields"].get("source_player"),
         tuple(e["fields"].get("location", [])))
        for e in creates
    )
    want = [(TRANSPORT_SHIP, 1, (14, 85)), (TRANSPORT_SHIP, 1, (15, 85))]
    check(
        "58",
        "AP Give Boats creates 2 Transport Ships for P1 at (14,85) and (15,85)",
        seen == want,
        f"found {seen}",
    )

    head = trigger_header(stem, "[D0] Finding Boats")
    ok = head is not None and head["effect_count"] == 1
    kinds = [
        e["type_name"]
        for e in by_trigger_name(effects(stem, "display_instructions"), "[D0] Finding Boats")
    ]
    check(
        "58",
        "[D0] Finding Boats has exactly one effect, its message",
        ok and kinds == ["display_instructions"],
        f"effect_count={head['effect_count'] if head else None} kinds={kinds}",
    )


def check_66():
    stem = "AP_Attila_3"
    tributes = effects(stem, "tribute")
    for name in ("AP Give Green TC Gold", "AP Give Red TC Gold"):
        rows = by_trigger_name(tributes, name)
        ok = len(rows) == 1 and rows[0]["fields"].get("source_player") == 4
        ok = ok and rows[0]["fields"].get("target_player") == 1
        ok = ok and rows[0]["fields"].get("resource") == GOLD
        ok = ok and rows[0]["fields"].get("quantity") == 3000
        check(
            "66",
            f"{name} tributes 3000 gold from P4 to P1",
            ok,
            f"{[r['fields'] for r in rows]}",
        )


def check_70():
    stem = "AP_Joan_6"
    creates = effects(stem, "create_object")
    want = {
        "Easy": [(BOMBARD_CANNON, (108, 120)), (PACKED_TREBUCHET, (136, 125))],
        "Easy and Moderate": [(BOMBARD_CANNON, (107, 120)), (BOMBARD_CANNON, (103, 120))],
    }
    for name, expected in want.items():
        rows = by_trigger_name(creates, name)
        seen = sorted(
            (r["fields"].get("unit_const"), tuple(r["fields"].get("location", [])))
            for r in rows
        )
        owners = {r["fields"].get("source_player", 0) for r in rows}
        head = trigger_header(stem, name)
        check(
            "70",
            f"{name} spawns its siege as Gaia",
            seen == sorted(expected) and owners == {0},
            f"units={seen} owners={sorted(owners)}",
        )
        check(
            "70",
            f"{name} is still enabled",
            head is not None and head["enabled"] == 1,
            f"enabled={head['enabled'] if head else None}",
        )

    grants = {
        "AP Give Artillery": ((99, 114), (113, 123), [(108, 120), (107, 120), (103, 120)]),
        "AP Give Army": ((126, 114), (143, 129), [(136, 125)]),
    }
    for name, (low, high, tiles) in grants.items():
        inside = all(
            low[0] <= x <= high[0] and low[1] <= y <= high[1] for x, y in tiles
        )
        check("70", f"{name} area covers its spawn tiles", inside, f"{tiles} in {low}-{high}")


def check_68():
    stem = "AP_Joan_5"
    head = trigger_header(stem, "AP Victory")
    conditions = [] if head is None else head["condition_data"]
    pairs = sorted(
        (c["known_fields"].get("variable"), c["known_fields"].get("quantity"))
        for c in conditions
    )

    writers = {}
    for row in effects(stem, "change_variable"):
        var = row["fields"].get("variable")
        writers.setdefault(var, []).append((row["trigger_name"], row["fields"].get("operation")))

    escorted = sorted({name for name, _ in writers.get(1, [])})
    joan = sorted({name for name, _ in writers.get(2, [])})

    check(
        "68",
        "var 1 RefugeesEscorted is written only by the Refugees in Area counters",
        all(name.startswith("Refugees in Area") for name in escorted) and len(escorted) == 7,
        f"{escorted}",
    )
    check(
        "68",
        "var 2 ObjectiveReached is written only by Joan in Area",
        joan == ["Joan in Area"],
        f"{joan}",
    )
    joan_head = trigger_header(stem, "Joan in Area")
    check(
        "68",
        "Joan in Area does not loop, so var 2 cannot double-count",
        joan_head is not None and joan_head["looping"] == 0,
        f"looping={joan_head['looping'] if joan_head else None}",
    )
    check(
        "68",
        "AP Victory requires Joan (var 2 == 1) and six refugees escorted (var 1 == 6)",
        pairs == [(1, 6), (2, 1)],
        f"conditions={pairs}; var0={'RefugeesLocated' if 0 in [p[0] for p in pairs] else '-'}",
    )


def main():
    if not os.path.exists(KIT):
        print(f"aoe2kit not found at {KIT}")
        return 2
    check_58()
    check_66()
    check_70()
    check_68()

    width = max(len(name) for _, name, _, _ in results)
    failed = 0
    for ticket, name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{mark}] #{ticket}  {name.ljust(width)}  {detail}")
    print()
    print(f"{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
