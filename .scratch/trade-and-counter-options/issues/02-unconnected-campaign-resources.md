# 02: Bring in the unconnected campaigns' resource files

**What to build:** The Saladin, Barbarossa, El Cid and Montezuma resource scans from PR 19 land in
source, not imported, so the data waits in the repo rather than in a branch. They keep PR 19's
per-scenario market and dock flags, which record judged usability, not building existence.

Spec: Implementation Decisions, "Unconnected campaigns".

**Blocked by:** None (can start immediately)

**Status:** done

- [x] One file per campaign, in the same form as the other scenario resource data, with valid Python syntax (PR 19's missing commas, lowercase booleans and `boolean` annotation fixed)
- [x] The duplicate Montezuma file is removed; only one copy remains
- [x] The Saladin docstring no longer says "Khan" or "Mongols"
- [x] Each docstring says the file is not imported, and that its flags must be rescanned per player when the campaign is connected
- [ ] Nothing imports them; the existing suite is green; no new tests (nothing imports them and no tests were added; the suite was not run, by request)
