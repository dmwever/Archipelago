# Spec: trade and counter options, per-player scenario records, and the pending PRs

Status: ready-for-agent. Branch: `v0.3.0` (apworld) and `0.3.0` (Ageipelago docs). Nothing is committed
as part of this work. Vocabulary follows `worlds/age2de/CONTEXT.md`.

## Problem Statement

Three pull requests are waiting on stale bases. PR 19 and PR 20 are the same branch; neither PR 18 nor
PR 19 imports as written. PR 18 carries real judgement about which counters are "harder difficulty",
but only as comments. PR 19 carries hand-judged trade usability for every scenario and resource scans
for four campaigns that do not exist yet, but it hangs the trade facts off the per-tier resource count,
where they do not belong.

Meanwhile the logic has no way for a yaml to say how much it expects of P1. Monks and clumsy siege
always count as counters, so a seed can demand monk micro or mangonel micro of a player who never
uses them. Market trade and trade with other players exist in the logic as stubs switched off by
module constants, and trade with a player can never turn on because no scenario declares a trading
ally. Rams sit in the counter table as though they killed archers, which they cannot.

Finally, "can P1 defeat this player" exists only as local variables inside each scenario's rules,
named three different ways, so nothing else - trade in particular - can ask the question.

## Solution

Bring the PRs in as working-tree changes on `v0.3.0`, keeping their intent and discarding what
`v0.3.0` has already superseded. The four campaigns without scenarios land as source only.

Add four logic-only yaml options:

- **Market trade**: whether the logic may expect P1 to buy and sell at its own market. Off by default.
- **Partner trade**: whether the logic may expect trade carts and trade cogs run to a trade partner,
  and which partners count: none, allies, or allies and enemies. Allies by default.
- **Monks can counter**: whether faith lines count as counters. Off by default; even off, faith lines
  still counter the elephant lines.
- **Siege can counter**: whether anti-unit siege counts as a counter against armies and ships. Off by
  default; even off, it still counters other siege.

Give rams their real role: a ram is a sponge, which counters its targets only alongside a military
line that deals the damage.

Give each connected scenario a record of its players, each an ally or an enemy, with the usability of
its market and dock, whether it is a main opponent, and how P1 defeats it. Defeat rules become shared
logic that both victory and trade read.

## User Stories

