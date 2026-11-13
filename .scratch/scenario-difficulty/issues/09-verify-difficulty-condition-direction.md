# Verify Difficulty Level condition direction in game

Type: task
Status: open
Blocked by:

## Question

Is the Difficulty Level trigger condition (id 19) with `quantity` N true when the game is at level
N *or easier* (numeric level ≥ N), as the scenario authors' trigger names imply, or N *or harder*,
or exactly N? And how does `inverted` combine with it? See
[Audit difficulty-conditional triggers](02-audit-difficulty-triggers.md): Attila 4's
Moderate/Hard triggers only work under "N or easier", while Genghis 6 "Additional Siege Onagers"
then fires only on extreme.

Two more engine behaviours from the same audit, checked in the same scenario:

- **Inverted AI Signal at game start.** Does an AI Signal condition with `inverted` = 1 fire in
  the first trigger pass, before the AI has run and sent anything? Genghis 4 "Not Easy Mode"
  depends on this.
- **Selected objects owned by another player.** When an effect names a source player but its
  `selected_object_ids` point at a unit another player owns, does the effect still apply? Attila 1
  (Change Object HP on Attila, Remove Object on a Watch Tower), Attila 2 (Remove Object on two
  Mangonels) and Genghis 2 (Remove Object on five units) depend on this.
- **Research Technology on a withheld tech.** Does a trigger's Research Technology effect
  research a tech the mod withholds until its AP item arrives (Loom, Murder Holes under
  techsanity), and does it tick the matching *Research X* location? Logic assumes the item is still
  needed ([Does the scenario difficulty touch logic or locations?](06-difficulty-logic-impact.md)).

HITL: the agent builds a throwaway test scenario through `aoe2-modding` containing:
- one trigger per `quantity` 4…-1, plain and inverted, each showing a chat message;
- an AI player whose script sends a signal after a short delay, plus a trigger on that signal
  with `inverted` = 1 that shows a message (and notes the game time it fires);
- a P2-owned unit hit by Change Object HP and a second P2-owned unit by Remove Object, both
  effects with source player P0 and the unit selected by id, plus a matching pair with source
  player P1.

The human plays it at two or three lobby difficulties and reports which messages appear and
which units changed. Record the truth table and the two behaviours as the answer.
