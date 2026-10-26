"""Replay every saved seed against one Archipelago checkout.

    python replay.py <checkout> <yamls dir> <out.jsonl> [jobs]

If the laptop sleeps during a run, that run's times are meaningless; its logic results still hold.
"""
import concurrent.futures
import json
import pathlib
import subprocess
import sys

checkout, yamls, out = (pathlib.Path(arg).resolve() for arg in sys.argv[1:4])   # generations run in the checkout
jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 6
here = pathlib.Path(__file__).parent


def run(seed_dir: pathlib.Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(here / "replay_one.py"), str(seed_dir), seed_dir.name],
        cwd=checkout, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("ROW "):
            return json.loads(line[4:])
    return {"seed": int(seed_dir.name), "ok": False,
            "error": (proc.stderr.strip().splitlines() or ["no output"])[-1][:300]}


done = set()
if out.exists():   # resume: keep what finished, rerun only the rest
    done = {json.loads(line)["seed"] for line in out.read_text(encoding="utf-8").splitlines() if line}
seeds = sorted((d for d in yamls.iterdir() if d.is_dir() and int(d.name) not in done),
               key=lambda d: int(d.name))
print(f"{len(done)} already done, {len(seeds)} to run", flush=True)
with open(out, "a", encoding="utf-8") as f, concurrent.futures.ThreadPoolExecutor(jobs) as pool:
    for n, row in enumerate(pool.map(run, seeds), 1):
        f.write(json.dumps(row) + "\n")
        f.flush()
        if not row["ok"]:
            print(f"FAIL {row['seed']}: {row.get('error')}", flush=True)
        if n % 10 == 0:
            print(f"{len(done) + n}/{len(done) + len(seeds)}", flush=True)
