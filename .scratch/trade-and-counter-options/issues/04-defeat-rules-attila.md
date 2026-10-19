# 04: Move Attila's defeat rules

**What to build:** The same move as ticket 03 for Attila 1-6. Attila 3's Philippopolis and
Marcianopolis share one defeat rule, as the scenario already treats them as interchangeable.

Spec: Implementation Decisions, "Defeat rules". ADR 0001.

**Decided (2026-10-19): per-player labels for the shared rule.** `defeat_rules` maps Philippopolis
(P4) and Marcianopolis (P3) to the same rule object; `defeats()` labels each with its own name, as
it already does. Red TC asks `defeats(PHILIPPOPOLIS)`, Green TC `defeats(MARCIANOPOLIS)`, and victory
ORs the two: `((Philippopolis | Marcianopolis) & has_navy) | Constantinople`. No grouping by rule
identity. The snapshot stays label-blind and flattens Or, so it stays green. Test the shared body
with `assertIs(defeats(P).child, defeats(M).child)`.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] Each Attila scenario has a `Player` enum for the opponents its rules defeat
- [ ] Attila 3's two cities map to one shared rule
- [ ] No `can_beat_*` locals remain in the Attila rules files; labels read "can defeat ..."
- [ ] The ticket-01 snapshot test is green
- [ ] Full suite green
