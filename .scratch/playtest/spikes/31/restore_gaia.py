import json
import subprocess
import sys
import tempfile
from collections import Counter
from types import SimpleNamespace
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIPELAGO = HERE.parents[3]
sys.path.insert(0, str(ARCHIPELAGO))

from worlds.age2de.campaign.CampaignReader import Campaign
from worlds.age2de.campaign.ScenarioParser import restore_unsupported_properties
from worlds.age2de.AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.effects import EffectId
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists.capture_flag import CaptureFlag
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.heroes import HeroInfo
from AoE2ScenarioParser import settings

settings.SHOW_SCENARIO_VERSION_WARNINGS = False

AP_FOLDER = Path.home() / "Documents/GitHub/Ageipelago/age 2 files/resources/_common/scenario"
CAMPAIGN_FOLDER = Path("C:/Program Files (x86)/Steam/steamapps/common/AoE2DE/resources/_common/campaign")
OUT_SUFFIX = ""

CAMPAIGNS = {
    "Attila": ("xcam1.aoe2campaign", "C1_Attila_{}"),
    "Joan": ("cam2.aoe2campaign", "2_Joan_{}"),
    "Genghis": ("cam4.aoe2campaign", "4_Genghis_{}"),
}

SCYTHIAN_TROOP = {"AP_Attila_2": {UnitInfo.MANGUDAI.ID, UnitInfo.CAPPED_RAM.ID, UnitInfo.ONAGER.ID}}
ADDED_FLAGS = {"AP_Attila_1": (PlayerId.ONE, OtherInfo.FLAG_H.ID)}
MISSING_DECORATIONS = {"AP_Attila_2": {OtherInfo.GRASS_DRY.ID, OtherInfo.BAMBOO_STUMP.ID}}
TERRAIN_RESTORED = {"AP_Attila_2"}

NAMES = {}
for dataset in (UnitInfo, BuildingInfo, HeroInfo, OtherInfo):
    for member in dataset:
        NAMES.setdefault(member.ID, member.name)


def name_of(const):
    return NAMES.get(const, str(const))


def read(path):
    restore_unsupported_properties()
    return AoE2DEScenario.from_file(str(path))


def vanilla_bodies():
    bodies = {}
    for campaign, (bundle, pattern) in CAMPAIGNS.items():
        scenarios = Campaign(str(CAMPAIGN_FOLDER / bundle)).scenarios
        for chapter in range(1, 7):
            stem = pattern.format(chapter)
            found = [s for s in scenarios if Path(s.file_name).stem == stem]
            if len(found) != 1:
                raise SystemExit(f"{bundle}: {len(found)} scenarios named {stem}")
            bodies[f"AP_{campaign}_{chapter}"] = found[0].body
    return bodies


UNIT_FIELDS = ("player", "unit_const", "x", "y", "z", "reference_id", "rotation",
               "initial_animation_frame", "status")


def snapshot(source, target):
    scenario = read(source)
    Path(target).write_text(json.dumps({
        "scenario_version": scenario.scenario_version,
        "units": [{f: getattr(u, f) for f in UNIT_FIELDS} for u in units_of(scenario)],
        "terrain": [[t.terrain_id, t.elevation] for t in scenario.map_manager.terrain],
    }))


def read_vanilla(body, folder):
    source, target = Path(folder, "vanilla.aoe2scenario"), Path(folder, "vanilla.json")
    source.write_bytes(body)
    subprocess.run([sys.executable, __file__, "--snapshot", str(source), str(target)], check=True)
    data = json.loads(target.read_text())
    return SimpleNamespace(
        scenario_version=data["scenario_version"],
        units=[SimpleNamespace(**u) for u in data["units"]],
        terrain=[SimpleNamespace(terrain_id=t, elevation=e) for t, e in data["terrain"]],
    )


def units_of(scenario):
    if isinstance(scenario, SimpleNamespace):
        return scenario.units
    return scenario.unit_manager.get_all_units()


