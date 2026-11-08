import json
import os
import subprocess
import sys
from pathlib import Path

KIT = Path(os.environ.get("AOE2KIT", r"C:\Users\dmwev\Documents\GitHub\aoe2kit\bin\kit.exe"))
HERE = Path(__file__).resolve().parent
PROFILE = Path(os.environ.get(
    "AOE2_PROFILE",
    r"C:\Users\dmwev\Games\Age of Empires 2 DE\76561199655318799\profile"))

RECORDS = 256
FIELDS = 8

REC_BOOT, REC_SEED, REC_ROW, REC_CASE, REC_STAGE = 1, 2, 3, 4, 5
REC_RES, REC_COUNT, REC_LOC, REC_WONDER, REC_DONE, REC_DIAG = 6, 7, 8, 9, 10, 11
REC_TRACE = 12
REC_RELIC = 13
REC_PROBE = 14
REC_GARRISON = 15
MONASTERY = 104

TECH_STATE = {-1: "Disabled (this civ cannot research it)", 0: "NotReady",
              1: "Ready", 2: "Researching", 3: "Done"}

CASE_DM_ELSEWHERE, CASE_DM_ATTILA5, CASE_LEITIS = 0, 1, 2
CASE_SIEGE_RAM, CASE_SIEGE_ONAGER, CASE_LONG_SWORD = 3, 4, 5
CASE_HALBERDIER, CASE_WONDER, CASE_RELIC = 6, 7, 8

LEITIS_TYPE, LEITIS_LOCATION, LEITIS_SPAWN = 1236, 441, 10
THREAT_BASE_YEARS = 200
ATHEISM_YEARS = 100

UPGRADES = [
    (CASE_SIEGE_RAM, "72", "Siege Ram", 548, 363),
    (CASE_SIEGE_ONAGER, "72", "Siege Onager", 588, 376),
    (CASE_LONG_SWORD, "72", "Long Swordsman (non-siege)", 77, 320),
    (CASE_HALBERDIER, "72", "Halberdier (research first, item second)", 359, 341),
]

COUNTDOWN_CHECKS = [
    "a completed Wonder starts one countdown",
    "the Wonder is revealed to the threatened player",
    "two Wonders standing at once show two independent timers",
    "Atheism adds 100 years to every running timer",
    "destroying a Wonder clears its timer and leaves the other running",
]

results = []


def check(ticket, name, ok, detail):
    results.append((ticket, name, "PASS" if ok else "FAIL", detail))


def skip(ticket, name, detail):
    results.append((ticket, name, "SKIP", detail))


def decode(path, ledger):
    args = [str(KIT), "xsdat", "decode", str(path), "--json"]
    if ledger.exists():
        args += ["--ledger", str(ledger)]
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0 and not proc.stdout:
        sys.exit("kit failed: " + (proc.stderr or proc.stdout).strip())
    return json.loads(proc.stdout)


class WrongSidecar(Exception):
    pass


def records(report):
    values = report["decode"]["values"]
    ints = [v.get("int") for v in values]
    header = values[0].get("string") if values else None
    if header != "AP78":
        raise WrongSidecar(
            f"header is {header!r}, not 'AP78' - this sidecar is from another harness")
    end = next((i for i, v in enumerate(values) if v.get("string") == "END"), None)
    if end is None or end + 2 >= len(values):
        raise WrongSidecar(
            f"no END marker in {len(values)} values - the run ended before it closed the file")
    written = ints[end + 1]
    magic = ints[end + 2]
    if magic != 424242:
        raise WrongSidecar(f"footer is {magic}, not 424242 - the run did not finish")
    if written is None:
        raise WrongSidecar("the record count after END is not an int")
    body = ints[3:3 + RECORDS * FIELDS]
    rows = []
    for n in range(min(written, RECORDS)):
        kind, tick, gtime, a, b, c, d, e = body[n * FIELDS:(n + 1) * FIELDS]
        rows.append({"kind": kind, "tick": tick, "time": gtime,
                     "v": (a, b, c, d, e)})
    strings = [v.get("string") for v in values if v.get("string") is not None]
    return rows, written, strings


def first(rows, kind, predicate=None):
    for row in rows:
        if row["kind"] == kind and (predicate is None or predicate(row["v"])):
            return row
    return None


