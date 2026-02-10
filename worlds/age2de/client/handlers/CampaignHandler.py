from dataclasses import dataclass, field
import os

from ...campaign import XsdatFile
from ...items.Items import Age2ItemData, SCENARIO_TO_ITEMS
from ...locations.Scenarios import Age2ScenarioData, CAMPAIGN_TO_SCENARIOS
from ...locations.Campaigns import Age2CampaignData

@dataclass
class ManagedScenarioItem:
    data: Age2ItemData
    scenario: Age2ScenarioData = None
    unlocked = False

@dataclass
class ManagedScenario:
    data: Age2ScenarioData = None
    campaign: Age2CampaignData = None
    items: list[Age2ItemData] = field(default_factory=list[Age2ItemData])
    unlocked: bool = False
    completed: bool = False

@dataclass
class ManagedCampaign:
    data: Age2CampaignData = None
    scenarios: list[Age2ScenarioData] = field(default_factory=list[Age2ScenarioData])
    unlocked: bool = False
    
class CampaignHandler:
    _campaigns: dict[Age2CampaignData, ManagedCampaign]
    _scenarios: dict[Age2ScenarioData, ManagedScenario]
    _scenario_items: dict[Age2ItemData, ManagedScenarioItem]
    
    active_scenario: ManagedScenario = None
    
    def __init__(self, data: list[Age2CampaignData]):
        for cpn_data in data:
            scenarios_as_data: list[Age2ScenarioData] = []
            for scn_data in CAMPAIGN_TO_SCENARIOS[cpn_data]:
                items_as_data: list[Age2ItemData] = []
                for item_data in SCENARIO_TO_ITEMS[scn_data]:
                    managed_item = ManagedScenarioItem(data=item_data, scenario=scn_data)
                    items_as_data.append[item_data]
                    self._scenario_items[item_data] = managed_item
                managed_scenario = ManagedScenario(data=scn_data, campaign=cpn_data, items=items_as_data)
                scenarios_as_data.append[scn_data]
                self._scenarios[scn_data] = managed_scenario
            managed_campaign = ManagedCampaign(data=cpn_data, scenarios=scenarios_as_data)
            self._campaigns[cpn_data] = managed_campaign

    def set_user_folder(self, user_folder: str):
        self._user_folder = user_folder
        
    def unlock_campaign(self, campaign: Age2CampaignData):
        if campaign not in self._campaigns:
            print("Campaign data not found in this AP World's Campaign Handler. Could not unlock campaign.")
            return
        first_scenario = self._campaigns[campaign].scenarios[0]
        if first_scenario is None:
            print("Campaign contains no scenarios. Could not unlock campaign.")
            return
        
        self._campaigns[campaign].unlocked = True
        self._scenarios[first_scenario].unlocked = True
    
    def unlock_scenario(self, scenario: Age2ScenarioData):
        pass
    
    def unlock_progressive_scenario(self, campaign: Age2CampaignData):
        if campaign not in self._campaigns:
            print("Campaign data not found in this AP World's Campaign Handler. Could not unlock progressive scenario.")
            return
        if self._campaigns[campaign].unlocked is False:
            print("Campaign is not unlocked. Could not unlock progressive scenario.")
            return
        
        for scn in self._campaigns[campaign].scenarios:
            if self._scenarios[scn].unlocked is False:
                self._scenarios[scn].unlocked = True # Activate first scenario that is not active
                return
        
        print("All scenarios in this campaign are already unlocked.")
    
    def find_active_scenario(self):
        for scenario in self._scenarios.values():
            if scenario.unlocked:
                try:
                    with open(self._user_folder + scenario.data.xsdat_read_name, "rb") as fp:
                        active = fp.peek(1)[:1]
                        if (active != b'\x00'):
                            self.active_scenario = scenario
                            return
                        else:
                            print("Not active")
                except:
                    pass
        self.active_scenario = None
    
    def has_active_scenario(self) -> bool:
        return self.active_scenario is not None
    
    
    def deactivate_scenario(self) -> bool:
        try:
            with open(self._user_folder + self.active_scenario.data.xsdat_read_name, "wb") as fp:
                XsdatFile.write_bool(fp, False)
        except Exception as ex:
            print(ex)
        self.active_scenario = None
    
    def sync_scenario_items(self, unlocked_items: list[Age2ItemData]) -> None:
        try:
            for item in unlocked_items:
                managed_item = self._scenario_items[item]
                if managed_item is None:
                    print(f"{item.name} is not in the list of scenario items for this AP World.")
                managed_item.unlocked = True
            
            for scenario in self._scenarios.values():
                if scenario.unlocked == True:
                    with open(self._user_folder + scenario.data.xsdat_write_name, "wb") as fp:
                        XsdatFile.write_int(fp, scenario.completed) # Change to completed
                        for item in scenario.items:
                            if self._scenario_items[item].unlocked == True:
                                XsdatFile.write_int(fp, item.id)
            
        except Exception as ex:
            print(ex)
            
    def try_flush_from_folder(self):
        for scn in self._scenarios:
            if os.path.exists(self._user_folder + scn.xsdat_write_name):
                os.remove(self._user_folder + scn.xsdat_write_name)
            if os.path.exists(self._user_folder + scn.xsdat_read_name):
                os.remove(self._user_folder + scn.xsdat_read_name)
    
    def __add_campaign_to_folder():
        pass
    
    def __add_scenario_to_age2campaign():
        pass
    
    def __update_age2campaign_json():
        pass