def terrain_of(scenario):
    if isinstance(scenario, SimpleNamespace):
        return scenario.terrain
    return scenario.map_manager.terrain


def place(unit):
    return unit.unit_const, unit.x, unit.y


def match(vanilla, ap):
    ap_units = units_of(ap)
    by_id = {u.reference_id: u for u in ap_units}
    by_place = {}
    for u in ap_units:
        by_place.setdefault(place(u), []).append(u)
    pairs, taken, missing = [], set(), []
    unmatched = []
    for v in units_of(vanilla):
        a = by_id.get(v.reference_id)
        if a is not None and place(a) == place(v) and id(a) not in taken:
            pairs.append((v, a))
            taken.add(id(a))
        else:
            unmatched.append(v)
    for v in unmatched:
        candidates = [a for a in by_place.get(place(v), []) if id(a) not in taken]
        if candidates:
            pairs.append((v, candidates[0]))
            taken.add(id(candidates[0]))
        else:
            missing.append(v)
    added = [a for a in ap_units if id(a) not in taken]
    return pairs, missing, added


def terrain_diff(vanilla, ap):
    diffs = []
    for v, a in zip(terrain_of(vanilla), terrain_of(ap)):
        if (v.terrain_id, v.elevation) != (a.terrain_id, a.elevation):
            diffs.append((v, a))
    return diffs


def in_area(effect, unit):
    if effect.area_x1 == -1:
        return True
    return (effect.area_x1 <= int(unit.x) <= effect.area_x2
            and effect.area_y1 <= int(unit.y) <= effect.area_y2)


def selects(effect, unit, owner):
    if effect.selected_object_ids:
        return unit.reference_id in effect.selected_object_ids
    if owner != effect.source_player:
        return False
    if effect.object_list_unit_id not in (-1, None) and effect.object_list_unit_id != unit.unit_const:
        return False
    return in_area(effect, unit)


def is_ap(trigger):
    return trigger.name.startswith("AP")


def ownership_effects(scenario):
    for trigger in scenario.trigger_manager.triggers:
        for effect in trigger.effects:
            if effect.effect_type == EffectId.CHANGE_OWNERSHIP:
                yield trigger, effect


def summarize(units):
    return ", ".join(f"{n} {name_of(c)}" for c, n in Counter(u.unit_const for u in units).most_common())


def describe(effect):
    if effect.selected_object_ids:
        where = f"ids {list(effect.selected_object_ids)}"
    elif effect.area_x1 == -1:
        where = "whole map"
    else:
        where = f"area ({effect.area_x1},{effect.area_y1})-({effect.area_x2},{effect.area_y2})"
    filters = []
    if effect.object_list_unit_id not in (-1, None):
        filters.append(f"unit {name_of(effect.object_list_unit_id)}")
    if effect.object_type not in (-1, None):
        filters.append(f"type {effect.object_type}")
    if effect.object_group not in (-1, None):
        filters.append(f"group {effect.object_group}")
    return f"P{effect.source_player}->P{effect.target_player} {where}" + (f" [{', '.join(filters)}]" if filters else "")


