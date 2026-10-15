# 03: Defeat rules as shared logic, with Genghis as the first campaign moved

**What to build:** "Can P1 defeat this player" becomes a question anything in a scenario's logic can
ask. Introduce per-scenario `Player` enumerations (slot number, readable name), a defeat-rules hook on
each scenario's starting state, and a cached `defeats(player)` on scenario logic. Move all six Genghis
scenarios onto it: their rules files read `defeats()` instead of building local `can_kill_*` rules,
and the rule labels say "can defeat". Victory and every other location behave exactly as before.

Spec: Implementation Decisions, "Player records" and "Defeat rules". ADR 0001. Glossary: P1, Player,
Opponent, Defeat.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Each Genghis scenario has a `Player` enum covering the opponents its rules defeat (neutral slots get no member)
- [ ] `defeats(player)` returns the same rule object on repeated calls
- [ ] No `can_kill_*` / `can_beat_*` locals remain in the Genghis rules files; labels read "can defeat ..."
- [ ] The ticket-01 snapshot test is green
- [ ] Full suite green
