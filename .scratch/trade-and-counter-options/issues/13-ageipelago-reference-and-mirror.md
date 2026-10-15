# 13: Ageipelago reference update and skill mirror

**What to build:** The Ageipelago agent reference describes `Player` records and `defeats()`, so the
next scenario author knows to declare players, sides, trade usability and defeat rules when
connecting a campaign. Then, only after asking the user, recopy the installed ageipelago skill
mirror from `docs/agent/`.

Spec: Implementation Decisions, "Documentation". ADR 0001.

**Blocked by:** 12

**Status:** ready-for-agent

- [ ] The apworld reference covers `Player` records, gates, main opponents and `defeats()`
- [ ] The "Adding a scenario" workflow mentions declaring players and defeat rules
- [ ] The option index lists all four new options
- [ ] The user is asked before the skill mirror is recopied; the mirror is recopied only on a yes
