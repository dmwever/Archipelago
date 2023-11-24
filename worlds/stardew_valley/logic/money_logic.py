from typing import Union

from Utils import cache_self1
from .base_logic import BaseLogicMixin, BaseLogic
from .buff_logic import BuffLogicMixin
from .has_logic import HasLogicMixin
from .received_logic import ReceivedLogicMixin
from .region_logic import RegionLogicMixin
from .time_logic import TimeLogicMixin
from ..stardew_rule import StardewRule, True_, HasProgressionPercent, False_
from ..strings.currency_names import Currency
from ..strings.region_names import Region

qi_gem_rewards = ("100 Qi Gems", "50 Qi Gems", "40 Qi Gems", "40 Qi Gems", "40 Qi Gems", "35 Qi Gems", "25 Qi Gems",
                  "25 Qi Gems", "20 Qi Gems", "10 Qi Gems", "15 Qi Gems", "15 Qi Gems", "15 Qi Gems")


class MoneyLogicMixin(BaseLogicMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.money = MoneyLogic(*args, **kwargs)


class MoneyLogic(BaseLogic[Union[RegionLogicMixin, MoneyLogicMixin, TimeLogicMixin, RegionLogicMixin, ReceivedLogicMixin, HasLogicMixin, BuffLogicMixin]]):

    @cache_self1
    def can_have_earned_total(self, amount: int) -> StardewRule:
        if amount < 2000:
            return True_()
        shipping_bin_rule = self.logic.region.can_reach(Region.shipping)
        if amount < 10000:
            return shipping_bin_rule

        percent_progression_items_needed = min(100, amount // 10000)
        return shipping_bin_rule & HasProgressionPercent(self.player, percent_progression_items_needed)

    @cache_self1
    def can_spend(self, amount: int) -> StardewRule:
        if self.options.starting_money == -1:
            return True_()
        return self.logic.money.can_have_earned_total(amount * 5)

    # Should be cached
    def can_spend_at(self, region: str, amount: int) -> StardewRule:
        return self.logic.region.can_reach(region) & self.logic.money.can_spend(amount)

    # Should be cached
    def can_trade(self, currency: str, amount: int) -> StardewRule:
        if amount == 0:
            return True_()
        if currency == Currency.money:
            return self.can_spend(amount)
        if currency == Currency.star_token:
            return self.logic.region.can_reach(Region.fair)
        if currency == Currency.qi_coin:
            return self.logic.region.can_reach(Region.casino) & self.logic.buff.has_max_luck()
        if currency == Currency.qi_gem:
            number_rewards = min(13, max(1, (amount // 10)))
            return self.logic.received(qi_gem_rewards, number_rewards)
        if currency == Currency.golden_walnut:
            return self.can_spend_walnut(amount)

        return self.logic.has(currency) & self.logic.time.has_lived_months(amount)

    # Should be cached
    def can_trade_at(self, region: str, currency: str, amount: int) -> StardewRule:
        if amount == 0:
            return True_()
        if currency == Currency.money:
            return self.logic.money.can_spend_at(region, amount)

        return self.logic.region.can_reach(region) & self.can_trade(currency, amount)

    def can_spend_walnut(self, amount: int) -> StardewRule:
        return False_()
