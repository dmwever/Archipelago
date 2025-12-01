import struct

from numpy import array

def read_bool(fp) -> bool:
    return struct.unpack("<?xxx", fp.read(4))[0]

def read_vector(fp) -> tuple[float, float, float]:
    return array(struct.unpack("<fff", fp.read(12)))

def read_int(fp) -> int:
    return struct.unpack("<i", fp.read(4))[0]

def read_float(fp) -> float:
    return struct.unpack("<f", fp.read(4))[0]

def read_string(fp) -> str:
    len = struct.unpack("<i", fp.read(4))[0]
    struct.unpack(f"{str(len)}s", fp.read(len))[0]
    
def skip_int(fp, len):
    struct.unpack(f"{len*4}s", fp.read(len * 4))