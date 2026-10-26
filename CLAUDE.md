## Agent skills

### Issue tracker

Issues are local markdown files under `.scratch/<feature>/issues/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, recorded as a `Status:` line in each issue. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, kept in `worlds/age2de/` (`CONTEXT.md`, `docs/adr/`). See `docs/agents/domain.md`.

### Checks

Lint the files you changed with `python -m ruff check --select F,E9 <files>`; the full rule set and mypy carry a large existing baseline.

Tests: run what `.githooks/pre-commit` runs for your change, plus any test file the change touches. A change under `worlds/age2de/logic/` or `locations/` picks up the logic canaries there — about a minute, and the only automatic cover the rules have. The maintainer runs the full `worlds/age2de` suite by hand; leave it to them.

Leave your work in the working tree for the maintainer to commit. These two rules override any skill or workflow that says to run the full suite or to commit.

### Agent tools

`worlds/age2de/tools/` holds `red_check.py` (prove a new test fails at HEAD), `route_catalog.py` (regenerate the pinned economy route list) and `recapture_easy_sources.py`. Each explains itself in its module docstring. The fill gate is defined in `worlds/age2de/fuzz/bench/README.md`.
