# 06: Loading a mid-scenario save misses scenario items received since the save

**Reported:** 2026-10-19, playtesting

**Status:** ready-for-agent

## Report

Scenario progression items and mercenaries received while playing a different scenario never
arrive in a scenario loaded from a mid-scenario save.

Repro:

1. Save in Genghis 1.
2. Play Attila 1.
3. Receive Kereyid Tribe.
4. Keep playing Attila 1.
5. Load the Genghis 1 save.
6. Genghis 1 never sees the Kereyid Tribe (the blue-tribe check stays false).

## Audit (from code, not verified in game)

A scenario takes its own items from two places:

- **Its scenario item file** (`GEN1.xsdat`). The client rewrites it for every unlocked scenario
  (`CampaignHandler._sync_scenario_items`), so it does hold 4020. But the game reads it only in
  `ConnectAP` (`AP.xs:263-303` → `GiveScenarioItems` → `ReadScenarioItemFile`), and `ConnectAP`
  disables itself after the first successful read. A save restores that disabled rule and
  `scenarioItemsRead = 1`, so a loaded save never reads the file again.
- **The shared item window** (`items.xsdat`, `GameClient.send_items`). It streams every unlocked
  item in order, and the client tracks delivery with one global counter (`acked_items`). Kereyid
  Tribe went out while Attila 1 was running; Attila 1's `ReadItems` → `GiveItem(4020)` →
  `Genghis1BlueForce()` set the flag in *Attila 1's* XS state and acked it. The counter moved
  past it, so the client never sends it again.

Result: the item is acked in the wrong scenario, and the right scenario never rereads its file. A
fresh start of Genghis 1 would be fine, since `ConnectAP` runs then.

This is not limited to mercenaries. It hits every flag-type item in `ProgressionItems.xs` and
`MercenaryItems.xs` received while another scenario was running, whenever the target scenario is
then resumed from a save.

Note: the XS check is named `HasGenghis1BlueForce` (`MercenaryItems.xs:202`). There is no
`HasKereyidTribe` or `HasBlueTribe` in the XS. If the Genghis 1 triggers call one of those names,
that's a separate bug.

## Fix

Specced as part of the delivery-cursor change, which also covers 08 and 02:
`worlds/age2de/docs/spec-item-delivery-cursor.md`. This report is fixed by slice 03.

## Original sketch



Re-read the scenario item file after a load, not only at first connect: periodically, or whenever
the client reconnects or the packet shows a new session. The flags are idempotent, so rereading is
safe.
