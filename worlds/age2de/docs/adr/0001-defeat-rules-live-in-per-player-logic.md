---
status: accepted
---

# Defeat rules live in the logic layer, keyed by per-scenario Player records

Partner trade needs to know when P1 can defeat one specific opponent, but "can P1 defeat this player"
existed only as local variables inside each scenario's rules, named `can_beat_*`, `can_kill_*` or
`can_defeat_*` and keyed by colour or faction. So each connected scenario now has an enumeration of
its players (slot number, readable name, a fixed ally or enemy side, main-opponent flag, usable
market and dock, and a gate per enemy building), each scenario's starting state builds one defeat
rule per opponent, and scenario logic serves them through a cached `defeats(player)` that both the
victory rules and the trade logic read.

## Considered Options

- **Keep the rules in the rules layer and let trade reach into it.** Rejected: it inverts the
  dependency, which runs from rules to logic everywhere else, and trade is asked from inside the
  rules themselves.
- **Per-scenario booleans only (PR 19's shape), with trade opening once the scenario's victory rule
  is met.** Rejected: by then the scenario is won, and usability differs between opponents in the
  same scenario.
- **A player's side as a set, or stance changes during a scenario.** Rejected: every scenario was
  resolvable as one fixed side per player, and neutral or ignored players simply get no record.

## Consequences

- A defeat rule must never depend on partner trade with its own player, or building it recurses. A
  test guards this.
- The move must preserve behaviour: every location rule is snapshotted on `v0.3.0` before it and
  compared after each campaign moves; the snapshot is deleted once the move is complete.
- The scenario-level ally and enemy market and dock facts are derived from the records, never
  stored, so the two cannot disagree. Those facts record judged usability, not whether the building
  exists; do not correct them from a scenario scan.
- Connecting a new campaign now includes declaring its players and their defeat rules, not just
  writing victory rules.