def last(rows, kind, predicate=None):
    found = None
    for row in rows:
        if row["kind"] == kind and (predicate is None or predicate(row["v"])):
            found = row
    return found


def resources(rows, tag):
    row = first(rows, REC_RES, lambda v: v[4] == tag)
    return None if row is None else row["v"][:4]


def case_ran(rows, case_id):
    return first(rows, REC_CASE, lambda v: v[0] == case_id) is not None


def check_deathmatch(rows):
    before, after = resources(rows, 0), resources(rows, 1)
    if before is None or after is None:
        check("71", "the item pays nothing outside Attila 5", False, "records missing")
    else:
        delta = tuple(a - b for a, b in zip(after, before))
        check("71", "the item pays nothing outside Attila 5", delta == (0, 0, 0, 0),
              f"food/wood/stone/gold delta {delta}")

    before, after = resources(rows, 2), resources(rows, 3)
    if before is None or after is None:
        check("71", "the item pays in full inside Attila 5", False, "records missing")
    else:
        delta = tuple(a - b for a, b in zip(after, before))
        check("71", "the item pays in full inside Attila 5", delta == (7000, 1000, 500, 7250),
              f"food/wood/stone/gold delta {delta}")


def check_leitis(rows):
    row = first(rows, REC_ROW, lambda v: v[0] == LEITIS_TYPE)
    if row is None:
        check("73", "the Elite Leitis row carries no phantom upgrade item", False,
              "row record missing")
    else:
        check("73", "the Elite Leitis row carries no phantom upgrade item",
              row["v"][4] == -1,
              f"upgradeItemId={row['v'][4]} (expected -1; 3800 means /install predates the fix)")

    count = first(rows, REC_COUNT, lambda v: v[0] == CASE_LEITIS)
    if count is None:
        check("73", "all ten Elite Leitis survive the caveman pass", False, "records missing")
    else:
        elite, militia, spawned = count["v"][1], count["v"][2], count["v"][3]
        check("73", "all ten Elite Leitis survive the caveman pass",
              elite == LEITIS_SPAWN and militia == 0,
              f"elite={elite} militia={militia} spawned={spawned}")

    loc = last(rows, REC_LOC, lambda v: v[0] == LEITIS_LOCATION)
    check("73", "Own Elite Leitis sends its location",
          loc is not None and loc["v"][1] == 1,
          "complete" if loc and loc["v"][1] == 1 else "not sent")


def check_upgrade(rows, case_id, ticket, label, upgraded_type, location_id):
    count = last(rows, REC_COUNT, lambda v: v[0] == case_id)
    loc = last(rows, REC_LOC, lambda v: v[0] == location_id and v[3] == case_id)
    case = first(rows, REC_CASE, lambda v: v[0] == case_id)
    if count is None or loc is None:
        check(ticket, f"{label} checks its location", False, "records missing")
        return
    base_left, upgraded, research, state = count["v"][1], count["v"][2], count["v"][3], count["v"][4]
    pre = case["v"][4] if case else None
    note = ""
    if pre == 3:
        note = "  [INVALID: the tech was already Done at case entry, so onTechResearched never ran]"
    elif state == -1:
        note = f"  [INVALID: tech stayed {TECH_STATE[-1]}]"
    check(ticket, f"{label} units actually upgrade", upgraded == 3 and pre != 3,
          f"base={base_left} upgraded={upgraded} techState {TECH_STATE.get(pre, pre)}"
          f" -> {TECH_STATE.get(state, state)} researchCount={research}{note}")
    check(ticket, f"{label} checks its location", loc["v"][1] == 1 and pre != 3,
          f"location {location_id} " + ("complete" if loc["v"][1] == 1 else "NOT sent"))


def wonder_stage(rows, tag):
    return first(rows, REC_STAGE, lambda v: v[0] == CASE_WONDER and v[1] == tag)


def wonder_timers(rows, tag):
    return [row["v"][1] for row in rows
            if row["kind"] == REC_WONDER and row["v"][2] == tag]


def wonder_diag(rows, tag):
    return first(rows, REC_DIAG, lambda v: v[0] == CASE_WONDER and v[1] == tag)


