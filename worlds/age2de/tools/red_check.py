"""Prove a new test goes red without the fix.

    python worlds/age2de/tools/red_check.py worlds/age2de/test/test_x.py::TestY::test_z ...

Runs the named tests against a throwaway worktree at HEAD with your new test files copied in, so
the old code answers the new tests. Your working tree is never touched: the maintainer edits in
this repo while agents run, and an earlier version of this script reverted the fix by stashing
every uncommitted change under the world - including theirs.

A test that still passes at HEAD guards unchanged behaviour, or proves nothing.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

WORLD = "worlds/age2de"
TESTS = f"{WORLD}/test/"
USAGE = f"python {WORLD}/tools/red_check.py {TESTS}test_x.py::TestY::test_z ..."
ROOT = pathlib.Path(__file__).resolve().parents[3]


def git(*args: str, cwd: pathlib.Path = ROOT) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True,
                          cwd=cwd).stdout


def changed(*prefixes: str) -> list[str]:
    tracked = git("diff", "--name-only", "HEAD", "--", WORLD).splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard", "--", WORLD).splitlines()
    return sorted({path for path in tracked + untracked if path.startswith(prefixes)})


def run_tests(test_ids: list[str], cwd: pathlib.Path) -> str:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider",
         "--color=no", *test_ids],
        capture_output=True, text=True, cwd=cwd,
    ).stdout


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def verdict(test_id: str, output: str) -> str:
    """"red", "red (did not load)" or "GREEN".

    Three ways this has read a failure as a pass. pytest colours its summary, which puts an
    escape before FAILED *and inside the test id*, so the output is stripped before
    matching as well as asked for uncoloured. Subtest failures print as SUBFAILED[...] and
    SUBFAILED(...), whose parameters carry spaces and nested brackets, so anything may sit
    between the marker and the id. A test whose module will not import at HEAD is named by
    file alone, which reads as GREEN unless it is looked for.
    """
    output = ANSI.sub("", output)
    failed = re.compile(
        r"^(?:(?:FAILED|ERROR)\s+|SUBFAILED[\[(].*?\s)" + re.escape(test_id),
        re.MULTILINE,
    )
    if failed.search(output):
        return "red"
    collection = re.compile(r"^ERROR\s+" + re.escape(test_id.split("::")[0]) + r"\s*$",
                            re.MULTILINE)
    if collection.search(output):
        return "red (did not load)"
    return "GREEN"


def main(test_ids: list[str]) -> int:
    if not test_ids:
        print(USAGE)
        return 2
    fix = [path for path in changed(f"{WORLD}/")
           if not path.startswith((TESTS, f"{WORLD}/tools/"))]
    if not fix:
        print(f"No uncommitted changes under {WORLD} outside {TESTS}: nothing to check against.")
        return 2
    new_tests = changed(TESTS)
    if not new_tests:
        print(f"No changed test files under {TESTS}: nothing to carry back to HEAD.")
        return 2

    holding = pathlib.Path(tempfile.mkdtemp(prefix="red_check_"))
    worktree = holding / "head"
    print(f"Building a worktree at HEAD in {worktree}")
    git("worktree", "add", "--detach", "--quiet", str(worktree), "HEAD")
    try:
        for path in new_tests:
            print(f"  carrying back {path}")
            shutil.copy2(ROOT / path, worktree / path)
        host = ROOT / "host.yaml"            # a fresh checkout has none, and parallel jobs race
        if host.exists():                    # on writing host.yaml.tmp
            shutil.copy2(host, worktree / "host.yaml")
        output = run_tests(test_ids, worktree)
    finally:
        git("worktree", "remove", "--force", str(worktree))
        shutil.rmtree(holding, ignore_errors=True)

    verdicts = {test_id: verdict(test_id, output) for test_id in test_ids}
    still_green = [test_id for test_id, said in verdicts.items() if said == "GREEN"]
    for test_id, said in verdicts.items():
        print(f"{said:18} {test_id}")
    if still_green:
        print(
            f"\n{len(still_green)} test(s) pass without the fix:",
            "each guards unchanged behaviour or proves nothing.",
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
