from pathlib import Path
import struct

from .CampaignReader import DE_DEPENDENCY_NUM, RGE_DE2_MAX_CHAR, Campaign, Scenario

HEADER_SIZE = 4 + DE_DEPENDENCY_NUM * 4 + RGE_DE2_MAX_CHAR + 4
SCENARIO_FIXED_SIZE = struct.calcsize("<ii") + 2 * struct.calcsize("<HH")


def _encode_name_field(name: str) -> bytes:
    encoded = name.encode("utf-8")
    if len(encoded) >= RGE_DE2_MAX_CHAR:
        raise ValueError(
            f"Campaign name is {len(encoded)} bytes, which does not fit the "
            f"{RGE_DE2_MAX_CHAR}-byte field with a terminator: {name!r}")
    return encoded + b"\x00" * (RGE_DE2_MAX_CHAR - len(encoded))


def _scenario_size(scenario: Scenario) -> int:
    return (SCENARIO_FIXED_SIZE
            + len(scenario.name.encode("utf-8"))
            + len(scenario.file_name.encode("utf-8")))


def _pack_scenario_header(scenario: Scenario, offset: int) -> bytes:
    name = scenario.name.encode("utf-8")
    file_name = scenario.file_name.encode("utf-8")
    return (
        struct.pack("<ii", len(scenario.body), offset)
        + struct.pack("<HH", scenario.name_string_id, len(name)) + name
        + struct.pack("<HH", scenario.file_name_string_id, len(file_name)) + file_name
    )


def write(campaign: Campaign, write_path: Path, display_name: str):
    name_field = (_encode_name_field(display_name) if display_name is not None
                  else campaign.header.name_raw)

    offset = HEADER_SIZE + sum(_scenario_size(scn) for scn in campaign.scenarios)

    scenario_headers = b""
    for scn in campaign.scenarios:
        scenario_headers += _pack_scenario_header(scn, offset)
        offset += len(scn.body)
    
    header = (
        struct.pack("<i", campaign.header.version)
        + struct.pack("<7i", *campaign.header.dependencies)
        + name_field
        + struct.pack("<i", len(campaign.scenarios))
    )
    assert len(header) == HEADER_SIZE, len(header)
    
    write_path.write_bytes(header + scenario_headers + b"".join(scn.body for scn in campaign.scenarios))
    
