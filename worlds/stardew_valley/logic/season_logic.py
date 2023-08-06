from typing import Iterable

from .received_logic import ReceivedLogic
from .time_logic import TimeLogic
from .. import options
from ..stardew_rule import StardewRule, True_, And, Or
from ..strings.generic_names import Generic
from ..strings.season_names import Season


class SeasonLogic:
    player: int
    season_option: int
    received: ReceivedLogic
    time: TimeLogic

    def __init__(self, player: int, season_option: int, received_logic: ReceivedLogic, time: TimeLogic):
        self.player = player
        self.season_option = season_option
        self.received = received_logic
        self.time = time

    def has(self, season: str) -> StardewRule:
        if season == Generic.any:
            return True_()
        seasons_order = [Season.spring, Season.summer, Season.fall, Season.winter]
        if self.season_option == options.SeasonRandomization.option_progressive:
            return self.received(Season.progressive, seasons_order.index(season))
        if self.season_option == options.SeasonRandomization.option_disabled:
            if season == Season.spring:
                return True_()
            return self.time.has_lived_months(1)
        return self.received(season)

    def has_any(self, seasons: Iterable[str]):
        if not seasons:
            return True_()
        return Or([self.has(season) for season in seasons])

    def has_any_not_winter(self):
        return self.has_any([Season.spring, Season.summer, Season.fall])

    def has_all(self, seasons: Iterable[str]):
        if not seasons:
            return True_()
        return And([self.has(season) for season in seasons])

