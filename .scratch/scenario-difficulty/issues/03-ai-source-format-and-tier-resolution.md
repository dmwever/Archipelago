# AI source format and how the tier resolves

Type: grilling
Status: open
Blocked by: 01, 08

## Question

Where does the AI builder read each scenario-player AI from, and how does a tier pick a branch?

- Source: extracted `.per` templates in the Ageipelago repo (lean), versus rewriting the scenario's
  embedded text in place at install.
- Resolution: rewrite each `(difficulty <op> <level>)` to `(true)`/`(false)` for the tier, versus
  inject a tier constant / goal the rules compare against, versus explicit per-tier template
  markers.
- How the odd forms from the inventory resolve, and how the five tiers map onto the game's
  difficulty levels in comparisons (`<= moderate` etc.).
