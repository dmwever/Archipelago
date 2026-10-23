## Agent skills

### Issue tracker

Issues are local markdown files under `.scratch/<feature>/issues/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, recorded as a `Status:` line in each issue. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context, kept in `worlds/age2de/` (`CONTEXT.md`, `docs/adr/`). See `docs/agents/domain.md`.

### Checks

Lint the files you changed with `python -m ruff check --select F,E9 <files>`; the full rule set and mypy carry a large existing baseline. Tests: the pre-commit hook in `.githooks/` runs the client subset.
