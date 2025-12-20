from typing import List

from ...aoe2_object import AoE2Object
from ..unit import Unit
from ....sections.retrievers.retriever_object_link import RetrieverObjectLink
from ....sections.retrievers.retriever_object_link_group import RetrieverObjectLinkGroup


class PlayerUnits(AoE2Object):

    _link_list = [
        RetrieverObjectLinkGroup("Units", "players_units[__index__]", group=[
            RetrieverObjectLink("unit_count"),
            RetrieverObjectLink("units", process_as_object=Unit),
        ])
    ]

    def __init__(self, unit_count: int, units: List[Unit], **kwargs):
        super().__init__(**kwargs)

        self.unit_count: int = unit_count
        self.units: List[Unit] = units
