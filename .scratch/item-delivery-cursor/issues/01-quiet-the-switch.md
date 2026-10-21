# 01: Quiet the scenario switch, and check identity harder

**What to build:** `AP_Read` currently compares the scenario id before anything else and returns, so
a save/load switch prints the red `Wrong Scenario ID` pair on every read for the whole recovery
window and the real identity checks never run. Read the scenario id where the file puts it, but act
on it only after world version, slot id and seed halves have been validated — those are per-install,
so they are meaningful even while the client is attached to another scenario. Then make the client
find the switch by watching which packet file's ping is still moving, instead of waiting out the
ten-repeat threshold.

Spec: `worlds/age2de/docs/spec-item-delivery-cursor.md` (02: quiet the switch, and check identity harder). Fixes
`.scratch/playtest/issues/02-save-load-scenario-mismatch.md`.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] `AP_Read` validates version, slot and seed before acting on the scenario id, still through
      `ReportMismatch`, still disabling `ReadAP`
- [x] A packet addressed to another scenario returns quietly, with one `<YELLOW>` line per absence
- [x] `ReadAP` does not claim the client disconnected while it is known to be on another scenario
- [x] The ping-moved test treats any change as movement, since game time restarts per scenario
- [x] `find_live_scenario` follows the file whose ping moved, deactivates the one left behind, and
      discards recorded pings when a scan bout ends
- [x] `status_loop` scans on every repeating pass instead of every fifth paused one
- [x] `test_scenario_switch.py` covers first-scan, moving, static, backwards, inactive, truncated,
      already-followed, locked, switch-with-deactivation, and stale-recorded-ping
- [x] `xs-check` reports nothing new for `AP.xs`
- [ ] In game: save in Genghis 1, load Attila 1 — no red text, one yellow line, pickup inside ~1 s
- [ ] In game: pause for 10 s — no spurious disconnect message
- [ ] In game: drop a scenario from another slot into the profile folder — the slot/seed mismatch
      still reports and still disables `ReadAP`
