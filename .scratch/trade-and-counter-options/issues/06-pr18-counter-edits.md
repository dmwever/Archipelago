# 06: Take PR 18's counter-table edits

**What to build:** PR 18's judgement on the counter table lands on `v0.3.0`: its re-tags (the "should
be for harder difficulty" comments that no option covers stay as comments, entries live), its
non-ram removals, and its petard removals (the petard no longer counters Bombard, Mangonel, Scorpion
or Trebuchet; its other entries stay). Its Hulk additions are not taken (`v0.3.0` already has the
Hulk line correctly) and its ram removals are not taken (ticket 07 supersedes them).

Spec: Implementation Decisions, "Rams" and "PR 18".

**Blocked by:** 05

**Status:** done

- [x] Every PR 18 counter-table change is applied except Hulk additions and ram removals
- [x] Entries added on `v0.3.0` after PR 18 branched are preserved
- [x] No duplicate or aliased unit-line ids
- [x] Full suite green

## Comments

- Hulk: v0.3.0 has the Hulk line (id 934) but no Hulk entries in the counter table. PR 18's Hulk
  counters (vs Longboat, Cannon Galleon, Turtle Ship, Fire Galley, and Hulk's own list) are dropped
  with its aliased id; re-author them against id 934 if wanted.
- Every "should be for harder difficulty" tag is kept, including the Monk, Missionary, Mangonel and
  Bombard ones that tickets 08 and 09 will cover. Those tickets should strip the tags they cover.
- Turtle Ship is left with only Monk and Missionary, so once 08 lands it has no default counters.
  No scenario fields Turtle Ships as an enemy.
