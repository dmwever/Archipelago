# Trigger handling per tier

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
tier resolution (*AI source format and how the tier resolves*) or get their own condition. Also
decide what to do with the anomalies the audit lists (Genghis 6 onagers, Genghis 4 inverted
signal, source-player/owner mismatches, empty Joan 3 "Hard").