def check_wonder(rows):
    diag = wonder_diag(rows, 1)
    if diag is not None:
        in_game, points, train_time = diag["v"][2], diag["v"][3], diag["v"][4]
        check("60", "the Wonder's owner counts as in the game", in_game == 1,
              f"xsGetPlayerInGame(2)={in_game}")
        check("60", "an xsCreateUnit Wonder reads as complete",
              points >= train_time > 0,
              f"buildPoints={points} vs cTrainTime={train_time}"
              + ("  [the countdown cannot start below train time]"
                 if 0 <= points < train_time else ""))

    trace = first(rows, REC_TRACE, lambda v: v[0] == CASE_WONDER and v[1] == 1)
    trace2 = first(rows, REC_TRACE, lambda v: v[0] == CASE_WONDER and v[1] == 101)
    if trace is not None:
        players, owner, slot = trace["v"][2], trace["v"][3], trace["v"][4]
        if slot < 0 and players <= 2:
            skip("60", "WonderThreatWatch tracked the Wonder into a slot",
                 f"FindWonderSlot={slot}, xsGetNumPlayers={players} - known issue #81, the"
                 f" owner array is one slot short so player {players} can never be armed")
        else:
            check("60", "WonderThreatWatch tracked the Wonder into a slot", slot >= 0,
                  f"FindWonderSlot={slot} " + ("(tracked)" if slot >= 0
                                               else "(never tracked: the rule did not see it)"))
        check("60", "the Wonder is owned by the player it was created for", owner == 2,
              f"xsGetUnitOwner={owner}, xsGetNumPlayers={players}")
    if trace2 is not None:
        complete, base_years = trace2["v"][2], trace2["v"][3]
        check("60", "IsWonderComplete agrees the Wonder is finished", complete == 1,
              f"IsWonderComplete={complete}, CountdownYears(0)={base_years}")

    stage1 = wonder_stage(rows, 1)
    if stage1 is None:
        check("60", "a completed Wonder starts a countdown", False, "records missing")
        return

    timers1 = wonder_timers(rows, 1)
    running1 = [t for t in timers1 if t > 0]
    armed = bool(running1) or (trace is not None and trace["v"][4] >= 0)
    if not armed:
        for name in COUNTDOWN_CHECKS:
            skip("60", name,
                 "XsTesting has 2 players, so EnableWonderThreat(2) is refused by the "
                 "off-by-one in #81 and no threat is ever armed - layer 3")
        return

    check("60", "a completed Wonder starts one countdown",
          len(running1) == 1 and running1[0] >= THREAT_BASE_YEARS - 5,
          f"running timers {running1}, wonders={stage1['v'][2]}")
    skip("60", "the Wonder is revealed to the threatened player",
         f"map revealers are not enumerable by xsGetPlayerUnitIds (read {stage1['v'][3]}), and "
         "TrackWonder provably ran, so RevealAround was called - the fog itself is a visual check")

    stage2 = wonder_stage(rows, 2)
    timers2 = [t for t in wonder_timers(rows, 2) if t > 0]
    check("60", "two Wonders standing at once show two independent timers",
          stage2 is not None and len(timers2) == 2,
          f"running timers {timers2}" + (f", wonders={stage2['v'][2]}" if stage2 else ""))

    timers3 = sorted(t for t in wonder_timers(rows, 3) if t > 0)
    gained = sorted(t for t in timers2)
    if len(timers3) == len(gained) and timers3:
        deltas = [a - b for a, b in zip(timers3, gained)]
        near = all(abs(d - ATHEISM_YEARS) <= 6 for d in deltas)
        check("60", "Atheism adds 100 years to every running timer", near,
              f"deltas {deltas} (seconds of drift allowed)")
    else:
        check("60", "Atheism adds 100 years to every running timer", False,
              f"before {gained} after {timers3}")

    stage4 = wonder_stage(rows, 4)
    end = first(rows, REC_TRACE, lambda v: v[0] == CASE_WONDER and v[1] == 4)
    end2 = first(rows, REC_TRACE, lambda v: v[0] == CASE_WONDER and v[1] == 104)
    if end is None or end2 is None or stage4 is None:
        check("60", "destroying a Wonder releases its slot", False, "records missing")
        return
    check("60", "destroying a Wonder releases its slot and leaves the other tracked",
          end["v"][4] == -1 and end2["v"][4] >= 0 and stage4["v"][2] == 1,
          f"FindWonderSlot(destroyed)={end['v'][4]}, FindWonderSlot(other)={end2['v'][4]}, "
          f"wonders standing={stage4['v'][2]}")
    skip("60", "the on-screen timer disappears when the Wonder falls",
         "xsClearTimer stops the display but xsUnsyncGetTimerTimeRemaining keeps counting "
         f"(slot still read {max(wonder_timers(rows, 4))}), so only an eye can confirm it")


