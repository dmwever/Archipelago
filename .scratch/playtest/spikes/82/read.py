import argparse
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import forks as catalog

AGE2_FILES = Path(os.environ.get(
    "AP_AGE2_FILES", r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files"))
PROFILE = Path(os.environ.get("AP_PROFILE_DIR", AGE2_FILES / "profile"))
DEFAULT_SIDECAR = PROFILE / "default1.xsdat"


class SidecarError(Exception):
    pass


def read_ints(path):
    raw = path.read_bytes()
    if len(raw) % 4:
        raise SidecarError(f"{path.name} is {len(raw)} bytes, not a whole number of ints")
    return list(struct.unpack("<%di" % (len(raw) // 4), raw))


def decode(path):
    values = read_ints(path)
    if not values:
        raise SidecarError(f"{path.name} is empty. The scenario has not been unloaded yet.")
    if values[0] != catalog.MAGIC:
        extra = ""
        if values[0] == 1:
            extra = (" That first int of 1 is AP_Write's: GiveVictory() writes the apworld packet"
                     " to the same file, so the fork was quit within a second of a victory."
                     " Replay it and let a few seconds pass before quitting.")
        raise SidecarError(
            f"{path.name} starts with {values[0]}, not {catalog.MAGIC}."
            f" This is some other run's sidecar.{extra}")
    if len(values) < len(catalog.HEADER_FIELDS):
        raise SidecarError(f"{path.name} is too short to hold a header")

    header = dict(zip(catalog.HEADER_FIELDS, values))
    fork = catalog.BY_ID.get(header["fork_id"])
    if fork is None:
        raise SidecarError(f"fork id {header['fork_id']} is not in the catalog")

    probe_count = header["probe_count"]
    start = len(catalog.HEADER_FIELDS)
    end = start + probe_count
    if len(values) < end + 1:
        raise SidecarError(
            f"{path.name} claims {probe_count} probes but holds {len(values) - start - 1}")
    if values[end] != catalog.FOOTER:
        raise SidecarError(
            f"{path.name} has no {catalog.FOOTER} footer, so the run did not finish a write")
    if probe_count != len(fork.probes):
        raise SidecarError(
            f"{path.name} holds {probe_count} probes, {fork.key} declares {len(fork.probes)}."
            " The fork was rebuilt after this run.")
    return fork, header, values[start:end]


def judge(probe, value):
    if probe.forbid is not None:
        if value == probe.forbid:
            return "FAIL", f"must not be {probe.forbid}"
        return "PASS", f"not {probe.forbid}"
    if probe.expect is None:
        return "NOTE", ""
    if value == probe.expect:
        return "PASS", f"expected {probe.expect}"
    return "FAIL", f"expected {probe.expect}"


def report(fork, header, probes):
    print(f"{fork.key}  {fork.title}")
    print(f"checks: {', '.join(fork.checks)}   scenario: {fork.source}"
          f"   id {header['scenario_id']}")
    print(f"slot {header['slot_id']}  unitsanity {header['unitsanity']}"
          f"  techsanity {header['techsanity']}  caveman {header['caveman']}"
          f"  game time {header['game_time']}s  tick {header['tick']}")

    seed_bad = [f"{name}={header[key]} want {want}"
                for name, key in (("AP_US_MODE", "unitsanity"), ("AP_TS_MODE", "techsanity"),
                                  ("AP_US_CAVEMAN", "caveman"))
                for want in (catalog.REQUIRED_SEED[name],)
                if header[key] != want]
    if seed_bad:
        print("SEED MISMATCH: " + ", ".join(seed_bad)
              + " - this run was made on an install the checks do not describe")
    print()

    width = max(len(probe.name) for probe in fork.probes)
    failed = 0
    for probe, value in zip(fork.probes, probes):
        mark, detail = judge(probe, value)
        if mark == "FAIL":
            failed += 1
        note = probe.note or detail
        if probe.note and detail:
            note = f"{detail}; {probe.note}"
        print(f"[{mark}] {probe.name.ljust(width)}  {value:>8}   {note}")

    asserted = sum(1 for probe in fork.probes
                   if probe.expect is not None or probe.forbid is not None)
    print()
    print(f"{asserted - failed}/{asserted} asserted probes passed,"
          f" {len(fork.probes) - asserted} recorded only")
    failed += len(seed_bad)
    print()
    print("What only a person can answer:")
    for line in fork.look:
        print(f"  - {line}")
    if fork.caveats:
        print()
        print("Caveats:")
        for line in fork.caveats:
            print(f"  - {line}")
    return failed


def parse_args():
    parser = argparse.ArgumentParser(
        description="Decode a #82 fork sidecar and print its probes beside what the eye must do.")
    parser.add_argument("path", nargs="?", default=str(DEFAULT_SIDECAR),
                        help="the .xsdat to read; default is the profile's default1.xsdat")
    return parser.parse_args()


def main_for_path(path):
    if not path.is_file():
        print(f"no sidecar at {path}")
        print("DE names a loose scenario's sidecar default1.xsdat and only flushes it on unload.")
        return 2
    try:
        fork, header, probes = decode(path)
    except SidecarError as error:
        print(f"[FAIL] {error}")
        return 2
    return 1 if report(fork, header, probes) else 0


def main():
    return main_for_path(Path(parse_args().path))


if __name__ == "__main__":
    sys.exit(main())
