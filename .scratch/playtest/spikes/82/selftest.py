import io
import struct
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import forks as catalog
import read

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def good(probe):
    if probe.expect is not None:
        return probe.expect
    if probe.forbid is not None:
        return probe.forbid - 1
    return 0


def pack(values):
    return struct.pack("<%di" % len(values), *values)


def sidecar(fork, probes=None, magic=None, footer=None, probe_count=None,
            unitsanity=2, techsanity=3, caveman=1):
    probes = list(probes if probes is not None else
                  [good(probe) for probe in fork.probes])
    header = [catalog.MAGIC if magic is None else magic,
              fork.fork_id, fork.scenario_id, 1, unitsanity, techsanity, caveman,
              120, 12, len(probes) if probe_count is None else probe_count]
    return pack(header + probes + [catalog.FOOTER if footer is None else footer])


def write(raw):
    handle = tempfile.NamedTemporaryFile("wb", suffix=".xsdat", delete=False)
    handle.write(raw)
    handle.close()
    return Path(handle.name)


def run_reader(path):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = read.main_for_path(path)
    return code, buffer.getvalue()


def main():
    for fork in catalog.FORKS:
        path = write(sidecar(fork))
        code, text = run_reader(path)
        path.unlink()
        asserted = sum(1 for probe in fork.probes
                       if probe.expect is not None or probe.forbid is not None)
        check(f"{fork.key} good run passes",
              code == 0 and f"{asserted}/{asserted} asserted probes passed" in text,
              f"exit {code}")
        check(f"{fork.key} prints what the eye must do",
              all(line in text for line in fork.look),
              f"{len(fork.look)} look lines")

    fork = catalog.BY_KEY["J3B"]

    path = write(sidecar(fork, magic=1))
    code, text = run_reader(path)
    path.unlink()
    check("a foreign sidecar is refused", code == 2 and "not 424282" in text, text.strip())

    path = write(sidecar(fork, footer=7))
    code, text = run_reader(path)
    path.unlink()
    check("a truncated run is refused", code == 2 and "footer" in text, text.strip())

    path = write(sidecar(fork, probe_count=len(fork.probes) + 3))
    code, text = run_reader(path)
    path.unlink()
    check("a stale probe count is refused", code == 2 and "holds" in text, text.strip())

    wrong = [good(probe) for probe in fork.probes]
    wrong[0] = 0
    path = write(sidecar(fork, probes=wrong))
    code, text = run_reader(path)
    path.unlink()
    check("a failed probe is reported and exits non-zero",
          code == 1 and "[FAIL] transports_p1" in text, f"exit {code}")

    menu = catalog.BY_KEY["J4M"]
    forbidden = [good(probe) for probe in menu.probes]
    forbidden[3] = 3
    path = write(sidecar(menu, probes=forbidden))
    code, text = run_reader(path)
    path.unlink()
    check("a forbidden value fails",
          code == 1 and "[FAIL] elite_skirmisher_tech" in text, f"exit {code}")

    path = write(sidecar(fork, caveman=0))
    code, text = run_reader(path)
    path.unlink()
    check("the wrong seed is called out and fails the run",
          code == 1 and "SEED MISMATCH" in text, f"exit {code}")

    path = write(pack([1, 0, 0, 0]))
    code, text = run_reader(path)
    path.unlink()
    check("an apworld packet names itself",
          code == 2 and "AP_Write's" in text, text.strip().splitlines()[0])

    path = write(b"")
    code, text = run_reader(path)
    path.unlink()
    check("an unflushed sidecar is refused", code == 2 and "empty" in text, text.strip())

    width = max(len(name) for name, _, _ in results)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name.ljust(width)}  {detail}")
    print()
    print(f"{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
