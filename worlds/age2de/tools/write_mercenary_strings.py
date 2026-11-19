import argparse
import pathlib

from worlds.age2de.items.Items import CATEGORY_TO_ITEMS, Age2ItemData, Mercenary
from worlds.age2de.locations.Heroes import Age2HeroData
from worlds.age2de.locations.Units import Age2UnitData

LANGUAGES = [
    "br",
    "de",
    "en",
    "es",
    "fr",
    "hi",
    "it",
    "jp",
    "ko",
    "ms",
    "mx",
    "pl",
    "ru",
    "tr",
    "tw",
    "vi",
    "zh",
]
RESOURCES = pathlib.Path("age 2 files", "mods", "local", "Ageipelago", "resources")
STRINGS_FILE = pathlib.Path("strings", "key-value", "key-value-modded-strings-utf8.txt")

def strings_file(ageipelago: pathlib.Path, language: str) -> pathlib.Path:
    return ageipelago / RESOURCES / language / STRINGS_FILE

def display_name(unit: Age2UnitData | Age2HeroData) -> str:
    if isinstance(unit, Age2HeroData):
        return unit.hero_name
    return unit.unit_name

def mercenary_name(mercenary: Age2ItemData) -> str:
    return mercenary.item_name.partition(": ")[2]

def mercenary_description(mercenary: Age2ItemData) -> str:
    units = ", ".join(
        f"{display_name(mercenary_unit.unit)} ×{mercenary_unit.count}"
        for mercenary_unit in mercenary.type.units
    )
    return f"{mercenary_name(mercenary)}\\n{units}"

def render_strings_file() -> bytes:
    mercenaries = sorted(CATEGORY_TO_ITEMS[Mercenary], key=lambda item: item.id)
    lines = [
        f'{mercenary.type.name_string_id} "{mercenary_description(mercenary)}"\r\n'
        for mercenary in mercenaries
    ]
    return "".join(lines).encode("utf-8")

def write_strings_files(ageipelago: pathlib.Path) -> None:
    contents = render_strings_file()
    for language in LANGUAGES:
        path = strings_file(ageipelago, language)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ageipelago", type=pathlib.Path)
    arguments = parser.parse_args()
    write_strings_files(arguments.ageipelago)

if __name__ == "__main__":
    main()
