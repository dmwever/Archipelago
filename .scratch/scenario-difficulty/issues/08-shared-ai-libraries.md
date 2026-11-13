# Shared AI libraries and difficulty symbols

Type: task
Status: claimed
Blocked by:

## Question

70 of the 75 live embedded AIs `(load "scenario difficulty DE")` (one loads `scenario difficulty`);
others load `scenario upgrades DE`, `scenario market`, `scenario resign*`, `elite petersen *`. These
ship with the game in `resources/_common/ai/`, which is not on this machine. Get those files and
record, for each: does it read `difficulty` or `#load-if-defined DIFFICULTY-*`, and what does each
level change (sn values, resource cheats, build/army caps)?

Also settle from the same source (or the game's AI scripting docs) whether `normal` and `standard`
are valid `difficulty` level symbols and which level each means; 17 rules use `== normal` and one
`== standard` (see [Inventory difficulty branches in embedded AIs](01-inventory-ai-difficulty-branches.md)).

HITL: the human copies the game's `resources/_common/ai/` folder (or the named files) somewhere the
agent can read; the agent does the read-through. Link the findings as an asset.
