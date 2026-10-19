# 09: siege_can_counter option

**What to build:** A yaml option, default off, deciding whether anti-unit siege (Mangonel, Bombard
Cannon, Rocket Cart, Heavy Rocket Cart lines) counts against armies and ships. Off, those lines
still counter the siege targets: Battering Ram, Armored Elephant, Trebuchet, Traction Trebuchet,
Mounted Trebuchet, Bombard Cannon, Mangonel, Scorpion, Rocket Cart, Heavy Rocket Cart. Fire Archer,
Petard and Organ Gun count as armies. The Scorpion is an ordinary counter, untouched. Logic only.

Spec: Implementation Decisions, "Counter groups", "Counter filtering". Glossary: Anti-unit siege.

**Blocked by:** 06

**Status:** done

- [x] Tests first: with the option off, an anti-unit-siege-only answer fails against an army and a ship and passes against a siege target; with it on, all pass
- [x] Scorpion counters are unchanged by the option
- [x] Fire Archer, Petard and Organ Gun are treated as armies
- [x] Default is off; not in slot data or XS; world version unchanged
- [x] Ageipelago option reference page and index row added
- [x] Full suite green

## Comments

- The option is `SiegeCanCounter` (`siege_can_counter`). The groups are `ANTI_UNIT_SIEGE` and
  `SIEGE_TARGETS` beside the faith groups in UnitRoles; the filter is a second branch of
  `ScenarioUnitLogic._is_expected_counter`.
- `SIEGE_TARGETS` is separate from `SIEGE`, which keeps Fire Archer and Petard for the building
  roles. The Organ Gun is in neither.
- `TestSiegeCanCounter` mocks `can_field` like `TestMonksCanCounter`: Mangonel vs Archer (army),
  Bombard Cannon vs Cannon Galleon (ship), and Mangonel/Bombard vs Trebuchet, Mangonel, Scorpion
  (siege). Rocket cart lines counter nothing in the table, so no test can field them as a direct counter.
  Fire Archer and Petard have no anti-unit-siege counters either, so "treated as armies" is checked
  as group membership; the Organ Gun is also checked through Mangonel resolving false.
- `siege_can_counter` added to `LOGIC_ONLY` (test_slot_data_wire) and the pools exemption list.
- Ageipelago: `siege-can-counter.md` and its index row, on the `0.3.0` branch.
- Review follow-up: the ram sponge's military escort included the Mangonel and rocket cart lines, so
  rams plus Mangonels still countered archers with the option off. Decided: anti-unit siege is no
  escort when off. `can_sponge_for_military` now filters the military lines through
  `_is_expected_escort`; covered by `test_off_anti_unit_siege_is_no_escort_for_rams` and
  `test_on_anti_unit_siege_escorts_rams`.
