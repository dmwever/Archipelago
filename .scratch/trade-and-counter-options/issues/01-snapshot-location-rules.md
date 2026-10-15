# 01: Snapshot every location rule before the defeat-rule move

**What to build:** A temporary regression guard for the defeat-rule move. Capture every connected
scenario's resolved location rules (victory included) on `v0.3.0` as test data, and add a test that
compares a freshly built world against it. The comparison ignores rule labels, because the move
renames "can beat X" / "can kill X" to "can defeat X". The snapshot is deleted in ticket 05.

Spec: `worlds/age2de/docs/spec-trade-and-counter-options.md` (Testing Decisions). ADR 0001.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Snapshot covers every location in every connected scenario (Attila, Joan, Genghis), built with default options
- [x] Comparison is label-insensitive and fails with the location name when a rule differs
- [x] The test is green on unmodified `v0.3.0`
- [x] Capturing the snapshot is a documented one-off step, not run by the test suite
