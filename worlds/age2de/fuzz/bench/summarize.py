import collections
import json
import pathlib
import statistics
import sys

out = pathlib.Path(sys.argv[1])
report = json.loads((out / "report.json").read_text())
rows = [json.loads(line) for line in (out / "timings.jsonl").read_text().splitlines() if line]
ok = [r for r in rows if r["ok"]]
times = sorted(r["seconds"] for r in ok)

print("fuzzer stats:", report["stats"])
print(f"timed generations: {len(rows)}, succeeded: {len(ok)}")
if times:
    q = lambda p: times[min(len(times) - 1, int(len(times) * p))]
    print(f"seconds: min {times[0]:.1f}  median {statistics.median(times):.1f}  "
          f"mean {statistics.mean(times):.1f}  p90 {q(.9):.1f}  p99 {q(.99):.1f}  max {times[-1]:.1f}")
    print(f"total generation time: {sum(times) / 60:.1f} min")

def by(key, fmt=str):
    groups = collections.defaultdict(list)
    for r in ok:
        groups[fmt(r.get(key))].append(r["seconds"])
    print(f"\nby {key}:")
    for name, ts in sorted(groups.items(), key=lambda kv: -statistics.mean(kv[1])):
        print(f"  {statistics.mean(ts):6.1f}s mean  {max(ts):6.1f}s max  n={len(ts):3}  {name}")

by("enabled_campaigns", lambda v: "+".join(v or []))
by("caveman")
by("local_start")
by("existing_techs")
by("include_unique_units")
by("scenario_branching")

print("\nslowest 5:")
for r in sorted(ok, key=lambda r: -r["seconds"])[:5]:
    print(f"  {r['seconds']:6.1f}s  seed {r['seed']}  locations {r['locations']}  "
          f"{'+'.join(r['enabled_campaigns'])}  caveman={r['caveman']} local_start={r['local_start']}")

errors = report.get("errors", {})
if errors:
    print("\nerrors:")
    for game, kinds in errors.items():
        for kind, entries in kinds.items():
            print(f"  {game} {kind}: {len(entries) if hasattr(entries, '__len__') else entries}")
