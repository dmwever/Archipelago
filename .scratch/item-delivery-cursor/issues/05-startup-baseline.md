# 05: `startupBaseline`, so starting resources land once

**What to build:** `StartingResources` and `TCResources` are paid out by `startup.xsdat` at every
`ConnectAP` *and* streamed through the item window, so receiving one in the menu and then starting a
scenario pays it twice. They cannot be governed by the once-ever mark from ticket 02 — they are
per-scenario-start, and they still have to land immediately when received mid-scenario.

Give `startup.xsdat` a leading `startupBase` int (the stream length when the client wrote it), have
`GiveStartupItems` record it, ship it in the packet, and sentinel those two categories below it.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (`startupBaseline`, so starting resources still land mid-playthrough).

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] `startup.xsdat` carries `startupBase`; `GiveStartupItems` stores it as a saved `int` global
- [ ] The packet carries `startupBaseline`; the reserved loop drops 26 → 25 and `scenario_id` stays
      at byte 72
- [ ] `StartingResources` and `TCResources` below the baseline go out as `ITEM_SKIP`; above it they
      go out for real
- [ ] A failed `startup.xsdat` open leaves the baseline at 0, so everything comes through the window
      once
- [ ] Tests: above-baseline sends, below-baseline sentinels, packet layout
- [ ] In game: receive a starting resource in the menu, start a scenario — granted once
- [ ] In game: receive one mid-scenario — it lands immediately
- [ ] In game: start the next scenario — the full pile applies again from `startup.xsdat`
