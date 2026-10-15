# 05: Move Joan's defeat rules, then retire the snapshot

**What to build:** The same move for Joan's scenarios (including Joan 3's faction-named Fastolf rule
and Joan 6's existing `can_defeat_*` rules). Once all three campaigns are moved and no local defeat
rules remain anywhere, delete the ticket-01 snapshot test and its data: later counter changes alter
resolved rules on purpose.

Spec: Testing Decisions, "Location regression". ADR 0001.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] Each Joan scenario with defeat rules has a `Player` enum; fixed-force scenarios need none
- [ ] No local defeat rules remain in any rules file; every defeat label reads "can defeat ..."
- [ ] The snapshot test is green immediately before it is deleted
- [ ] Snapshot test and data removed; full suite green
