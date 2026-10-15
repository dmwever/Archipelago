# 09: siege_can_counter option

**What to build:** A yaml option, default off, deciding whether anti-unit siege (Mangonel, Bombard
Cannon, Rocket Cart, Heavy Rocket Cart lines) counts against armies and ships. Off, those lines
still counter the siege targets: Battering Ram, Armored Elephant, Trebuchet, Traction Trebuchet,
Mounted Trebuchet, Bombard Cannon, Mangonel, Scorpion, Rocket Cart, Heavy Rocket Cart. Fire Archer,
Petard and Organ Gun count as armies. The Scorpion is an ordinary counter, untouched. Logic only.

Spec: Implementation Decisions, "Counter groups", "Counter filtering". Glossary: Anti-unit siege.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] Tests first: with the option off, an anti-unit-siege-only answer fails against an army and a ship and passes against a siege target; with it on, all pass
- [ ] Scorpion counters are unchanged by the option
- [ ] Fire Archer, Petard and Organ Gun are treated as armies
- [ ] Default is off; not in slot data or XS; world version unchanged
- [ ] Ageipelago option reference page and index row added
- [ ] Full suite green
