# 06: Take PR 18's counter-table edits

**What to build:** PR 18's judgement on the counter table lands on `v0.3.0`: its re-tags (the "should
be for harder difficulty" comments that no option covers stay as comments, entries live), its
non-ram removals, and its petard removals (the petard no longer counters Bombard, Mangonel, Scorpion
or Trebuchet; its other entries stay). Its Hulk additions are not taken (`v0.3.0` already has the
Hulk line correctly) and its ram removals are not taken (ticket 07 supersedes them).

Spec: Implementation Decisions, "Rams" and "PR 18".

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] Every PR 18 counter-table change is applied except Hulk additions and ram removals
- [ ] Entries added on `v0.3.0` after PR 18 branched are preserved
- [ ] No duplicate or aliased unit-line ids
- [ ] Full suite green
