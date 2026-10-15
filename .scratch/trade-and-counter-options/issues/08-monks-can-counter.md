# 08: monks_can_counter option

**What to build:** A yaml option, default off, deciding whether faith lines (Monk, Missionary) count
as counters. Off, they stop countering every target except Battle Elephant, War Elephant and
Elephant Archer. Logic only: no slot data, no XS.

Spec: Implementation Decisions, "Options", "Counter groups", "Counter filtering". Glossary: Faith line.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] Tests first: with the option off, a faith-line-only answer fails against a non-elephant target and passes against each elephant line; with it on, both pass
- [ ] Default is off
- [ ] Option is not in slot data or the game's slot-data constants; world version unchanged
- [ ] Ageipelago option reference page added (logic only, no game-side effect) and index row added
- [ ] Full suite green
