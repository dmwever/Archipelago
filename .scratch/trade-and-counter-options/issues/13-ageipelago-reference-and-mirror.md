# 13: Ageipelago reference update and skill mirror

**What to build:** The Ageipelago agent reference describes `Player` records and `defeats()`, so the
next scenario author knows to declare players, sides, trade usability and defeat rules when
connecting a campaign. Then, only after asking the user, recopy the installed ageipelago skill
mirror from `docs/agent/`.

Spec: Implementation Decisions, "Documentation". ADR 0001.

**Blocked by:** 12

**Status:** done

- [x] The apworld reference covers `Player` records, gates, main opponents and `defeats()`
- [x] The "Adding a scenario" workflow mentions declaring players and defeat rules
- [x] The option index lists all four new options
- [x] The user is asked before the skill mirror is recopied; the mirror is recopied only on a yes

## Comments

- `apworld.md`: new *Players and defeats* section (records, routing, trade access, gates,
  `defeat_rules`, `defeats`, the defeat events and why trade never reads `defeats` inline); layout,
  `create_regions` and `set_rules` mention the records and events; the "Adding a scenario"
  convention declares players and defeat rules.
- `adding-a-campaign.md`: order of work, a *Players and defeat rules* section, a **[ask]** entry for
  players, and the hand-maintained lists in `test_player_records.py`.
- `SKILL.md`: the "Adding a scenario" workflow declares players and defeat rules; routing row and
  description keywords; revision 2026-10-20a.
- The option index already listed all four options (done in 07-12).
- Docs only: no code changed, so no full suite run.
- Asked; user said recopy, and to drop the mirror's stale `options/lock-techs.md`. Recopied with
  `cp -r docs/agent/.`; `diff -rq` against `docs/agent/` is now empty.
