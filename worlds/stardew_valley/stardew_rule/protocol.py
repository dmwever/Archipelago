from __future__ import annotations

from abc import abstractmethod
from typing import Tuple, Protocol, runtime_checkable

from BaseClasses import CollectionState
from .explanation import ExplainableRule
from ..options import StardewValleyOptions


class PlayerWorldContext(Protocol):
    """
    Offers a read only view on the multi world, from the player perspective.
    """
    player: int
    options: StardewValleyOptions
    # Maybe add starting inventory


@runtime_checkable
class StardewRule(ExplainableRule, Protocol):

    @abstractmethod
    def __call__(self, state: CollectionState, context: PlayerWorldContext) -> bool:
        ...

    @abstractmethod
    def evaluate_while_simplifying(self, state: CollectionState, context: PlayerWorldContext) -> Tuple[StardewRule, bool]:
        ...

    # TODO does this need the context?
    @abstractmethod
    def get_difficulty(self):
        ...

    @abstractmethod
    def __or__(self, other) -> StardewRule:
        ...

    @abstractmethod
    def __and__(self, other) -> StardewRule:
        ...
