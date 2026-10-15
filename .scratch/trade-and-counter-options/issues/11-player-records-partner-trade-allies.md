# 11: Player trade records and partner_trade with allies

**What to build:** Every connected scenario's `Player` enum covers its allies and enemies, each
carrying a fixed side, a main-opponent flag, usable market, usable dock, and a gate per enemy
building (defeat its owner, or none). Seed the records by the agreed rule (PR 19 flag true: a player
on that side is usable if it owns the building at start or its AI builds one, unless it is a main
opponent; flag false: none usable) and apply every design ruling listed in the spec. The
scenario-level ally/enemy market and dock facts are derived from the records. `trading_ally`
defaults from the records and a starting state can still override it. A `partner_trade` option
(none / allies / allies and enemies, default allies) replaces `ALLY_TRADE`; this ticket makes `none`
and `allies` work.

Spec: Implementation Decisions, "Player records", "Seeding the records", "Trade logic". Glossary:
Trade partner, Partner trade, Main opponent.

Data for seeding (who owns or builds which market or dock, per slot): `../research/` - start with
its README. The raw per-scenario rulings are in `../research/grill-decisions.md`.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] Tests first, through economy rules on a built world
- [ ] Records match every ruling in the spec (sides, neutral/ignored slots absent, main opponents, overridden flags)
- [ ] Derived scenario flags agree with the records for every connected scenario
- [ ] `none`: no partner trade anywhere; `allies`: trade opens only where an ally has a usable building
- [ ] `trading_ally` follows the records, and a starting-state override still wins
- [ ] `ALLY_TRADE` constant gone; option not in slot data or XS
- [ ] Ageipelago option reference page and index row added
- [ ] Full suite green
