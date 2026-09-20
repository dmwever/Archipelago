import re
import zlib

import Utils

TAG_LENGTH = 8
SOURCE_SUFFIX = " Template"

TAGGED_XSDAT = re.compile(r"^AP[ _].*_([0-9a-f]{%d})\.xsdat$" % TAG_LENGTH)

# Tab and newline are left in so they collapse to a space rather than welding two words together;
# every other C0 control is not text and simply goes. Spelled out rather than using str.isspace(),
# which also counts the separator controls 0x1c-0x1f.
COLLAPSIBLE = frozenset(" \t\n\r\v\f")
CONTROL_CHARS = frozenset(chr(code) for code in range(0x20)) - COLLAPSIBLE


def seed_tag(seed_name: str, slot: int) -> str:
    return format(zlib.crc32(f"{seed_name}:{slot}".encode()) & 0xFFFF_FFFF, "0%dx" % TAG_LENGTH)


def sanitize_player(name: str) -> str:
    """The part of a player name usable in a file name, or '' if nothing survives.

    Archipelago truncates slot names to 16 characters but leaves the characters themselves alone,
    so a name can still carry separators, quotes or control codes. Length is therefore not our
    problem; legality on disk is.
    """
    safe = Utils.get_file_safe_name(name)
    safe = "".join(char for char in safe if char not in CONTROL_CHARS)
    # A trailing dot or space is legal in the string but not at the end of a Windows file name.
    return " ".join(safe.split()).strip(" .")

def tagged(stem: str, tag: str) -> str:
    return f"{stem}_{tag}" if tag else stem

def file_stem(stem: str, tag: str, player: str) -> str:
    """The player goes before the tag so that the tag stays the last segment, which is what
    TAGGED_XSDAT and tag_of rely on. Generation refuses a slot whose name sanitizes to nothing,
    so player is always something."""
    return tagged(f"{stem}_{player}", tag)


def xsdat_name(stem: str, tag: str) -> str:
    return tagged(stem, tag) + ".xsdat"


def scenario_file_name(stem: str, tag: str) -> str:
    return tagged(stem, tag) + ".aoe2scenario"


def campaign_file_name(stem: str, tag: str, player: str) -> str:
    return file_stem(stem, tag, player) + ".aoe2campaign"


def campaign_xsdat_name(stem: str, tag: str, player: str) -> str:
    """What the engine writes while a campaign installed under this name is played."""
    return file_stem(stem, tag, player) + ".xsdat"

def storage_file_name(stem: str, tag: str, player: str) -> str:
    return file_stem(stem, tag, player) + ".json"


def source_campaign_stem(stem: str) -> str:
    """The shipped bundle's stem. The suffix keeps the source apart from the player copies in the
    same folder, and is dropped from every name the player sees or the engine writes."""
    return stem + SOURCE_SUFFIX


def source_campaign_file_name(stem: str) -> str:
    """The untagged bundle shipped with the mod, which /install reads and never writes."""
    return source_campaign_stem(stem) + ".aoe2campaign"


def tag_of(file_name: str) -> str:
    match = TAGGED_XSDAT.match(file_name)
    return match.group(1) if match else ""
