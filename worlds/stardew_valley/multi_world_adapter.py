from dataclasses import dataclass
from typing import Iterable, Union, Set

from BaseClasses import MultiWorld, Entrance, Location, CollectionState
from worlds.generic import Rules as MultiWorldRules
from worlds.generic.Rules import CollectionRule
from .options import StardewValleyOptions
from .stardew_rule import StardewRule
from .stardew_rule.literal import LiteralStardewRule
from .stardew_rule.protocol import PlayerWorldContext


@dataclass(frozen=True)
class ContextualizedRule(CollectionRule):
    context: PlayerWorldContext
    rule: StardewRule

    def __call__(self, state: CollectionState):
        return self.rule(state, self.context)


@dataclass(frozen=True)
class PlayerMultiWorldAdapter(PlayerWorldContext):
    """
    Wrap the usage of the multi world to avoid always needing to pass the player and options context.
    """
    multi_world: MultiWorld

    player: int
    options: StardewValleyOptions

    def get_entrance(self, name: str) -> Entrance:
        return self.multi_world.get_entrance(name, self.player)

    def get_location(self, name: str) -> Location:
        return self.multi_world.get_location(name, self.player)

    def get_all_locations(self) -> Iterable[Location]:
        return self.multi_world.get_locations(self.player)

    def _add_context(self, rule: StardewRule):
        if isinstance(rule, LiteralStardewRule):
            return rule

        return ContextualizedRule(self, rule)

    def set_entrance_rule(self, entrance_name: str, rule: StardewRule):
        entrance = self.get_entrance(entrance_name)
        MultiWorldRules.set_rule(entrance, self._add_context(rule))

    def set_location_rule(self, location_name: str, rule: StardewRule):
        location = self.get_location(location_name)
        MultiWorldRules.set_rule(location, self._add_context(rule))

    # FIXME we should not use add, only set so we make sure to always keep the StardewRule to use the optimizations.
    def add_entrance_rule(self, entrance_name: str, rule: StardewRule):
        entrance = self.get_entrance(entrance_name)
        MultiWorldRules.add_rule(entrance, self._add_context(rule))

    def add_location_rule(self, location_name: str, rule: StardewRule):
        location = self.get_location(location_name)
        MultiWorldRules.add_rule(location, self._add_context(rule))

    def has_mod(self, name: str) -> bool:
        return name in self.options.mods

    def get_option_value(self, option: str) -> Union[int, str, Set[str]]:
        return self.options.get_value_of(option).value