1. As a yaml author, I want a market trade option, so that I can decide whether a seed may expect me to buy and sell at my own market.
2. As a yaml author, I want market trade off by default, so that a seed never quietly assumes market trading I did not ask for.
3. As a yaml author, I want a partner trade option, so that I can decide whether a seed may expect trade carts and trade cogs.
4. As a yaml author, I want partner trade to offer none, allies, and allies and enemies, so that I can opt into trading with defeated or undefended opponents separately from allies.
5. As a yaml author, I want partner trade to default to allies, so that the easiest form of trade is assumed without asking me.
6. As a yaml author, I want one partner trade option to cover carts and cogs together, so that I make one decision about trade, not two.
7. As a yaml author, I want a monks can counter option, so that seeds do not demand conversion micro of me unless I ask.
8. As a yaml author, I want monks can counter off by default, so that the default logic matches what the counter table's author marked as harder.
9. As a yaml author, I want faith lines to keep countering Battle Elephant, War Elephant and Elephant Archer even with monks off, so that monks' standard answer to elephants always counts.
10. As a yaml author, I want a siege can counter option, so that seeds do not demand mangonel, bombard or rocket cart micro unless I ask.
11. As a yaml author, I want siege can counter off by default, so that the default logic matches what the counter table's author marked as harder.
12. As a yaml author, I want anti-unit siege to keep countering other siege even with siege off, so that siege duels, which need no micro, still count.
13. As a yaml author, I want the scorpion to stay an ordinary counter whatever the siege option says, so that the one easy siege unit is not punished with the clumsy ones.
14. As a yaml author, I want the organ gun, fire archer and petard treated as army targets rather than siege, so that the siege option's exception covers only true siege.
15. As a yaml author, I want these options to change only what the logic expects, so that I can still use monks, siege and trade in game whatever I chose.
16. As a player, I want a ram never counted as killing archers on its own, so that the logic never sends me against archers with nothing but rams.
17. As a player, I want rams plus any army to count against the lines rams soak for, so that the classic ram-screen push is recognised.
18. As a player, I want rams to keep countering trebuchets as a plain counter, so that killing siege with rams needs no escort in the logic.
19. As a player of an elephant civilisation, I want the Armored Elephant line to count as my ram, so that I am not denied the sponge because my civilisation has no Battering Ram.
20. As a player, I want trade with an ally counted only where the scenario's ally actually has a usable market or dock, so that the logic does not expect trade that the map cannot support.
21. As a player, I want trade with a defended opponent building counted only after the logic says I can defeat its owner, so that I am never expected to trade through a hostile army.
22. As a player, I want an undefended opponent building usable without defeating its owner, so that Joan 3's open English dock counts as it plays.
23. As a player, I want a main opponent's market and dock excluded from trade by default, so that I am not expected to trade with the strongest army on the map.
24. As a player, I want markets an AI builds after the start counted as well as the ones it starts with, so that the logic matches scenarios where the market appears later.
25. As a player, I want neutral players ignored by trade and defeat logic, so that bystanders never become requirements.
26. As a player, I want fixed-force scenarios to have no trade at all, so that no logic expects an economy where there is none.
27. As a maintainer, I want each scenario's trading allies to come from its player records, so that no scenario has to hand-author them.
28. As a maintainer, I want an ally's trade access to be the whole answer, with no per-scenario override, so that an ally open from the start (Attila 1's Scythians) asks only what any trade asks: a market, the Feudal Age and trade carts.
29. As a maintainer, I want trade usability to live only on the player records, with no scenario-level ally and enemy market and dock flags, so that the two cannot disagree.
30. As a maintainer, I want every connected scenario's players named for what the campaign calls them, so that rules read as the scenario does.
31. As a maintainer, I want each player record to carry its scenario slot number, so that the record is exact against the scenario file.
32. As a maintainer, I want each player to be exactly one of ally or enemy, so that the model does not branch on stance changes the scenarios do not need.
33. As a maintainer, I want one defeat rule per opponent, reachable from anywhere in that scenario's logic, so that victory and trade ask the same question.
34. As a maintainer, I want the defeat rules to live in the logic layer, so that dependencies keep pointing from rules to logic.
35. As a maintainer, I want the rules files to read defeat rules rather than build them, so that they shrink to what each location requires.
36. As a maintainer, I want two opponents allowed to share one defeat rule, so that Attila 3's interchangeable cities stay as one rule.
37. As a maintainer, I want a defeat rule allowed to be free, so that a city that offers no resistance needs no fabricated requirement.
38. As a maintainer, I want every defeat rule's label to say "defeat", so that explain output uses the glossary's word.
39. As a maintainer, I want every location rule proved unchanged by the move, so that the refactor cannot silently weaken or tighten any scenario.
40. As a maintainer, I want partner trade to ask for a defeat event rather than a defeat rule, and a test that builds every defeat and trade rule, so that building the rules can never recurse.
41. As a maintainer, I want the ram counters in their own table, so that the sponge's extra requirement applies to exactly the targets it belongs to.
42. As a maintainer, I want the faith-line, anti-unit-siege and siege-target groups defined once, so that the options filter against one definition.
43. As a maintainer, I want PR 18's remaining "harder difficulty" tags kept as comments with their entries live, so that the judgement is preserved for a later decision without changing behaviour now.
44. As a maintainer, I want PR 18's broken Hulk additions dropped, so that the correct Hulk line already on `v0.3.0` is not duplicated or aliased.
45. As a maintainer, I want PR 18's counter edits brought in, so that its re-tags and its non-ram removals take effect, with its ram removals superseded by the sponge.
46. As a maintainer, I want PR 19's market and dock flags treated as judged usability rather than building existence, so that nobody corrects them from a scan.
47. As a maintainer, I want the rulings made during design recorded as data, so that each scenario's trade behaviour is visible in one place.
48. As a maintainer, I want the four unconnected campaigns' resource files present but not imported, so that the scanned data waits in the source rather than in a branch.
49. As a maintainer, I want the unconnected files to keep PR 19's per-scenario flags, so that no data is lost before those campaigns get player records.
50. As a maintainer, I want the unconnected files' docstrings to say their flags need a per-player rescan when connected, so that the next person knows what is still owed.
51. As a maintainer, I want the duplicated Montezuma file removed and the Saladin docstring corrected, so that the unconnected files do not mislead.
52. As a maintainer, I want the unconnected files to have no tests, so that they cost nothing until their campaigns exist.
53. As a maintainer, I want the four options kept out of slot data and XS, so that no world version bump and no paired game release is needed.
54. As a maintainer, I want the market and ally-trade module constants removed in favour of options, so that there is one switch per behaviour.
55. As a maintainer, I want each new option documented in the Ageipelago option references, so that the option index stays complete.
56. As a maintainer, I want each option's documentation to say it has no game-side effect, so that nobody looks for XS that does not exist.
57. As a maintainer, I want the apworld reference to describe player records and defeat rules, so that the next scenario author knows to fill them in.
58. As a scenario author adding a campaign, I want a clear place to declare each player, its side, its trade usability and its defeat rule, so that connecting a scenario covers trade as well as victory.

