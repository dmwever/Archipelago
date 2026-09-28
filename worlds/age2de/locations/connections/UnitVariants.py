"""Extra genie ids that ARE the same unit.

Two sources. The same unit trained at a different building keeps a separate id, so a Tarkan
from the Stable is not id 755 but 886. And a villager takes a new id for every job it does,
so counting only the base id misses every villager that is currently working - which is most
of them. Anything that counts owned units has to sum game_id and these.

Imported for its side effect: binds Age2UnitData.variant_game_ids.
"""

from ..Units import Age2UnitData
from ..VillagerJobs import Age2VillagerJobData


UNIT_TO_VARIANT_IDS: dict[Age2UnitData, list[int]] = {
    Age2UnitData.HUSKARL: [759],
    Age2UnitData.VILLAGER_MALE: [56, 118, 120, 122, 123, 124, 156, 259, 579, 592, 1810, 1892, 2333],
    Age2UnitData.SPEARMAN: [1786],
    Age2UnitData.VILLAGER_FEMALE: [57, 212, 214, 216, 218, 220, 222, 354, 581, 590, 1891, 2334],
    Age2UnitData.PIKEMAN: [1787],
    Age2UnitData.HALBERDIER: [1788],
    Age2UnitData.ELITE_HUSKARL: [761],
    Age2UnitData.TARKAN: [886],
    Age2UnitData.ELITE_TARKAN: [887],
    Age2UnitData.KONNIK: [1254],
    Age2UnitData.ELITE_KONNIK: [1255],
    Age2UnitData.SERJEANT: [1660],
    Age2UnitData.ELITE_SERJEANT: [1661],
}


for unit, variant_ids in UNIT_TO_VARIANT_IDS.items():
    unit.variant_game_ids = variant_ids


assert not [unit for unit in Age2UnitData
            if unit.game_id in unit.variant_game_ids], \
    "a variant id repeats the unit's own game_id"

_villager_variants = set(Age2UnitData.VILLAGER_MALE.variant_game_ids)     | set(Age2UnitData.VILLAGER_FEMALE.variant_game_ids)
assert not [job for job in Age2VillagerJobData
            if job.game_id not in _villager_variants],     "a villager job names an id the villager does not take"
