# Trigger handling per scenario difficulty

Type: grilling
Status: open
Blocked by: 02, 09

## Question

How does the scenario difficulty drive the difficulty-conditional triggers found in the audit?
Rewrite or replace the difficulty condition at install, enable/disable whole triggers per tier,
or something else? What do easiest and legendary do where the scenario only distinguishes
easy/moderate/hard?

Inputs from the audit ([Audit difficulty-conditional triggers](02-audit-difficulty-triggers.md)):
eight triggers fire on AI signals the AI sends from `(difficulty …)` rules, so they follow the
built AI script rather than any trigger condition. Decide whether those stay coupled to the AI
tier resolution (*AI source format and how the scenario difficulty resolves*) or get their own condition. Also
decide what to do with the anomalies the audit lists (Genghis 6 onagers, Genghis 4 inverted
signal, source-player/owner mismatches, empty Joan 3 "Hard").

Constraint from [Does the scenario difficulty touch logic or locations?](06-difficulty-logic-impact.md): triggers that
grant P1 things (techs, buildings, units) and Genghis 1's relic removal are kept, not stripped;
logic follows them. The answer here must state, per trigger, which scenario difficulties fire it,
since `DIFFICULTY_DEPENDENT_GRANTS` / `DIFFICULTY_DEPENDENT_LOCATIONS` take their sets from it.
