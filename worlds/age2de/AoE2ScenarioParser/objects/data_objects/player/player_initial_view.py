from ...aoe2_object import AoE2Object
from ....sections.retrievers.retriever_object_link import RetrieverObjectLink
from ....sections.retrievers.retriever_object_link_group import RetrieverObjectLinkGroup


class PlayerInitialView(AoE2Object):

    _link_list = [
        RetrieverObjectLinkGroup("Map", "initial_player_views[__index__]", group=[
            RetrieverObjectLink("location_x"),
            RetrieverObjectLink("location_y"),
        ])
    ]

    def __init__(self, location_x: int, location_y: int, **kwargs):
        super().__init__(**kwargs)

        self.location_x: int = location_x
        self.location_y: int = location_y
