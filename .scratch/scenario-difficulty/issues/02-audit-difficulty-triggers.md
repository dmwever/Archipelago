# Audit difficulty-conditional triggers

Type: task
Status: resolved
Blocked by:

## Question

Which triggers in the 18 AP scenarios depend on the difficulty setting, and what do they do? For
each: scenario, trigger name, the condition (id resolved from the vendored datasets, with its
comparison and level), and the effects, honouring `object_type` / `object_list_unit_id` filters.
Note which effects change map content P1 interacts with (relics, units, buildings near locations),
since that feeds the logic question. Genghis 1's "Hard Difficulty" trigger is a known example.

AFK. Link the audit as an asset.

## Answer

Audit: [`../assets/difficulty-triggers.md`](../assets/difficulty-triggers.md) (raw
[`../assets/difficulty-triggers.json`](../assets/difficulty-triggers.json), script
[`../assets/tools/audit_triggers.py`](../assets/tools/audit_triggers.py)).

**Two mechanisms, 38 triggers in 16 of 18 scenarios.**
- 30 triggers in 13 scenarios use the Difficulty Level condition (id 19, `quantity` = level).
- 8 triggers in 5 scenarios (Attila 2, Genghis 1/2/4/5) fire on an **AI Signal** that the
  scenario's AI sends from a `(difficulty …)` rule. Genghis 1 "Hard Difficulty" is one. These follow
  whatever the built AI script does, so trigger handling and AI tier resolution are coupled.
- Only Genghis 3 and Joan 4 have none. Attila 1–6 and Joan 1–3/5/6 group theirs under a
  "--- Difficulties ---" separator.

**Condition direction (inferred, not sourced):** `Difficulty Level q=N` is true at level N *or
easier*. Attila 4's "Moderate" (`q=2 ∧ ¬q=3`) and "Hard" (`q=1 ∧ ¬q=3 ∧ ¬q=2`) triggers are
only satisfiable under that reading. So "Easy" triggers (`q=3`) also fire on easiest.

**Map content P1 touches:**
- Genghis 1 hard removes the relic behind *Pick Up the Relic Surrounded by Wolves* — the location
  becomes uncheckable.
- Easy/easiest gives P1 free Loom (Attila 1) and Murder Holes (Attila 1–5) — bypasses techsanity
  items — and a free Castle + two Mining Camps in Attila 6 — bypasses building shuffle.
- Genghis 6 gives P1 Siege Onagers and Onager/Siege Onager research, but under the inferred
  reading only on extreme.
- Joan 5 easy turns P3 Neutral to P1; Joan 6 removes capturable GAIA siege on moderate+/hard+;
  Joan 3 adds oak trees on easy/moderate.
- Everything else only scales enemy strength (removals, enemy techs, Attila 4 wave lengths, Attila
  6 wonder timer, Joan 6 extra Town Center).

**Anomalies:** condition direction unverified; Genghis 4/5 "easy mode" signals hang on
`difficulty == normal` (ticket *Shared AI libraries and difficulty symbols*); Genghis 4's inverted
AI Signal likely fires on every difficulty; several effects select objects owned by a player other
than the source player (possible no-ops); Joan 3 "Hard" is empty.
