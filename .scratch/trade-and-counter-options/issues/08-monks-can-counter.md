# 08: monks_can_counter option

**What to build:** A yaml option, default off, deciding whether faith lines (Monk, Missionary) count
as counters. Off, they stop countering every target except Battle Elephant, War Elephant and
Elephant Archer. Logic only: no slot data, no XS.

Spec: Implementation Decisions, "Options", "Counter groups", "Counter filtering". Glossary: Faith line.

**Blocked by:** 06

**Status:** done

- [x] Tests first: with the option off, a faith line alone fails to counter against a non-elephant target and passes against each elephant line; with it on, both pass
- [x] Default is off
- [x] Option is not in slot data or the game's slot-data constants; world version unchanged
- [x] Ageipelago option reference page added (logic only, no game-side effect) and index row added
- [x] Full suite green

## Comments

- The option is `MonksCanCounter` (`monks_can_counter`). The exception group is
  `FAITH_EXCEPTION_TARGETS` beside `FAITH_LINES` in UnitRoles; the filter is
  `ScenarioUnitLogic._is_expected_counter`, asked of each `countered_by` entry in `can_counter`.
- `TestMonksCanCounter` mocks `can_field` like `TestRamsAreASponge`, with the Knight line as the
  non-elephant target. `test_a_monk_converts_siege_only_with_redemption` now builds with the option on,
  since it asserts monks answer Knights.
- `TestLogicOnlyOptionsStayOutOfTheGame` (test_slot_data_wire) holds a `LOGIC_ONLY` tuple for 09-12
  to extend.
- Ageipelago: `monks-can-counter.md` and its index row, written on the `0.4.0` branch, which is what
  that checkout had out (the spec names `0.3.0`). The index's "Eighteen fields" count was already
  stale (the trap options are missing) and is left alone.
