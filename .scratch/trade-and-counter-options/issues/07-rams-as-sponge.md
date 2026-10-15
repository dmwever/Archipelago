# 07: Rams as a sponge

**What to build:** A ram no longer counts as killing the lines it only soaks fire for. Those targets
(Archer, Cavalry Archer, Longbowman, Plumed Archer, Rattan Archer, Ballista Elephant, Skirmisher)
move to a ram-counter table, and are countered only when P1 can field a ram (Battering Ram or
Armored Elephant line) and any military line in that age. Ram versus Trebuchet stays a plain counter.

Spec: Implementation Decisions, "Rams". Glossary: Sponge, Ram.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] Tests first, through resolved counter rules on a built world
- [ ] Rams alone do not counter a ram-counter target; rams plus any military line do
- [ ] The Armored Elephant line satisfies the ram requirement for an elephant civilisation
- [ ] Rams still counter Trebuchet with no escort
- [ ] Full suite green
