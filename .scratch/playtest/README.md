# Playtest issues

Running list of issues found while playtesting Ageipelago. One file per issue under `issues/`.

| # | Issue | Status |
| --- | --- | --- |
| 01 | [Caveman is not applied to scenario rules](issues/01-caveman-scenario-rules.md) | done |
| 02 | [Switching scenarios by save/load reports a scenario mismatch](issues/02-save-load-scenario-mismatch.md) | done |
| 03 | ["Location does not exist: 3616" (Loom)](issues/03-location-3616-does-not-exist.md) | done |
| 04 | [Reach Feudal / Castle sent at scenario start (Joan 1)](issues/04-age-checks-sent-at-start.md) | ready-for-human (awaiting playtest) |
| 05 | [Attila 1 Forging in logic without an affordable Town Center](issues/05-attila1-forging-without-town-center.md) | done (folds in #13) |
| 06 | [Loading a mid-scenario save misses scenario items received since](issues/06-reload-misses-scenario-items.md) | done |
| 07 | [Own Shepherd in logic where no scenario with villagers has sheep](issues/07-own-shepherd-without-sheep.md) | done |
| 08 | [Traps fire again after reconnecting to the server](issues/08-traps-resent-on-server-reconnect.md) | done |
| 09 | [Castle Age received before reaching Feudal covers the Feudal button](issues/09-castle-age-covers-feudal-button.md) | done |
| 10 | [Caveman knockdowns and unit checks are starved while the unit count keeps moving](issues/10-caveman-sweep-delayed.md) | done (folds in #34) |
| 11 | [Khan shows up as trainable at the Castle](issues/11-khan-trainable-at-castle.md) | ready-for-human (awaiting playtest) |
| 12 | [Build Fish Trap doesn't require a Fishing Ship](issues/12-fish-trap-without-fishing-ship.md) | done |
| 13 | [Easy resources don't require a base; base doesn't require the Villager Line](issues/13-easy-resources-no-base-no-villager-line.md) | done (with #05) |
| 14 | [Castle Age missing in Joan 2](issues/14-joan2-castle-age-missing.md) | done |
| 15 | [Joan 2 bridge accepts a military that needs Orleans first](issues/15-joan2-bridge-military-needs-orleans.md) | done |
| 16 | [Under caveman, are scenario-granted ships and carts knocked down?](issues/16-caveman-scenario-ships-and-carts.md) | needs-triage |
| 17 | [Buildings "standing or buildable" are never paid for](issues/17-buildable-buildings-unpaid.md) | done |
| 18 | [Military asks for a base directly instead of through its price](issues/18-military-base-through-price.md) | done |
| 19 | [Economy routes, resolved together (no behaviour change)](issues/19-trade-cogs-without-base.md) | done (folds in #21; naval guard unwound by #23) |
| 20 | [Retire the `starting_*` resource flags in favour of the scan](issues/20-retire-starting-resource-flags.md) | done |
| 21 | [Structural fielding still asks for a price](issues/21-structural-field-asks-price.md) | done (folds into #19 / #22; naval guard unwound by #23) |
| 22 | [The economy route catalog](issues/22-economy-route-catalog.md) | done (folds in #21) |
| 23 | [Defending open ground is free](issues/23-land-defence-unpaid.md) | done |
| 24 | [Items that seed the economy's buildings and units](issues/24-building-seed-items.md) | done |
| 25 | [Guarded trade buildings (no behaviour change)](issues/25-guarded-trade-buildings.md) | done (unblocks #26, #27) |
| 26 | [Dock guard rulings](issues/26-dock-guard-rulings.md) | done |
| 27 | [Market guard rulings](issues/27-market-guard-rulings.md) | done |
| 28 | [Joan 4's French Camp base is not recorded as standing](issues/28-joan4-french-camp-base-unrecorded.md) | done |
| 29 | [Military can defend their own resources](issues/29-military-can-defend-their-own-resources.md) | done |
| 30 | [A standing Mill, Mining Camp or Folwark is still charged *some* wood](issues/30-standing-dropsite-charged-wood.md) | done |
| 31 | [Units handed to P1 by AP triggers start as Gaia, never capturable](issues/31-ap-granted-units-start-as-gaia.md) | done |
| 32 | [Nothing may be unpaid: ages, buildings and units the logic asks without a price](issues/32-feudal-prerequisite-unpaid.md) | needs-triage |
| 33 | [Spike: what do the caveman sweep and the unit checks cost per tick?](issues/33-unitsanity-sweep-cost-spike.md) | done |
| 34 | [Without caveman, unit location checks wait for a quiet second](issues/34-unit-checks-starved-caveman-off.md) | done (folds into #10) |
| 35 | [Spike: can the unitsanity rule find P1's new units by id on every tick?](issues/35-unit-id-lookup-spike.md) | done |
| 36 | [Which tests run on every commit, and what the easy-source snapshot is for](issues/36-pre-commit-test-curation.md) | wontfix |
| 37 | [A test that no structural form is asked bare](issues/37-never-bare-test.md) | done |
| 38 | [The age price, and what locations pay outside the economy](issues/38-age-price-outside-economy.md) | done |
| 39 | [Pay the economy's capital: Feudal, Castle, camps and villagers](issues/39-economy-capital-paid.md) | done |
| 40 | [A second Town Center as a defence and as a camp](issues/40-second-tc-defence-and-camp.md) | done |
| 41 | [Cavemanify pulls a garrisoned unit out, and its replacement can be stuck](issues/41-cavemanify-garrisoned-units.md) | wontfix |
| 42 | [The age climb's Town Center and age-up buildings are unpaid](issues/42-age-climb-buildings-paid.md) | done |
| 43 | [Housing](issues/43-houses-and-the-base.md) | ready-for-agent |
| 44 | [What the base becomes once the House leaves it](issues/44-the-base-without-houses.md) | needs-triage |
| 45 | [The caveman ledger is scanned linearly, and it is most of what a full pass costs](issues/45-caveman-ledger-lookup.md) | needs-triage |
| 46 | [Spike: what does caveman do to every row of the unit table?](issues/46-caveman-catalog-spike.md) | done |
