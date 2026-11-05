# 74: in-game checks for "never enable tier > 0 rows"

The candidate fix for [#74](../../issues/74-skirmishers-train-elite-without-the-research.md) is
the ticket's option 3, and it is unproven. This spike decides whether it is the answer. `setUnitDisable` in `Unitsanity.xs` now fires `cEnableObject` only for a row with
`tier == 0`. Every row, whatever its tier, still has its disabled flag cleared. Upgraded tiers are
left to the engine: the vanilla upgrade tech promotes them when techsanity is off, and the shadow
tech runs the same effect when it is on.

The maintainer picked it as the working hypothesis on 2026-11-05. Q1, Q2 and Q4 each test it, and
any one can rule it out. Q3 is the ticket's own in-game criterion. None of them can be answered on
the agent's machine.

## Q1: Mongols' Camel Rider

Camel Rider is tier 1 on the Camel Scout line and has no upgrade tech. The Mongols train it
without the line head, so it is the one row in the unit table that vanilla turns on with an age
tech (Castle Age) rather than with an upgrade. The candidate never enables it.

Test in a Genghis scenario with unitsanity on, `unitsanity_items: unit_line`, and Camel Rider in
the seed:

| Run | Order | Expected |
|---|---|---|
| a | Camel line item before reaching Castle Age | Stable offers Camel Rider once in Castle |
| b | Camel line item after reaching Castle Age | Stable offers Camel Rider once the item lands |
| c | Scenario opens at or above Castle Age (vanilla climb) | Stable offers Camel Rider once the item lands |

If any run shows no Camel Rider, rule A is not enough. The row then needs the installer to mark
"has an upgrade tech" (option B), so Camel Rider keeps its enable.

## Q2: Pikeman icon, upgrade before and after the line item

Spearman is tier 0 and Pikeman is tier 1. The fix still enables Spearman when the line item lands,
and that enable could bind the Barracks button back to Spearman after Pikeman has already been
researched.

Run this with techsanity off, and again with techsanity `units` (the Pikeman item held, so the
shadow applies the Pikeman effect):

| Run | Order | Expected |
|---|---|---|
| a | Spearman line item, then research Pikeman | Barracks button becomes Pikeman; existing Spearmen convert |
| b | Research Pikeman, then Spearman line item | Barracks offers Pikeman, not Spearman |

Also note whether the Pikeman research button disappears once it is researched in both orders.

## Q4: is disabling the line head enough?

Today every row gets its disabled flag set, upgraded tiers included. If disabling the head alone
locks the whole line through the upgrades, tier > 0 rows would not need disabling at all.

Use a throwaway XS change that skips `setObjectDisable` for tier > 0 rows. Hold no Militia line
item, so Militia (the head) stays disabled, and run with techsanity off:

| Run | Action | Question |
|---|---|---|
| a | Before any research | Does the Barracks show Man-at-Arms at all? |
| b | Research Man-at-Arms | Can the player train Man-at-Arms? Does the button appear? |
| c | Receive the Militia line item after b | Does the Barracks offer Man-at-Arms or Militia? |

If run b trains Man-at-Arms, the upgraded tiers must keep their disabled flag (today's
behaviour). If it doesn't, the per-tier flag can be dropped in a follow-up.

## Q3: Joan 4 (the ticket's in-game criterion)

Start Joan 4 fresh (Franks, Castle Age) with unitsanity on and `unitsanity_items: unit_line`, and
receive the archer-skirmisher and galley/demolition line items.

- The Archery Range offers **Skirmisher**, and the Elite Skirmisher research is present and
  unresearched.
- The Dock offers **Galley** and **Demolition Raft**, and War Galley and Demolition Ship are
  present and unresearched.
- Researching Elite Skirmisher turns the button into Elite Skirmisher without a further item.

The save from the report was created by the old code, which had already enabled the upgraded
units. Loading it will not show the fix.
