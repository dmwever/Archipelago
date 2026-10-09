
import os
import struct

DE_DEPENDENCY_NUM = 7
RGE_DE2_MAX_CHAR = 256

RGE_STRING_ID = 0x0A60

CPN_VERSION = 808463922             # the four bytes "2.00", read as a little-endian int
DE_DEPENDENCIES = (6, 2, 3, 4, 5, 6, 7)


class CpnHeader:
    version: int
    dependencies: tuple
    name_raw: bytes
    name: str
    scenarioNum: int

    def __init__(self, fp=None):
        if fp is None:
            return
        self.version = struct.unpack("i", fp.read(4))[0]
        self.dependencies = struct.unpack("iiiiiii", fp.read(DE_DEPENDENCY_NUM * 4))
        self.name_raw = struct.unpack(f"{str(RGE_DE2_MAX_CHAR)}s", fp.read(RGE_DE2_MAX_CHAR))[0]
        self.name = self.name_raw.split(b"\x00")[0].decode("utf-8")
        self.scenarioNum = struct.unpack("i", fp.read(4))[0]

    @classmethod
    def create(cls, name: str, scenario_count: int) -> 'CpnHeader':
        header = cls()
        header.version = CPN_VERSION
        header.dependencies = DE_DEPENDENCIES
        header.name = name
        header.name_raw = name.encode("utf-8")
        header.scenarioNum = scenario_count
        return header


class Scenario:
    size: int
    offset: int
    name: str
    name_len: int
    file_name: str
    file_name_len: int
    name_string_id: int
    file_name_string_id: int
    body: bytes

    def __init__(self, fp=None):
        if fp is None:
            self.body = b""
            return
        self.size = struct.unpack("i", fp.read(4))[0]
        self.offset = struct.unpack("i", fp.read(4))[0]
        self.name_string_id = struct.unpack("H", fp.read(2))[0]
        self.name_len = struct.unpack("H", fp.read(2))[0]
        self.name = (struct.unpack(f"{str(self.name_len)}s", fp.read(self.name_len))[0]).decode("utf-8")
        self.file_name_string_id = struct.unpack("H", fp.read(2))[0]
        self.file_name_len = struct.unpack("H", fp.read(2))[0]
        self.file_name = (struct.unpack(f"{str(self.file_name_len)}s", fp.read(self.file_name_len))[0]).decode("utf-8")
        self.body = b""

    @classmethod
    def from_file(cls, file_name: str, body: bytes) -> 'Scenario':
        scenario = cls()
        encoded_len = len(file_name.encode("utf-8"))
        scenario.size = len(body)
        scenario.offset = 0
        scenario.name = file_name
        scenario.name_len = encoded_len
        scenario.name_string_id = RGE_STRING_ID
        scenario.file_name = file_name
        scenario.file_name_len = encoded_len
        scenario.file_name_string_id = RGE_STRING_ID
        scenario.body = body
        return scenario


class Campaign:
    header: CpnHeader

    def __init__(self, filename: str = None, outFolder: str = None):
        self.scenarios: list[Scenario] = []
        if filename is None:
            return

        with open(filename, "rb") as fp:
            self.header = CpnHeader(fp)

            for _ in range(self.header.scenarioNum):
                self.scenarios.append(Scenario(fp))

            for scn in self.scenarios:
                fp.seek(scn.offset)
                scn.body = fp.read(scn.size)

        if outFolder is not None:
            os.makedirs(outFolder, exist_ok=True)
            for scn in self.scenarios:
                with open(os.path.join(outFolder, scn.file_name), "wb") as out:
                    out.write(scn.body)

    @classmethod
    def from_scenarios(cls, name: str, entries) -> 'Campaign':
        campaign = cls()
        campaign.scenarios = [Scenario.from_file(file_name, body) for file_name, body in entries]
        campaign.header = CpnHeader.create(name, len(campaign.scenarios))
        return campaign
