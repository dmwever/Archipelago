
import os
import struct

DE_DEPENDENCY_NUM = 7
RGE_DE2_MAX_CHAR = 256

RGE_STRING_ID = 0x0A60


class CpnHeader:
    version: int
    dependencies: tuple
    name_raw: bytes
    name: str
    scenarioNum: int

    def __init__(self, fp):
        self.version = struct.unpack("i", fp.read(4))[0]
        self.dependencies = struct.unpack("iiiiiii", fp.read(DE_DEPENDENCY_NUM * 4))
        self.name_raw = struct.unpack(f"{str(RGE_DE2_MAX_CHAR)}s", fp.read(RGE_DE2_MAX_CHAR))[0]
        self.name = self.name_raw.split(b"\x00")[0].decode("utf-8")
        self.scenarioNum = struct.unpack("i", fp.read(4))[0]


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

    def __init__(self, fp):
        self.size = struct.unpack("i", fp.read(4))[0]
        self.offset = struct.unpack("i", fp.read(4))[0]
        self.name_string_id = struct.unpack("H", fp.read(2))[0]
        self.name_len = struct.unpack("H", fp.read(2))[0]
        self.name = (struct.unpack(f"{str(self.name_len)}s", fp.read(self.name_len))[0]).decode("utf-8")
        self.file_name_string_id = struct.unpack("H", fp.read(2))[0]
        self.file_name_len = struct.unpack("H", fp.read(2))[0]
        self.file_name = (struct.unpack(f"{str(self.file_name_len)}s", fp.read(self.file_name_len))[0]).decode("utf-8")
        self.body = b""


class Campaign:
    header: CpnHeader

    def __init__(self, filename: str, outFolder: str = None):
        self.scenarios: list[Scenario] = []

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
