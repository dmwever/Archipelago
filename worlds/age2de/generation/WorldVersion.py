from Utils import Version, tuplize_version

SLOT_DATA_KEY = "world_version"

UNKNOWN = Version(0, 0, 0)


def parse(value) -> Version:
    if value is None:
        return UNKNOWN
    if isinstance(value, Version):
        return value
    if isinstance(value, (list, tuple)):
        return Version(*(list(value) + [0, 0, 0])[:3])
    try:
        return tuplize_version(str(value))
    except (ValueError, TypeError):
        return UNKNOWN


def compatible(seed: Version, client: Version) -> bool:
    return seed[:2] == client[:2]


def describe(seed: Version, client: Version) -> str:
    generated = ("did not record an Age2 version" if seed == UNKNOWN
                 else f"was generated with Age2 {seed.as_simple_string()}")
    return (f"This seed {generated} but this client is {client.as_simple_string()}. "
            f"Update the apworld, or regenerate the seed.")