def report_diff(stem, vanilla, ap, out):
    pairs, missing, added = match(vanilla, ap)
    owners = [(v, a) for v, a in pairs if v.player != a.player]
    expected_added = [a for a in added if a.player == PlayerId.GAIA
                      and a.unit_const in SCYTHIAN_TROOP.get(stem, ())]
    other_added = [a for a in added if a not in expected_added]
    tiles = terrain_diff(vanilla, ap)
    out(f"  vanilla diff: {len(pairs)} matched, {len(owners)} owner, {len(missing)} missing, "
        f"{len(added)} added ({len(expected_added)} Scythian troop), {len(tiles)} terrain")
    for (vp, ap_), group in Counter((v.player, a.player) for v, a in owners).items():
        units = [a for v, a in owners if (v.player, a.player) == (vp, ap_)]
        out(f"    owner P{vp} vanilla, P{ap_} AP: {summarize(units)}")
    if missing:
        out(f"    missing from AP: {summarize(missing)}")
        by_id = {u.reference_id: u for u in units_of(ap)}
        for v in missing:
            a = by_id.get(v.reference_id)
            if a is not None and a.unit_const == v.unit_const:
                out(f"      {name_of(v.unit_const)} {v.reference_id} moved ({v.x},{v.y}) -> ({a.x},{a.y})")
    if other_added:
        for player, n in Counter(a.player for a in other_added).items():
            out(f"    added in AP, P{player}: {summarize([a for a in other_added if a.player == player])}")
    if tiles:
        kinds = Counter(((v.terrain_id, v.elevation), (a.terrain_id, a.elevation)) for v, a in tiles)
        for (was, now), n in kinds.items():
            out(f"    terrain {n} tiles: vanilla {was} AP {now}")
    return owners, missing, other_added, tiles


def patch(stem, vanilla, ap, out):
    pairs, missing, added = match(vanilla, ap)
    moved = [(v, a) for v, a in pairs if v.player == PlayerId.GAIA and a.player != PlayerId.GAIA]
    owner_before = {a.reference_id: a.player for _, a in moved}
    changed = bool(moved)

    gives, conflicts = [], []
    for trigger, effect in ownership_effects(ap):
        if not trigger.name.startswith("AP Give") or effect.target_player != PlayerId.ONE:
            continue
        hits = [a for _, a in moved if selects(effect, a, PlayerId.GAIA)
                or selects(effect, a, owner_before[a.reference_id])]
        if not hits or effect.source_player == PlayerId.GAIA:
            if hits:
                gives.append((trigger, effect, hits, False))
            continue
        others = [u for u in units_of(ap)
                  if u.reference_id not in owner_before and selects(effect, u, u.player)]
        if others:
            conflicts.append((trigger, effect, others))
        gives.append((trigger, effect, hits, True))

    for _, a in moved:
        a.player = PlayerId.GAIA
        a.capture_flag = CaptureFlag.NEVER
    if moved:
        out(f"  moved to Gaia, capture Never: {summarize([a for _, a in moved])} ({len(moved)})")

    staging = [(t, e) for t, e in ownership_effects(ap) if is_ap(t) and e.target_player == PlayerId.GAIA]
    emptied = []
    for trigger, effect in staging:
        out(f"  deleted staging effect in '{trigger.name}': {describe(effect)}")
        trigger.remove_effect(effect=effect)
        if not trigger.effects:
            emptied.append(trigger)
        changed = True
    for trigger in emptied:
        referrers = [t.name for t in ap.trigger_manager.triggers
                     for e in t.effects
                     if e.effect_type in (EffectId.ACTIVATE_TRIGGER, EffectId.DEACTIVATE_TRIGGER)
                     and e.trigger_id == trigger.trigger_id]
        note = f" (was referenced by {referrers})" if referrers else ""
        out(f"  deleted empty trigger '{trigger.name}'{note}")
    if emptied:
        ap.trigger_manager.remove_triggers([t.trigger_id for t in emptied])

    for trigger, effect, hits, flip in gives:
        if flip:
            out(f"  '{trigger.name}': source P{effect.source_player} -> Gaia, {describe(effect)}; "
                f"hands {len(hits)}")
            effect.source_player = PlayerId.GAIA
            changed = True
        else:
            out(f"  '{trigger.name}': already Gaia, {describe(effect)}; hands {len(hits)}")
    for trigger, effect, others in conflicts:
        out(f"  !! '{trigger.name}' also selected non-Gaia-in-vanilla objects that now stay put: "
            f"{summarize(others)}")

    if stem in ADDED_FLAGS:
        player, const = ADDED_FLAGS[stem]
        flags = [a for a in added if a.player == player and a.unit_const == const]
        for flag in flags:
            ap.unit_manager.remove_unit(unit=flag)
        out(f"  removed {len(flags)} added P{player} {name_of(const)}: "
            f"{[(f.reference_id, f.x, f.y) for f in flags]}")
        changed = changed or bool(flags)

    if stem in MISSING_DECORATIONS:
        taken = {u.reference_id for u in units_of(ap)}
        restored = [v for v in missing if v.player == PlayerId.GAIA and v.unit_const in MISSING_DECORATIONS[stem]]
        reissued = 0
        for v in restored:
            ref = v.reference_id if v.reference_id not in taken else None
            reissued += ref is None
            unit = ap.unit_manager.add_unit(
                PlayerId.GAIA, v.unit_const, x=v.x, y=v.y, z=v.z, rotation=v.rotation,
                animation_frame=v.initial_animation_frame, status=v.status, reference_id=ref,
            )
            taken.add(unit.reference_id)
        out(f"  put back {len(restored)} decorations: {summarize(restored)} "
            f"({reissued} under a new reference id)")
        changed = changed or bool(restored)

    if stem in TERRAIN_RESTORED:
        tiles = terrain_diff(vanilla, ap)
        for v, a in tiles:
            a.terrain_id, a.elevation = v.terrain_id, v.elevation
        out(f"  restored {len(tiles)} terrain tiles: "
            f"{sorted(Counter((a.terrain_id, a.elevation) for _, a in tiles).items())}")
        changed = changed or bool(tiles)

    return changed, {a.reference_id for _, a in moved}


