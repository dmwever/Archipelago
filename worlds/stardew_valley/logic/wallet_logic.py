from .base_logic import BaseLogic, BaseLogicMixin
from ..stardew_rule import StardewRule
from ..strings.wallet_item_names import Wallet


class WalletLogicMixin(BaseLogicMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wallet = WalletLogic(*args, **kwargs)


class WalletLogic(BaseLogic):

    def can_speak_dwarf(self) -> StardewRule:
        return self.logic.received(Wallet.dwarvish_translation_guide)

    def has_rusty_key(self) -> StardewRule:
        return self.logic.received(Wallet.rusty_key)

    # These could be tested against gender if gender ever becomes a yaml option
    def has_mens_locker_key(self) -> StardewRule:
        return self.logic.received(Wallet.mens_locker_key)

    def has_womens_locker_key(self) -> StardewRule:
        return self.logic.received(Wallet.womens_locker_key)
    
    def has_river_road_1_key(self) -> StardewRule:
        return self.logic.received(Wallet.river_road_1_key)

    def has_river_road_2_key(self) -> StardewRule:
        return self.logic.received(Wallet.river_road_2_key)
    
    def has_willow_lane_1_key(self) -> StardewRule:
        return self.logic.received(Wallet.willow_lane_1_key)

    def has_willow_lane_2_key(self) -> StardewRule:
        return self.logic.received(Wallet.willow_lane_2_key)
    
    def has_mayors_key(self) -> StardewRule:
        return self.logic.received(Wallet.mayors_key)

    def has_blacksmith_key(self) -> StardewRule:
        return self.logic.received(Wallet.blacksmith_key)
    
    def has_carpenters_key(self) -> StardewRule:
        return self.logic.received(Wallet.carpenters_key)

    def has_willys_key(self) -> StardewRule:
        return self.logic.received(Wallet.willys_key)
    
    def has_hospital_key(self) -> StardewRule:
        return self.logic.received(Wallet.hospital_key)

    def has_jojamart_key(self) -> StardewRule:
        return self.logic.received(Wallet.jojamart_key)
    
    def has_marnies_key(self) -> StardewRule:
        return self.logic.received(Wallet.marnies_key)

    def has_pierres_key(self) -> StardewRule:
        return self.logic.received(Wallet.pierres_key)
    
    def has_saloon_key(self) -> StardewRule:
        return self.logic.received(Wallet.saloon_key)

    def has_adventurers_key(self) -> StardewRule:
        return self.logic.received(Wallet.adventurers_key)
