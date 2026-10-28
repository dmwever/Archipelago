import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

KIT = Path(r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe")
HERE = Path(__file__).resolve().parent

FIELDS = 8

REC = {1: "STAGE", 2: "META", 3: "PREDICT", 4: "CREATE", 5: "RESULT", 6: "PLACE",
       7: "RATE", 8: "DONE"}
OUTCOME = {0: "untested", 1: "left alone", 2: "swapped", 3: "destroyed"}
SPOT = {-1: "nowhere", 0: "land", 1: "water"}
WHO = {0: "probe", 1: "replacement"}
MILITIA = 74


def catalog():
    rows = json.loads((HERE / "catalog.json").read_text())
    return {r["typeId"]: r for r in rows}


def decode(path, ledger):
    args = [str(KIT), "xsdat", "decode", str(path), "--json"]
    if ledger and Path(ledger).exists():
        args += ["--ledger", str(ledger)]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0 and not out.stdout:
        sys.exit("kit failed: " + out.stderr.strip())
    return json.loads(out.stdout)


def records(report):
    values = report["decode"]["values"]
    ints = [v.get("int") for v in values]
    header = values[0].get("string")
    version, capacity = ints[1], ints[2]
    body = ints[3:3 + capacity * FIELDS]
    footer = values[3 + capacity * FIELDS].get("string")
    written = ints[3 + capacity * FIELDS + 1]
    tail = ints[3 + capacity * FIELDS + 2]
    meta = dict(header=header, version=version, capacity=capacity, footer=footer,
                written=written, tail=tail)
    out = []
    for n in range(written):
        kind, tick, gtime, a, b, c, d, e = body[n * FIELDS:(n + 1) * FIELDS]
        out.append(dict(kind=kind, tick=tick, t=gtime, a=a, b=b, c=c, d=d, e=e))
    return meta, out


def collate(recs):
    """One entry per unit row; each holds a pass per spot (0 land, 1 water)."""
    rows, cur, cp = [], None, None
    for r in recs:
        kind = r["kind"]
        if kind == 2:
            cur = dict(typeId=r["a"], lineId=r["b"], tier=r["c"], exempt=r["d"],
                       locked=r["e"], passes={})
            cp = None
            rows.append(cur)
        elif cur is None:
            continue
        elif kind == 3:
            cur.update(target=r["b"], upgradeItem=r["c"], locationId=r["d"], age=r["e"])
        elif kind == 4:
            cp = dict(spot=r["b"], probeId=r["c"], probeObject=r["d"], places=[])
            cur["passes"][r["b"]] = cp
        elif kind == 5 and cp is not None:
            cp.update(outcome=r["b"], objectNow=r["c"], replacementId=r["d"],
                      ledger=r["e"])
        elif kind == 6 and cp is not None:
            cp["places"].append((r["b"], r["c"], r["d"], r["e"]))
    return rows


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "run1.xsdat"
    ledger = HERE / (path.stem + "-ledger.json")
    report = decode(path, ledger)

    summary = report.get("summary") or {}
    if summary:
        print("ledger %s: %s passed, %s failed, %s unknown of %s"
              % (ledger.name, summary.get("passed"), summary.get("failed"),
                 summary.get("unknown"), summary.get("total")))

    meta, recs = records(report)
    print("header %(header)s v%(version)d capacity %(capacity)d footer %(footer)s "
          "records %(written)d tail %(tail)s" % meta)

    for r in recs:
        if r["kind"] != 1:
            continue
        what = {-2: "land spot", -3: "water spot"}.get(r["a"], "stage %d" % r["a"])
        terr = r["d"]
        note = " (WATER)" if terr == 23 else ""
        print("%-11s (%d, %d) terrain=%d%s" % (what, r["b"], r["c"], terr, note))
    print()

    cat = catalog()
    rows = collate(recs)

    def pass_text(p):
        if p is None:
            return "%-12s %s" % ("not probed", "")
        where = ""
        for who, x, z, obj in p["places"]:
            if who == 1:
                where = "-> %s at %d,%d" % (cat.get(obj, {}).get("name", obj), x, z)
        return "%-12s %s" % (OUTCOME.get(p.get("outcome"), "?"), where)

    print("%-6s %-20s %-6s %-10s | %-28s | %s"
          % ("id", "name", "place", "predicted", "on land", "on water"))
    for row in rows:
        info = cat.get(row["typeId"], {})
        target = row.get("target", -1)
        pred = "self" if target == row["typeId"] else cat.get(target, {}).get(
            "name", str(target))
        flags = " exempt" if row.get("exempt") else ""
        print("%-6s %-20s %-6s %-10s | %-28s | %s%s"
              % (row["typeId"], info.get("name", "?"), info.get("place", "?"), pred,
                 pass_text(row["passes"].get(0)), pass_text(row["passes"].get(1)),
                 flags))

    print()
    print("rows measured: %d of %d in catalog.json" % (len(rows), len(cat)))
    for spot, label in ((0, "land"), (1, "water")):
        sub = [r["passes"][spot] for r in rows if spot in r["passes"]]
        print("on %-6s %s" % (label,
                              dict(Counter(OUTCOME.get(p.get("outcome"), "?")
                                           for p in sub))))
        for place in ("foot", "siege", "water"):
            byplace = [r["passes"][spot] for r in rows
                       if spot in r["passes"]
                       and cat.get(r["typeId"], {}).get("place") == place]
            if byplace:
                print("   %-6s %s"
                      % (place, dict(Counter(OUTCOME.get(p.get("outcome"), "?")
                                             for p in byplace))))

    destroyed = [(r, spot) for r in rows for spot in r["passes"]
                 if r["passes"][spot].get("outcome") == 3]
    if destroyed:
        print()
        print("DESTROYED - removed with no replacement (%d):" % len(destroyed))
        for r, spot in destroyed:
            info = cat.get(r["typeId"], {})
            print("  %-6d %-12s %-6s on %-6s line=%d tier=%d"
                  % (r["typeId"], info.get("name", "?"), info.get("place", "?"),
                     SPOT.get(spot), r["lineId"], r["tier"]))
    else:
        print()
        print("no row was destroyed: every swap created its replacement.")


if __name__ == "__main__":
    main()
