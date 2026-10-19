# 07: Rams as a sponge

**What to build:** A ram no longer counts as killing the lines it only soaks fire for. Those targets
(Archer, Cavalry Archer, Longbowman, Plumed Archer, Rattan Archer, Ballista Elephant, Skirmisher)
move to a ram-counter table, and are countered only when P1 can field a ram (Battering Ram or
Armored Elephant line) and any military line in that age. Ram versus Trebuchet stays a plain counter.

Spec: Implementation Decisions, "Rams". Glossary: Sponge, Ram.

**Blocked by:** 06

**Status:** done

- [x] Tests first, through resolved counter rules on a built world
- [x] Rams alone do not counter a ram-counter target; rams plus any military line do
- [x] The Armored Elephant line satisfies the ram requirement for an elephant civilisation
- [x] Rams still counter Trebuchet with no escort
- [x] Full suite green

## Comments

- The sponge is `RAM_COUNTER_TARGETS` (UnitCounters) and `RAM_LINES` (UnitRoles), applied in
  `ScenarioUnitLogic.can_counter` via `can_sponge_for_military`: any ram line in the age and the
  military role in the age. The military role excludes siege, so a ram is never its own escort.
- Only the Battering Ram line counters Trebuchet and Mounted Trebuchet with no escort; the Armored
  Elephant line does not, as the table had it before.
- The table test asserting rams counter archers was removed; `TestRamsAreASponge` covers rams
  through resolved rules, with `can_field` mocked to control what P1 fields.
