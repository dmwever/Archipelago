import json
import subprocess
import sys
from pathlib import Path

KIT = Path(r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe")
HERE = Path(__file__).resolve().parent

REC = {1: "STAGE", 2: "WATCH", 3: "ROW", 4: "RATE", 5: "EVENT", 6: "GATE", 7: "COUNT",
       8: "PHASE"}
EV = {1: "create", 2: "convert", 3: "remove", 4: "item", 5: "research",
      6: "immune", 7: "clear-row", 8: "tech", 9: "caveman-on", 10: "bulk", 11: "swap"}
SLOT = {
    "A": {0: "Knight 38", 1: "Spearman 93", 2: "Scout 448", 3: "Skirmisher 7",
          4: "Mangonel 280 (immune)"},
    "B": {0: "Shepherd 592 (locked)", 1: "LongSwordsman 77", 2: "Shepherd 592 (held)"},
    "C": {},
    "D": {},
    "E": {},
}
TYPE = {38: "Knight", 93: "Spearman", 448: "Scout", 7: "Skirmisher", 280: "Mangonel",
        74: "Militia", 75: "ManAtArms", 77: "LongSword", 4: "Archer", 83: "Villager",
        592: "Shepherd"}


def state_text(bits):
    parts = ["exists" if bits & 1 else "gone", "listed" if bits & 2 else "unlisted"]
    if bits & 4:
        parts.append("untracked")
    return "/".join(parts)


def decode(path, ledger):
    args = [str(KIT), "xsdat", "decode", str(path), "--json"]
    if ledger:
        args += ["--ledger", str(ledger)]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0 and not out.stdout:
        sys.exit("kit failed: " + out.stderr.strip())
    return json.loads(out.stdout)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runA.xsdat"
    run = sys.argv[2].upper() if len(sys.argv) > 2 else path.stem[-1].upper()
    if run not in SLOT:
        run = "A"
    ledger = HERE / ("ledger%s.json" % run)
    report = decode(path, ledger)

    summary = report.get("summary", {})
    print("ledger %s: %s passed, %s failed, %s unknown of %s"
          % (ledger.name, summary.get("passed"), summary.get("failed"),
             summary.get("unknown"), summary.get("total")))

    values = report["decode"]["values"]
    ints = [v.get("int") for v in values]
    header = values[0].get("string")
    version, capacity = ints[1], ints[2]
    body = ints[3:3 + capacity * 8]
    footer = values[3 + capacity * 8].get("string")
    written = ints[3 + capacity * 8 + 1]
    print("header %s v%d capacity %d footer %s records %d"
          % (header, version, capacity, footer, written))
    print()

    slots = SLOT[run]
    for n in range(written):
        kind, tick, gtime, a, b, c, d, e = body[n * 8:(n + 1) * 8]
        head = "t=%3ds tick=%5d %-5s" % (gtime, tick, REC.get(kind, kind))
        if kind == 1:
            print("%s second %d begins (records so far %d)" % (head, a, b))
        elif kind == 2:
            print("%s %-24s id=%d object=%d original=%d %s"
                  % (head, slots.get(a, a), b, c, d, state_text(e)))
        elif kind == 3 and run == "C":
            print("%s %-10s owned=%d location=%d atTickInSecond=%d"
                  % (head, TYPE.get(a, a), b, c, d))
        elif kind == 3:
            print("%s %-10s owned=%d locationSent=%d location=%d locked=%d"
                  % (head, TYPE.get(a, a), b, c, d, e))
        elif kind == 4 and run in ("C", "D", "E"):
            print("%s %3d ticks in that second  p1Units=%3d rule=%d churn=%d load=%d"
                  % (head, a, b, c, d, e))
        elif kind == 4:
            print("%s %d ticks in that second, p1Units=%d anchors=%d records=%d"
                  % (head, a, b, c, d))
        elif kind == 5:
            print("%s %-9s %s" % (head, EV.get(a, a), (b, c, d, e)))
        elif kind == 6:
            print("%s anyUnitWithLockedProfession=%d professionsReady=%d" % (head, a, b))
        elif kind == 7:
            print("%s militia=%d manAtArms=%d longSword=%d shepherds=%d villagers=%d"
                  % (head, a, b, c, d, e))
        elif kind == 8:
            print("%s phase %d rule=%d churn=%d p1Units=%d" % (head, a, b, c, d))
        else:
            print("%s %s" % (head, body[n * 8:(n + 1) * 8]))

    if run == "C":
        phase_summary(body, written)
    if run == "D":
        interleaved_summary(body, written)
    if run == "E":
        cost_summary(body, written)


MODE = {0: "normal", 1: "FULL PASS", 2: "list fetch", 3: "prof sweep", 4: "fill"}


def cost_summary(body, written):
    phases, current = [], None
    for n in range(written):
        kind, tick, gtime, a, b, c, d, e = body[n * 8:(n + 1) * 8]
        if kind == 8:
            current = {"id": a, "rule": b, "mode": c, "start": gtime,
                       "rates": [], "units": [], "era": 1 if e else 0}
            phases.append(current)
        elif kind == 4 and current is not None and gtime > current["start"] + 1:
            current["rates"].append(a)
            current["units"].append(b)
    phases = [p for p in phases if p["rates"]]
    if not phases:
        return

    def rate(p):
        return sum(p["rates"]) / float(len(p["rates"]))

    print()
    print("window rule mode         ledger  n  per-s   ms/firing  units")
    for p in phases:
        r = rate(p)
        print("  %2d     %d   %-11s  %4s  %2d  %5.2f  %8.2f   %3d-%3d"
              % (p["id"], p["rule"], MODE.get(p["mode"], p["mode"]),
                 "~150" if p["era"] else "0", len(p["rates"]), r, 1000.0 / r,
                 min(p["units"]), max(p["units"])))

    print()
    print("extra game-ms for each firing, against neighbouring 'normal' windows")
    print("in the same rule/ledger group - this is #33's unit")
    for p in phases:
        if p["mode"] in (0, 4):
            continue
        group = [q for q in phases
                 if q["mode"] == 0 and q["rule"] == p["rule"] and q["era"] == p["era"]]
        before = [q for q in group if q["id"] < p["id"]]
        after = [q for q in group if q["id"] > p["id"]]
        nb = ([before[-1]] if before else []) + ([after[0]] if after else [])
        if not nb:
            continue
        base = sum(rate(q) for q in nb) / len(nb)
        extra = 1000.0 / rate(p) - 1000.0 / base
        print("  window %2d  %-11s ledger %-4s: %6.2f ms   (%5.2f/s -> %5.2f/s, %.1f%% of rate)"
              % (p["id"], MODE.get(p["mode"], p["mode"]), "~150" if p["era"] else "0",
                 extra, base, rate(p), 100.0 - 100.0 * rate(p) / base))


def interleaved_summary(body, written):
    phases, current = [], None
    for n in range(written):
        kind, tick, gtime, a, b, c, d, e = body[n * 8:(n + 1) * 8]
        if kind == 8:
            current = {"id": a, "rule": b, "churn": c, "load": e,
                       "start": gtime, "rates": [], "units": []}
            phases.append(current)
        elif kind == 4 and current is not None and gtime > current["start"] + 1:
            current["rates"].append(a)
            current["units"].append(b)
    phases = [p for p in phases if p["rates"]]
    if not phases:
        return
    print()
    print("window rule churn load  n  firings  per-s   units")
    for p in phases:
        r = p["rates"]
        print("  %2d     %d     %d    %d   %2d   %6d  %5.2f  %3d-%3d"
              % (p["id"], p["rule"], p["churn"], p["load"], len(r), sum(r),
                 sum(r) / float(len(r)), min(p["units"]), max(p["units"])))

    def rate(p):
        return sum(p["rates"]) / float(len(p["rates"]))

    print()
    print("interleaved pairs - each 'on' window against the mean of its neighbouring")
    print("'off' windows in the same group, so linear drift cancels")
    for i, p in enumerate(phases):
        marked = p["rule"] == 1 or p["load"] == 1
        if not marked:
            continue
        group = [q for q in phases
                 if q["churn"] == p["churn"] and q["rule"] == 0 and q["load"] == 0]
        before = [q for q in group if q["id"] < p["id"]]
        after = [q for q in group if q["id"] > p["id"]]
        neighbours = ([before[-1]] if before else []) + ([after[0]] if after else [])
        if not neighbours:
            continue
        base = sum(rate(q) for q in neighbours) / len(neighbours)
        what = "rule on" if p["rule"] == 1 else "CALIBRATION load"
        print("  window %2d (%s, churn=%d): %.2f of %.2f = %.1f%%  (cost %.1f%%)"
              % (p["id"], what, p["churn"], rate(p), base,
                 100.0 * rate(p) / base, 100.0 - 100.0 * rate(p) / base))


def phase_summary(body, written):
    phases = []
    for n in range(written):
        kind, tick, gtime, a, b, c, d, e = body[n * 8:(n + 1) * 8]
        if kind == 8:
            phases.append({"id": a, "rule": b, "churn": c, "start": gtime, "rates": []})
        elif kind == 4 and phases:
            if gtime > phases[-1]["start"]:
                phases[-1]["rates"].append(a)
    if not phases:
        return
    print()
    print("phase  rule churn  seconds  firings/s min  mean   max   total")
    for p in phases:
        r = p["rates"]
        if not r:
            continue
        print("  %d      %d     %d      %3d     %8d %5.1f %5d %7d"
              % (p["id"], p["rule"], p["churn"], len(r), min(r), sum(r) / len(r),
                 max(r), sum(r)))
    print()
    print("retained % = phase mean / the mean of the baselines either side of it")
    for i, p in enumerate(phases):
        if p["rule"] != 1 or not p["rates"]:
            continue
        base = [q for q in phases
                if q["rule"] == 0 and q["churn"] == p["churn"] and q["rates"]]
        if not base:
            continue
        bmean = sum(sum(q["rates"]) / len(q["rates"]) for q in base) / len(base)
        pmean = sum(p["rates"]) / len(p["rates"])
        print("  phase %d (churn=%d): %.1f of %.1f = %.1f%%"
              % (p["id"], p["churn"], pmean, bmean, 100.0 * pmean / bmean))


if __name__ == "__main__":
    main()