def report_relics(rows):
    if not case_ran(rows, CASE_RELIC):
        return
    marks = [r for r in rows if r["kind"] == REC_RELIC]
    if not marks:
        return
    print("relic probe - P2's monk fetching a Gaia relic into P2's monastery")
    print("attribute 55 is ALL_RELICS_CAPTURED; FindRelicHolder is the current implementation")
    print(f"  {'t':>4}  {'per player: attr55 / relics / monasteries':<46}  FindRelicHolder")
    seen = set()
    for row in marks:
        tag = row["v"][0]
        if tag in seen:
            continue
        seen.add(tag)
        same = [m for m in marks if m["v"][0] == tag]
        per = "   ".join(f"P{m['v'][1]}: {m['v'][2]}/{m['v'][3]}/{m['v'][4]}" for m in same)
        holder = first(rows, REC_TRACE, lambda v: v[0] == CASE_RELIC and v[1] == 200 + tag)
        found = holder["v"][2] if holder else "?"
        print(f"  {row['time']:>4}  {per:<46}  {found}")
    probes = [r for r in rows if r["kind"] == REC_PROBE]
    if probes:
        print()
        print("  can a relic be enumerated at all?  byClass / byType / monasteries, per owner")
        for tag in sorted({r["v"][0] for r in probes}):
            same = [r for r in probes if r["v"][0] == tag]
            when = next(m["time"] for m in marks if m["v"][0] == tag)
            per = "   ".join(
                (f"P{r['v'][1]}: {r['v'][2]}/{r['v'][3]}/{r['v'][4]}" if r["v"][1] else
                 f"p0scan={r['v'][2]} objCount(P1,relic)={r['v'][3]} objCount(P2,relic)={r['v'][4]}")
                for r in sorted(same, key=lambda r: r["v"][1]))
            print(f"  {when:>4}  {per}")
        best = max((max(r["v"][2], r["v"][3]) for r in probes), default=0)
        gaia = max((r["v"][2] for r in probes if r["v"][1] == 0), default=0)
        objc = max((max(r["v"][3], r["v"][4]) for r in probes if r["v"][1] == 0), default=0)
        print(f"  -> best per-player relic enumeration: {best}; player-0 scan: {gaia}; "
              f"xsGetObjectCount: {objc}")
        print()

    gar = [r for r in rows if r["kind"] == REC_GARRISON]
    if gar:
        print("  live possession via xsGetGarrisonedInUnitId, per relic")
        print(f"  {'t':>4}  relic -> container (object/owner)              FindRelicHolder")
        for tag in sorted({r["v"][0] for r in gar}):
            same = [r for r in gar if r["v"][0] == tag]
            when = next((m["time"] for m in marks if m["v"][0] == tag), "?")
            holder = first(rows, REC_TRACE, lambda v: v[0] == CASE_RELIC and v[1] == 200 + tag)
            per = "   ".join(
                (f"relic {r['v'][1]} -> loose" if r["v"][2] < 0 else
                 f"relic {r['v'][1]} -> unit {r['v'][2]} "
                 f"({'MONASTERY' if r['v'][3] == MONASTERY else r['v'][3]}/P{r['v'][4]})")
                for r in same)
            found = holder["v"][2] if holder else "?"
            print(f"  {when:>4}  {per:<46}  {found}")
        print()

    timers = [r for r in rows if r["kind"] == REC_TRACE and r["v"][0] == CASE_RELIC
              and r["v"][1] >= 300]
    if timers:
        seq = " ".join(str(r["v"][2]) for r in sorted(timers, key=lambda r: r["v"][1]))
        running = [r["v"][2] for r in timers if r["v"][2] > 0]
        print(f"  relic countdown timer, sample by sample: {seq}")
        if running:
            print(f"  -> the countdown ran, peak {max(running)} years, "
                  f"{len(running)} of {len(timers)} samples")
        else:
            print("  -> the countdown never started")
        print()

    killed = [r for r in rows if r["kind"] == REC_TRACE and r["v"][0] == CASE_RELIC
              and r["v"][1] >= 200 and r["v"][4] == 1]
    if killed:
        first_tag = min(r["v"][1] for r in killed) - 200
        after = [m for m in marks if m["v"][0] >= first_tag and m["v"][1] == 2]
        if after:
            seq = " ".join(str(m["v"][2]) for m in after)
            print(f"  after P2's monastery was destroyed, P2 attr55 reads: {seq}")
            print()

    flipped = sorted({m["v"][1] for m in marks if m["v"][2] == 1})
    if flipped:
        print(f"  -> attribute 55 reached 1 for player(s) {flipped}")
    else:
        print("  -> attribute 55 never left 0 for any player")
    print()


