import re
import subprocess
import sys

WORLD = "worlds/age2de"
TESTS = f"{WORLD}/test/"
TOOLS = f"{WORLD}/tools/"
USAGE = f"python {WORLD}/tools/red_check.py {TESTS}test_x.py::TestY::test_z ..."

def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

def fix_paths() -> list[str]:
    changed = git("diff", "--name-only", "HEAD", "--", WORLD).splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard", "--", WORLD).splitlines()
    return [
        path for path in changed + untracked
        if not path.startswith((TESTS, TOOLS))
    ]

def run_tests(test_ids: list[str]) -> str:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider", *test_ids],
        capture_output=True,
        text=True,
    ).stdout

def is_red(test_id: str, output: str) -> bool:
    failure = re.compile(r"^(FAILED|ERROR|SUBFAILED\(.*\)) " + re.escape(test_id), re.MULTILINE)
    return failure.search(output) is not None

def main(test_ids: list[str]) -> int:
    if not test_ids:
        print(USAGE)
        return 2
    paths = fix_paths()
    if not paths:
        print(f"No uncommitted changes under {WORLD} outside {TESTS}: nothing to revert.")
        return 2

    print("Reverting the fix:", *paths, sep="\n  ")
    git("stash", "push", "--include-untracked", "--message", "red_check", "--", *paths)
    try:
        output = run_tests(test_ids)
    finally:
        git("stash", "pop")

    still_green = [test_id for test_id in test_ids if not is_red(test_id, output)]
    for test_id in test_ids:
        print("red  " if test_id not in still_green else "GREEN", test_id)
    if still_green:
        print(
            f"\n{len(still_green)} test(s) pass without the fix:",
            "each guards unchanged behaviour or proves nothing.",
        )
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
