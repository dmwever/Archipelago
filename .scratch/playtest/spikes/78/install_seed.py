import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

AGE2_FILES = Path(r"C:\Users\dmwev\Documents\GitHub\Ageipelago\age 2 files")
BACKUP = HERE / "installed_backup"
XS_FILES = ("SlotData.xs", "TechData.xs", "UnitData.xs")


def parse_args():
    ap = argparse.ArgumentParser(
        description="Write SlotData/TechData/UnitData for a seed into the live xs folder. "
                    "Campaign bundles are not rebuilt.")
    ap.add_argument("--techsanity", default="all",
                    choices=["none", "units", "generic", "all"])
    ap.add_argument("--unitsanity", default="all", choices=["none", "unit_line", "all"])
    ap.add_argument("--caveman", default="yes", choices=["yes", "no"])
    ap.add_argument("--seed", default="techoff", help="seed tag input")
    ap.add_argument("--restore", action="store_true", help="put the backed-up files back")
    return ap.parse_args()


def restore():
    if not BACKUP.is_dir():
        print(f"no backup at {BACKUP}")
        return 2
    for name in XS_FILES:
        shutil.copyfile(BACKUP / name, AGE2_FILES / "resources/_common/xs" / name)
    print(f"restored {', '.join(XS_FILES)} from {BACKUP.name}")
    return 0


def main():
    args = parse_args()
    if args.restore:
        return restore()

    from worlds.age2de import Age2World
    from worlds.age2de.Options import Techsanity, Unitsanity, UnitsanityItems
    from worlds.age2de.client.handlers.InstallHandler import InstallHandler
    from worlds.age2de.generation import Identity
    from worlds.age2de.locations.connections.LocationMapping import location_name_to_id
    from worlds.age2de.locations.Campaigns import NAME_TO_CAMPAIGN
    from test.general import setup_solo_multiworld

    ts = {"none": Techsanity.option_none, "units": Techsanity.option_units,
          "generic": Techsanity.option_generic, "all": Techsanity.option_all}[args.techsanity]
    us = {"none": Unitsanity.option_none, "unit_line": Unitsanity.option_unit_line,
          "all": Unitsanity.option_all}[args.unitsanity]

    world = setup_solo_multiworld(Age2World, ()).worlds[1]
    every = {"Attila the Hun", "Joan of Arc", "Genghis Khan"}
    world.options.enabled_campaigns.value = set(every)
    world.options.starting_campaigns.value = {"Attila the Hun"}
    world.options.techsanity.value = ts
    world.options.unitsanity.value = us
    world.options.unitsanity_items.value = UnitsanityItems.option_unit_line
    world.options.caveman.value = 1 if args.caveman == "yes" else 0
    world.generate_early()
    world.create_regions()
    world.create_items()

    slot_data = world.fill_slot_data()
    location_ids = [location_name_to_id[location.name]
                    for location in world.multiworld.get_locations(1)
                    if location.name in location_name_to_id]

    xs_dir = AGE2_FILES / "resources/_common/xs"
    if not xs_dir.is_dir():
        print(f"xs folder not found at {xs_dir}")
        return 2

    BACKUP.mkdir(exist_ok=True)
    for name in XS_FILES:
        source = xs_dir / name
        if source.is_file() and not (BACKUP / name).exists():
            shutil.copyfile(source, BACKUP / name)
            print(f"backed up {name}")

    handler = InstallHandler()
    handler.set_user_folder(str(AGE2_FILES))
    campaigns = [NAME_TO_CAMPAIGN[name] for name in sorted(every)]
    handler.setup(campaigns, 1, Identity.seed_tag(args.seed, 1), "Spike",
                  slot_data, location_ids)

    written = [handler._write_slot_data(), handler._write_tech_data(),
               handler._write_unit_data()]
    for path in written:
        print(f"wrote {Path(path).name}")

    print()
    print(f"techsanity={args.techsanity} unitsanity={args.unitsanity} "
          f"caveman={args.caveman} locations={len(location_ids)}")
    print(f"restore the previous seed with: py -3 {Path(__file__).name} --restore")
    return 0


if __name__ == "__main__":
    sys.exit(main())
