"""Write every economy route out in a readable form, so a broken one is visible at a glance.

    python -m worlds.age2de.tools.route_catalog        # from the repository root

`test_route_catalog.py` renders the same thing and fails when it has drifted from the committed
`test/route_catalog.md`, so a route added, renamed, repriced or multiplied arrives as a diff a
human can read rather than as a number nobody checks.

Two faults the catalog makes obvious:

- a route **possible nowhere** is dead: no scenario can ever run it;
- a route whose **needs no route yields** can never run even where it is possible, because an
  economy seed is met only by another route already yielding.
"""
from __future__ import annotations

import collections
import pathlib

CATALOG = pathlib.Path(__file__).resolve().parents[1] / "test" / "route_catalog.md"
CAMPAIGNS = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
SEED = 19


def build_world():
    """One seed, every campaign, default options - the catalog is about the rules, not a roll."""
    from test.general import setup_solo_multiworld

    from worlds.age2de import Age2World

    world = setup_solo_multiworld(Age2World, (), seed=SEED).worlds[1]
    world.options.enabled_campaigns.value = set(CAMPAIGNS)
    world.options.starting_campaigns.value = set(CAMPAIGNS)
    for step in ("generate_early", "create_regions", "create_items", "set_rules"):
        getattr(world, step)()
    return world


def _strengths(amounts) -> str:
    return ", ".join(f"{resource.name.lower()} {strength.name.lower().replace('_', ' ')}"
                     for resource, strength in sorted(amounts.items(),
                                                      key=lambda pair: pair[0].value)) or "-"


def _signature(economy) -> tuple:
    return tuple((route.name, _strengths(route.yields), _strengths(route.needs))
                 for route in economy.routes)


def render(world) -> str:
    """The catalog as markdown. Scenarios sharing a route list share a table: they almost always
    do, and printing eighteen copies of one table would hide the scenario that differs."""
    economies = {
        scenario.scenario.name: scenario.economy.has_economy_routes().resolve(world)
        for scenario in sorted(world.rules.logic.scenarios, key=lambda s: s.scenario.name)
    }
    groups: dict[tuple, list[str]] = {}
    for name, economy in economies.items():
        groups.setdefault(_signature(economy), []).append(name)

    possible_in: collections.Counter[str] = collections.Counter()
    for economy in economies.values():
        possible_in.update({economy.routes[index].name for index in economy.possible})
        possible_in.update({route.name: 0 for route in economy.routes})
    lines = [
        "# Economy route catalog",
        "",
        "Every economy route the logic builds, and how many of the "
        f"{len(economies)} scenarios can run each one.",
        "",
        "    python -m worlds.age2de.tools.route_catalog",
        "",
        "Regenerate with that and commit the diff. `test_route_catalog.py` pins it.",
        "",
    ]
    lines += _problems(economies, possible_in)
    for signature, scenarios in groups.items():
        lines += [
            "",
            f"## {len(signature)} routes"
            + (" - every scenario" if len(groups) == 1 else f" - {', '.join(scenarios)}"),
            "",
            "| route | yields | needs | possible in |",
            "| --- | --- | --- | --- |",
        ]
        for name, yields, needs in signature:
            lines.append(f"| {name} | {yields} | {needs} | "
                         f"{possible_in[name]}/{len(economies)} |")
    lines += ["", "## Per scenario", "", "| scenario | routes | possible |", "| --- | --- | --- |"]
    for name, economy in economies.items():
        lines.append(f"| {name} | {len(economy.routes)} | {len(economy.possible)} |")
    return "\n".join(lines) + "\n"


def _problems(economies, possible_in) -> list[str]:
    """A route is starved only where it is *possible*; elsewhere its needs are moot. Flag one
    only when it is starved everywhere it is possible, which means it can never run at all."""
    starved_in: collections.Counter[str] = collections.Counter()
    live_in: collections.Counter[str] = collections.Counter()
    for economy in economies.values():
        for index in economy.possible:
            route = economy.routes[index]
            live_in[route.name] += 1
            others = frozenset(economy.possible) - {index}
            if route.needs and not economy.are_needs_met(route, others):
                starved_in[route.name] += 1
    dead = sorted(name for name, count in possible_in.items() if not count)
    starved = sorted(name for name, count in starved_in.items() if count == live_in[name])

    lines = ["## Worth a look", "",
             "Rendered at **default options**, so a route gated behind an option (Market Trade) "
             "or absent from every map (oysters, whales) reads as unreachable here and is not "
             "necessarily a fault. A fixed-force scenario runs no routes at all, by design.", ""]
    if not dead and not starved:
        return lines + ["Nothing: every route is reachable somewhere, and every reachable route "
                        "has something to seed it.", ""]
    for name in dead:
        lines.append(f"- **{name}** is reachable in no scenario.")
    for name in starved:
        lines.append(f"- **{name}** is reachable in {live_in[name]} scenario(s) and starved in "
                     f"all of them: no other route yields what it needs, so it never runs.")
    return lines + [""]


if __name__ == "__main__":
    CATALOG.write_text(render(build_world()), encoding="utf-8", newline="\n")
    print(f"wrote {CATALOG}")
