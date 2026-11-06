import json
import subprocess
import sys
from pathlib import Path

KIT = Path(r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe")

FIELDS = 8

REC = {1: "BOOT", 2: "MAKE", 3: "SCAN", 4: "RESULT", 5: "OPEN", 6: "DONE"}
CASE = {0: "spawn 35", 1: "spawn 1258", 2: "trained at a Siege Workshop"}
RAM = {35: "35 legacy", 1258: "1258 DE", 422: "422 Capped", 548: "548 Siege"}


def decode(path):
    out = subprocess.run([str(KIT), "xsdat", "decode", str(path), "--json"],
                         capture_output=True, text=True)
    if out.returncode != 0 and not out.stdout:
        sys.exit("kit failed: " + out.stderr.strip())
    return json.loads(out.stdout)


def records(report):
    ints = [v.get("int") for v in report["decode"]["values"]]
    header = report["decode"]["values"][0].get("string")
    version, capacity = ints[1], ints[2]
    body = ints[3:3 + capacity * FIELDS]
    written = ints[3 + capacity * FIELDS + 1]
    if header != "AP53":
        sys.exit(f"not an AP53 file: header {header!r}")
    rows = []
    for i in range(written):
        base = i * FIELDS
        rows.append(dict(zip(
            ("rec", "tick", "time", "v1", "v2", "v3", "v4", "v5"),
            body[base:base + FIELDS])))
    return version, written, rows


def name(type_id):
    return RAM.get(type_id, str(type_id))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: decode.py <run.xsdat>")
    version, written, rows = records(decode(sys.argv[1]))
    print(f"AP53 v{version}, {written} records\n")
    for r in rows:
        kind = REC.get(r["rec"], r["rec"])
        if kind == "BOOT":
            print(f"BOOT   vanillaAge={r['v1']} caveman={r['v2']} techsanity={r['v3']} "
                  f"spot=({r['v4']},{r['v5']})")
        elif kind == "MAKE":
            print(f"MAKE   {CASE.get(r['v1'])}: asked for {name(r['v2'])} -> "
                  f"unit {r['v3']} copyId {name(r['v4'])} objectId {name(r['v5'])}")
        elif kind == "OPEN":
            print(f"OPEN   {CASE.get(r['v1'])}: Siege Workshop unit {r['v3']}")
        elif kind == "SCAN":
            print(f"  seen {CASE.get(r['v1'])} +{r['v2']}s: unit {r['v3']} "
                  f"copyId {name(r['v4'])} objectId {name(r['v5'])}")
        elif kind == "RESULT":
            print(f"RESULT {CASE.get(r['v1'])}: unit {r['v2']} copyId {name(r['v3'])} "
                  f"objectId {name(r['v4'])} distinct rams seen {r['v5']}\n")
        elif kind == "DONE":
            print(f"DONE   {r['v1']} cases, {r['v2']} records")


if __name__ == "__main__":
    main()
