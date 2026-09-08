import re
import zlib

TAG_LENGTH = 8

TAGGED_XSDAT = re.compile(r"^AP[ _].*_([0-9a-f]{%d})\.xsdat$" % TAG_LENGTH)


def seed_tag(seed_name: str, slot: int) -> str:
    return format(zlib.crc32(f"{seed_name}:{slot}".encode()) & 0xFFFF_FFFF, "0%dx" % TAG_LENGTH)


def tagged(stem: str, tag: str) -> str:
    return f"{stem}_{tag}" if tag else stem


def xsdat_name(stem: str, tag: str) -> str:
    return tagged(stem, tag) + ".xsdat"


def scenario_file_name(stem: str, tag: str) -> str:
    return tagged(stem, tag) + ".aoe2scenario"


def campaign_file_name(stem: str, tag: str) -> str:
    return tagged(stem, tag) + ".aoe2campaign"


def tag_of(file_name: str) -> str:
    match = TAGGED_XSDAT.match(file_name)
    return match.group(1) if match else ""
