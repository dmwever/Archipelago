# Does the tier touch logic or locations?

Type: grilling
Status: open
Blocked by: 02

## Question

Where a difficulty trigger changes map content (Genghis 1 Hard removes a relic and adds enemy
units), does the seed's tier change what locations exist or what reaching them costs? If so, does
logic read the tier, or do we neutralise those triggers so logic stays tier-independent?

Inputs from the audit ([Audit difficulty-conditional triggers](02-audit-difficulty-triggers.md)):
- Genghis 1 hard removes the relic behind *Pick Up the Relic Surrounded by Wolves* (fired by an
  AI signal, not a trigger condition).
- Easy/easiest gives P1 free Loom (Attila 1) and Murder Holes (Attila 1–5), a free Castle and two
  Mining Camps (Attila 6); Genghis 6 gives Siege Onagers plus Onager/Siege Onager research. These
  bypass techsanity and building-shuffle items.
- Joan 5 easy turns P3 Neutral to P1; Joan 6 removes capturable GAIA siege on harder tiers.