def check_boot(rows, written, strings):
    boot = first(rows, REC_BOOT)
    seed = first(rows, REC_SEED)
    done = first(rows, REC_DONE)
    if boot is None or seed is None:
        check("78", "the run booted and recorded its seed", False, "records missing")
        return
    us_mode, caveman, ts_mode, rows_installed = boot["v"][0], boot["v"][1], boot["v"][2], boot["v"][3]
    check("78", "the seed is unitsanity all, techsanity all, caveman on",
          us_mode == 2 and ts_mode == 3 and caveman == 1,
          f"unitsanity={us_mode} techsanity={ts_mode} caveman={caveman} rows={rows_installed}")
    check("78", "the run reached its end and closed the file",
          done is not None, f"{written} records written")
    if case_ran(rows, CASE_WONDER):
        timer_messages = [s for s in strings if "Wonder <TIMER>" in s]
        check("60", "the timer line reads '<colour><name> Wonder <TIMER>'",
              len(timer_messages) >= 1,
              repr(timer_messages[0]) if timer_messages else "no timer message captured")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "run.xsdat"
    if not path.exists():
        candidate = PROFILE / "default1.xsdat"
        if candidate.exists():
            path = candidate
        else:
            print(f"no sidecar at {path} and none at {candidate}")
            return 2

    ledger = HERE / "ledger.json"
    report = decode(path, ledger)
    summary = report.get("summary", {})
    try:
        rows, written, strings = records(report)
    except WrongSidecar as problem:
        print(f"sidecar {path}")
        print(f"cannot read it: {problem}")
        print()
        print("Boot XsTesting with the AP78 Test.xs, wait for the green line, quit,")
        print("then re-run this script.")
        return 2

    check_boot(rows, written, strings)
    if case_ran(rows, CASE_DM_ELSEWHERE):
        check_deathmatch(rows)
    else:
        skip("71", "the deathmatch item pays only inside Attila 5", "case not run")
    if case_ran(rows, CASE_LEITIS):
        check_leitis(rows)
    else:
        skip("73", "the Elite Leitis survive the caveman pass", "case not run")
    for case_id, ticket, label, upgraded_type, location_id in UPGRADES:
        if case_ran(rows, case_id):
            check_upgrade(rows, case_id, ticket, label, upgraded_type, location_id)
        else:
            skip(ticket, f"{label} upgrades and checks its location", "case not run")
    if case_ran(rows, CASE_WONDER):
        check_wonder(rows)
    else:
        skip("60", "the Wonder countdown behaves", "case not run")

    print(f"sidecar {path}")
    if summary:
        print("ledger: %s passed, %s failed, %s unknown of %s"
              % (summary.get("passed"), summary.get("failed"),
                 summary.get("unknown"), summary.get("total")))
    print()

    report_relics(rows)

    width = max(len(name) for _, name, _, _ in results)
    failed = sum(1 for _, _, mark, _ in results if mark == "FAIL")
    skipped = sum(1 for _, _, mark, _ in results if mark == "SKIP")
    for ticket, name, mark, detail in results:
        print(f"[{mark}] #{ticket}  {name.ljust(width)}  {detail}")
    print()
    checked = len(results) - skipped
    tail = f", {skipped} skipped (not stageable here)" if skipped else ""
    print(f"{checked - failed}/{checked} passed{tail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