## Implementation Decisions

**Options.** Four new options, all logic-only: market trade (toggle, default off), partner trade
(choice of none, allies, allies and enemies; default allies), monks can counter (toggle, default
off), siege can counter (toggle, default off). None enters slot data or the game's slot-data script;
the world version does not change. Universal Tracker regeneration is unaffected because it does not
re-read option values today.

**Counter groups.** Three groups are defined once alongside the existing unit roles:
- faith lines: Monk and Missionary (exists already);
- anti-unit siege: Mangonel, Bombard Cannon and Rocket Cart lines (the Heavy Rocket Cart is the
  Rocket Cart line's upgrade) - not Scorpion, not Organ Gun;
- siege targets, for the siege option's exception: the Battering Ram, Armored Elephant, Trebuchet,
  Traction Trebuchet, Mounted Trebuchet, Bombard Cannon, Mangonel, Scorpion and Rocket Cart lines.
  This is its own group, not the existing building-breaker group: the Fire Archer
  and Petard lines are deliberately left out and count as armies, and the Organ Gun counts as an army.
  Mangonels and rocket carts do not counter the Bombard Cannon; the counter table already has no such
  entries, and none are added.
- the elephant exception for faith lines: Battle Elephant, War Elephant, Elephant Archer.

**Counter filtering.** With monks off, a faith line is dropped as a counter of any target outside the
elephant exception. With siege off, an anti-unit-siege line is dropped as a counter of any target
outside the siege targets. The filtering is applied where counters are resolved, so the table itself
carries no option markers.

**Rams.** Rams leave the main counter table for the targets they soak for and move to a ram-counter
table. A ram-counter target is countered when P1 can field a ram (Battering Ram line or Armored
Elephant line) in the age and can field any military line in the age. Ram versus trebuchet and
mounted trebuchet stays in the main counter table.

The sponge model supersedes PR 18's ram removals. The ram-counter targets are the Archer, Cavalry
Archer, Longbowman, Plumed Archer, Rattan Archer, Ballista Elephant and Skirmisher lines; PR 18's
removal of ram versus Trebuchet is not taken.

PR 18's petard removals are taken: the petard no longer counters the Bombard, Mangonel, Scorpion or
Trebuchet lines. Its other entries on `v0.3.0` stay.

**PR 18.** Only the counter-table edits are taken. Its "harder difficulty" tags that neither option
covers stay as comments with their entries live.

**Player records.** Each connected scenario gains an enumeration of its players. A neutral or ignored
slot has no member. Each member carries:
- the scenario slot number and a readable name;
- side: ally or enemy, fixed for the scenario;
- main opponent: a flag, meaning significantly stronger than the rest;
- usable market and usable dock;
- for enemies, a gate per usable building: defeat its owner (default) or none (undefended).

Trade usability lives only on the records; there are no scenario-level ally and enemy market and dock
flags.

**Seeding the records.** Where PR 19's flag for a side and building is true, a player on that side is
usable for it if it owns that building at the start or its AI script builds one, unless it is a main
opponent. Where the flag is false, no player is usable for it. The design rulings override this:

- Attila 1: Scythians ally; Eastern Roman Empire enemy; Bleda ignored; Persians main opponent.
- Attila 2: Thessalonica enemy with a usable dock (Attila 2 enemy dock becomes true); Scythians
  neutral; Eastern Roman Empire main opponent.
- Attila 3: Constantinople main opponent.
- Attila 4: Burgundy enemy; Orléans main opponent; enemy dock false.
- Attila 5: Franks neutral; Western Roman Empire main opponent.
- Attila 6: no main opponent.
- Joan 1 and Joan 5: fixed force, no players recorded for trade.
- Joan 2: enemy market false (the scenario ends on partial defeat).
- Joan 3: English main opponent, but their dock is usable with no gate.
- Joan 4: Troyes, Chalons and Rheims enemies.
- Joan 6: English main opponent.
- Genghis 2: Kushluk main opponent.
- Genghis 4: Khwarazm enemy and main opponent; ally market false.
- Genghis 5: ally market and ally dock false; enemy market true with Polish and Germans both usable.

**Defeat rules.** Each scenario's starting state exposes its defeat rules keyed by player; scenario
logic exposes a cached "defeats this player" query; the rules files read it instead of building
locals. Existing rules move unchanged except for their labels ("can beat X" and "can kill X" become
"can defeat X"). Two players may share one rule (Attila 3's Philippopolis and Marcianopolis). New
rules:
- Attila 2 Dyrrhachium: free.
- Attila 2 Thessalonica: free.
- Genghis 4 Kipchaks: free.
- Genghis 5 Polish: a base, a Castle Age army, siege, Castle Age, and counters for the militia, knight
  and mangonel lines at Castle Age.

**Trade logic.** P1 has a trading ally wherever an ally record has a usable market or dock; there is
no per-scenario override. Partner trade at "allies" opens trade with usable ally buildings; at "allies
and enemies" it also opens usable enemy buildings, each behind its gate. A defended building's gate is
an event location, "<scenario>: Can Defeat <player>", created only at "allies and enemies". Its rule is
that player's defeat rule, and trade asks for the event item, never the defeat rule itself: a defeat
asks for an army, the army asks the economy, and the economy asks trade, so a direct read could loop. Carts need a usable market, cogs a usable dock, as today. Market trade replaces its
module constant one for one.

**Unconnected campaigns.** Saladin, Barbarossa, El Cid and Montezuma resource files land with their
syntax fixed, their market and dock flags kept per scenario, the duplicate Montezuma file removed and
the Saladin docstring corrected. They are not imported.

**Documentation.** One reference page per new option plus index rows in the Ageipelago option
references; the apworld reference gains player records and defeat rules; option docstrings; the
unconnected files' docstrings. The installed skill mirror is recopied only after asking.

## Testing Decisions

A good test here builds a world with the options under test and asks a resolved rule whether it can
ever be satisfied, or asks whether a location is reachable from a swept state. It never inspects a
table's contents or a private helper. Every test uses the one existing seam: the built world, its
per-scenario logic, and resolved rules.

Tests are written first for each new behaviour:
- each option on and off, asserted through counters and economy rules on real scenarios;
- the elephant exception with monks off, and the siege-target exception with siege off;
- the scorpion and organ gun unaffected by the siege option;
- the sponge: rams alone fail against a ram-counter target, rams with any military line pass, and
  rams still counter trebuchets with no escort;
- the Armored Elephant line satisfying the sponge for an elephant civilisation;
- partner trade at each of its three values, against the scenarios with design rulings (Attila 2,
  Joan 2, Joan 3, Genghis 4, Genghis 5);
- a main opponent's buildings closed to trade, and Joan 3's undefended dock open without defeat;
- the player records agreeing with PR 19's judged flags.

Two guards:
- **Location regression.** Every connected scenario's resolved location rules, victory included, are
  snapshotted on `v0.3.0` before the defeat rules move, and compared after each campaign moves. The
  comparison ignores rule labels, since every "can beat X" label becomes "can defeat X" in the same
  change. The snapshot is a temporary guard: it is deleted once all three campaigns have moved,
  because the counter changes that follow alter resolved rules on purpose. Counter changes land only
  after it is gone.
- **No self-recursion.** Every scenario's defeat rules and trade rules build without recursion. Trade
  reads defeat events, not defeat rules, so the sweep settles any cycle.

Prior art: the military rules tests (per-scenario counters and roles, resolved against a built world)
and the economy rules tests (per-scenario economy questions, resolved). Both use the shared rule test
base, which runs all four generation steps and sweeps state.

The unconnected campaign files have no tests.

## Out of Scope

- Connecting Saladin, Barbarossa, El Cid or Montezuma, or giving them player records.
- Deciding PR 18's other "harder difficulty" tags (spearman, Flemish Militia, Kamayuk, Flaming Camel,
  archer versus cataphract and the rest); they stay as comments.
- Any stance change during a scenario; every player has one fixed side.
- Any game-side behaviour: the options do not lock markets, monks or siege in game.
- Slot data, XS, and the world version.
- Rescanning the vanilla AI include files ("scenario market" and the rest), which are not on this
  machine.
- Committing, merging or closing the pull requests.

## Further Notes

- PR 19's flags are judged usability, not building existence. A scenario scan disagreed with them in
  ten of sixteen scenarios; the flags win, and the rulings above are the only corrections.
- The working tree on `v0.3.0` holds uncommitted building-options work; this change adds to the
  options module and otherwise leaves those files alone.
- The scan scripts, their output and the extracted AI scripts are in the session scratchpad, not the
  repo.
- Moving defeat rules into per-player logic is recorded in ADR 0001 under this world's `docs/adr/`.
