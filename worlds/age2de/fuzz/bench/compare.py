"""Compare two stored result files seed by seed, split by campaign mix.

    python compare.py <old results.jsonl> <new results.jsonl> [timings.jsonl]

timings.jsonl is the fuzz run the seeds came from; it supplies each seed's campaign mix.
"""
import json
import pathlib
import statistics
import sys


def load(path):
    return {r["seed"]: r for r in map(json.loads, pathlib.Path(path).read_text().splitlines()) if r}


base, new = load(sys.argv[1]), load(sys.argv[2])
timings = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else None

campaigns = {}
if timings:
    for line in timings.read_text().splitlines():
        row = json.loads(line)
        campaigns[row["seed"]] = "+".join(name.split()[0] for name in row["enabled_campaigns"])

seeds = sorted(base.keys() & new.keys())
both = [s for s in seeds if base[s]["ok"] and new[s]["ok"]]
print(f"seeds compared: {len(seeds)}   ok baseline {sum(base[s]['ok'] for s in seeds)}"
      f"   ok branch {sum(new[s]['ok'] for s in seeds)}")
for s in seeds:
    if not new[s]["ok"]:
        print(f"  branch FAIL {s}: {new[s].get('error')}")


def line(name, key, fmt="{:.1f}"):
    # Stored runs are kept forever and a metric comes and goes, so a key one side never recorded
    # is normal. Say so and move on: a comparison must not die on the metric nobody asked about.
    seeds = [s for s in both if key in base[s] and key in new[s]]
    if not seeds:
        print(f"{name:<22} not recorded on both sides")
        return
    b = [base[s][key] for s in seeds]
    n = [new[s][key] for s in seeds]
    d = [y - x for x, y in zip(b, n)]
    up = sum(1 for x in d if x > 0)
    down = sum(1 for x in d if x < 0)
    print(f"{name:<22} baseline {fmt.format(statistics.median(b)):>7} median {fmt.format(statistics.mean(b)):>7} mean"
          f"  | branch {fmt.format(statistics.median(n)):>7} median {fmt.format(statistics.mean(n)):>7} mean"
          f"  | per seed: {up} up, {down} down, {len(d) - up - down} same")


print()
line("seconds", "seconds")
line("spheres", "spheres", "{:.1f}")
line("sphere 1 locations", "sphere1", "{:.1f}")

if campaigns:
    print("\nby campaign mix (mean):")
    groups = {}
    for s in both:
        groups.setdefault(campaigns.get(s, "?"), []).append(s)
    for name, ss in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        def m(src, key):
            return statistics.mean(src[s][key] for s in ss)
        print(f"  {name:<14} n={len(ss):3}  seconds {m(base, 'seconds'):5.1f} -> {m(new, 'seconds'):5.1f}"
              f"  spheres {m(base, 'spheres'):5.1f} -> {m(new, 'spheres'):5.1f}"
              f"  sphere1 {m(base, 'sphere1'):5.1f} -> {m(new, 'sphere1'):5.1f}")

print("\nbiggest sphere-1 drops:")
for s in sorted(both, key=lambda s: new[s]["sphere1"] - base[s]["sphere1"])[:5]:
    print(f"  {s}  {campaigns.get(s, '?'):<14} sphere1 {base[s]['sphere1']} -> {new[s]['sphere1']}"
          f"  spheres {base[s]['spheres']} -> {new[s]['spheres']}")
