# 05: Move Joan's defeat rules, then retire the snapshot

**What to build:** The same move for Joan's scenarios (including Joan 3's faction-named Fastolf rule
and Joan 6's existing `can_defeat_*` rules). Once all three campaigns are moved and no local defeat
rules remain anywhere, delete the ticket-01 snapshot test and its data: later counter changes alter
resolved rules on purpose.

Spec: Testing Decisions, "Location regression". ADR 0001.

**Decided (2026-10-19): Joan 3's castle rule is the English defeat rule.** All four castles on the
bundle's map are owned by the English (P3), so the old `can_destroy_castle` moves to
`defeats(ENGLISH)` and the castle locations ask it. Unused locals still became players: Joan 2 and
Joan 3 Burgundy, Joan 6 Shrewsbury. Joan 5's refugee rule is not a defeat and stays local, renamed
`can_win_scenario`.

**Blocked by:** 03, 04

**Status:** done

- [x] Each Joan scenario with defeat rules has a `Player` enum; fixed-force scenarios need none
- [x] No local defeat rules remain in any rules file; every defeat label reads "can defeat ..."
- [x] The snapshot test is green immediately before it is deleted
- [x] Snapshot test and data removed; full suite green
