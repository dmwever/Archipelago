from functools import cached_property

from Utils import cache_self1
from .cached_logic import CachedLogic, CachedRules
from .received_logic import ReceivedLogic
from ..stardew_rule import StardewRule, CountPercent, True_
from ..strings.ap_names.event_names import Event

MAX_MONTHS = 12
MONTH_COEFFICIENT = 100 // MAX_MONTHS


class TimeLogic(CachedLogic):
    received: ReceivedLogic

    def __init__(self, player: int, cached_rules: CachedRules, received_logic: ReceivedLogic):
        super().__init__(player, cached_rules)
        self.received = received_logic

    @cache_self1
    def has_lived_months(self, number: int) -> StardewRule:
        if number <= 0:
            return True_()
        number = min(number, MAX_MONTHS)
        return CountPercent(self.player, number * MONTH_COEFFICIENT)

    @cached_property
    def has_lived_max_months(self) -> StardewRule:
        return self.has_lived_months(MAX_MONTHS)

    @cached_property
    def has_year_two(self) -> StardewRule:
        return self.has_lived_months(4)

    @cached_property
    def has_year_three(self) -> StardewRule:
        return self.has_lived_months(8)
