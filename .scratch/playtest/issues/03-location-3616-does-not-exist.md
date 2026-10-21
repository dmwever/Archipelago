# 03: "Location does not exist: 3616"

**Reported:** 2026-10-19, playtesting

**Status:** needs-triage

## Report

The game reports location 3616 does not exist.

## Audit (from code, not verified in game)

3616 is the **Loom** tech location (`items/Items.py:514`, `TECH_LOOM = 3616`; `TechData.xs:14`).

A tech location is only registered in a scenario when the tech is *not* already researched at
start. `initTech` (`Techsanity.xs:~178-193`) returns early when `xsGetTechState` is
`cTechStateDone` (or `cTechStateInvalid`), and only otherwise calls `AddLocation(itemId)`.

`MarkServerLocations` (`AP.xs:~362-385`) then reads the server's checked-locations file and calls
`SetServerLocationComplete` on every id below `MIN_SCENARIO_ID` (101) — all tech, building, unit
and age ids — without checking whether this scenario registered it. For a location the scenario
never added, `GetLocationById` prints `Location Not Found: 3616` (`ScenarioLocations.xs:25`) and
`SetServerLocationComplete` prints `Location does not exist: 3616` (`ScenarioLocations.xs:132`).

Likely trigger: Loom was checked earlier (another scenario), and this scenario opens with Loom
already researched, so 3616 was never registered here.

Probably cosmetic: the location is already checked on the server, so nothing is lost. But the
same path will print for **any** checked global location the current scenario didn't register —
other already-researched techs, techs the civ can't research, building/unit locations not present
here — so it should grow as more locations are checked.

## To confirm

- Which scenario, and whether it starts with Loom researched (or in an age past Dark)
- Whether Loom had been checked before entering it
- Whether other ids also print, or only 3616