def verify(stem, vanilla, ap, moved_ids, out):
    problems = []
    by_id = {u.reference_id: u for u in units_of(ap)}
    for ref in moved_ids:
        u = by_id.get(ref)
        if u is None or u.player != PlayerId.GAIA or u.capture_flag != CaptureFlag.NEVER:
            problems.append(f"object {ref} is {u!r}")
    for trigger, effect in ownership_effects(ap):
        if is_ap(trigger) and effect.target_player == PlayerId.GAIA:
            problems.append(f"'{trigger.name}' still changes ownership to Gaia")
        if trigger.name.startswith("AP Give") and effect.source_player != PlayerId.GAIA:
            hit = [ref for ref in moved_ids if selects(effect, by_id[ref], by_id[ref].player)]
            if hit:
                problems.append(f"'{trigger.name}' selects moved objects {hit} from P{effect.source_player}")
    for p in problems:
        out(f"  !! {p}")
    out(f"  verify: {'ok' if not problems else f'{len(problems)} problems'}")
    return not problems


def main():
    if sys.argv[1:2] == ["--snapshot"]:
        snapshot(sys.argv[2], sys.argv[3])
        return
    write = "--write" in sys.argv
    lines = []

    def out(line):
        print(line)
        lines.append(line)

    bodies = vanilla_bodies()
    all_ok = True
    with tempfile.TemporaryDirectory() as folder:
        for stem, body in bodies.items():
            out(f"{stem}")
            vanilla = read_vanilla(body, folder)
            ap = read(AP_FOLDER / f"{stem}.aoe2scenario")
            out(f"  AP map v{ap.scenario_version}, vanilla v{vanilla.scenario_version}")
            out(" before:")
            report_diff(stem, vanilla, ap, out)
            changed, moved_ids = patch(stem, vanilla, ap, out)
            if not changed:
                out("  unchanged, not written")
                continue
            target = AP_FOLDER / f"{stem}{OUT_SUFFIX}.aoe2scenario"
            if not write:
                continue
            ap.write_to_file(str(target))
            written = read(target)
            out(f" after ({target.name}):")
            report_diff(stem, vanilla, written, out)
            all_ok &= verify(stem, vanilla, written, moved_ids, out)
    (HERE / ("report.txt" if write else "scan.txt")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if write and not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
