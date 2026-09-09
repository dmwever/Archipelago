from collections import Counter
from dataclasses import dataclass, field
import logging
import os

from .FolderHandler import FolderHandler

from ...campaign import XsdatFile
from ...items.Items import CATEGORY_TO_ITEMS, Age2ItemData, SCENARIO_TO_ITEMS, Campaign, Mercenary, ProgressiveScenario, ScenarioItem
from ...locations.Scenarios import Age2ScenarioData, CAMPAIGN_TO_SCENARIOS, scenario_from_id
from ...locations.Campaigns import Age2CampaignData

logger = logging.getLogger("Client")

@dataclass
class ManagedScenarioItem:
    data: Age2ItemData
    scenario: Age2ScenarioData = None
    unlocked: bool = False

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
    must_beat: bool = False
    
class ActiveFile:
    current_scenario: ManagedScenario
    read_file_name: str = ''
    
    def __init__(self, scn: ManagedScenario, read_file_name: str):
        self.current_scenario = scn
        self.read_file_name = read_file_name
    
class CampaignHandler(FolderHandler):
    _campaigns: dict[Age2CampaignData, ManagedCampaign]
    scenarios: dict[Age2ScenarioData, ManagedScenario]
    _scenario_items: dict[Age2ItemData, ManagedScenarioItem]
    
    active_file: ActiveFile

    def __init__(self, data: list[Age2CampaignData]):
        self._campaigns = {}
        self.scenarios = {}
        self._scenario_items = {}
        self.active_file = None
        self._reported_locked: set[Age2ScenarioData] = set()
        for cpn_data in data:
            scenarios_as_data: list[Age2ScenarioData] = []
            for scn_data in CAMPAIGN_TO_SCENARIOS[cpn_data]:
                items_as_data: list[Age2ItemData] = []
                for item_data in SCENARIO_TO_ITEMS[scn_data]:
                    managed_item = ManagedScenarioItem(data=item_data, scenario=scn_data)
                    items_as_data.append(item_data)
                    self._scenario_items[item_data] = managed_item
                managed_scenario = ManagedScenario(data=scn_data, campaign=cpn_data, items=items_as_data)
                scenarios_as_data.append(scn_data)
                self.scenarios[scn_data] = managed_scenario
            managed_campaign = ManagedCampaign(data=cpn_data, scenarios=scenarios_as_data)
            self._campaigns[cpn_data] = managed_campaign
        super().__init__()
    
    def setup_victory_requirements(self, args: dict):
        for data in self._campaigns.keys():
            if data.campaign_name + "_unlocked" in args.keys():
                self._campaigns[data].must_beat = True
    
    def check_victory(self) -> bool:
        for campaign in self._campaigns.values():
            if (campaign.must_beat == False):
                continue
            for scenario in campaign.scenarios:
                if self.scenarios[scenario].completed == False:
                    return False
        return True
    
    def sync_unlocked(self, unlocked_items: list[Age2ItemData]) -> None:
        counts = Counter(unlocked_items)
        for campaign, managed_campaign in self._campaigns.items():
            managed_campaign.unlocked = any(
                counts[item] for item in CATEGORY_TO_ITEMS[Campaign]
                if item.type.vanilla_campaign == campaign
            )
            available = 0
            if managed_campaign.unlocked:
                progressives = sum(
                    counts[item] for item in CATEGORY_TO_ITEMS[ProgressiveScenario]
                    if item.type.vanilla_campaign == campaign
                )
                available = min(1 + progressives, len(managed_campaign.scenarios))
            for index, scn in enumerate(managed_campaign.scenarios):
                self.scenarios[scn].unlocked = index < available

        self._sync_scenario_items(unlocked_items)

    def _note_locked_scenario(self, scenario: ManagedScenario) -> None:
        if scenario.data in self._reported_locked:
            return
        self._reported_locked.add(scenario.data)
        logger.info(
            "%s is not unlocked in your Archipelago world yet, so its items cannot be delivered.",
            scenario.data.scenario_name,
        )

    def find_active_campaign(self) -> bool:
        for campaign in self._campaigns.values():
            if campaign.unlocked:
                try:
                    with open(self._user_folder + campaign.data.xsdat_read_name, "rb") as fp:
                        active = fp.peek(1)[:1]
                        if (active == b'\x01'):
                            XsdatFile.skip_int(fp, 18)
                            scenario_id = XsdatFile.read_int(fp)
                            scenario = self.scenarios[scenario_from_id[scenario_id]]
                            if not scenario.unlocked:
                                self._note_locked_scenario(scenario)
                            else:
                                self.active_file = ActiveFile(scn=scenario, read_file_name=campaign.data.xsdat_read_name)
                                return True
                        else:
                            print("Not active")
                except Exception as ex:
                    print(ex)
        self.active_file = None
        return False
    
    def find_active_scenario(self):
        for scenario in self.scenarios.values():
            if scenario.unlocked:
                try:
                    with open(self._user_folder + scenario.data.xsdat_read_name, "rb") as fp:
                        active = fp.peek(1)[:1]
                        if (active == b'\x01'):
                            self.active_file = ActiveFile(scn=scenario, read_file_name=scenario.data.xsdat_read_name)
                            return
                        else:
                            print("Not active")
                except Exception as ex:
                    print(ex)
        self.active_file = None
    
    def has_active_scenario(self) -> bool:
        return self.active_file is not None
    
    def is_active_scenario_complete(self) -> bool:
        return self.active_file.current_scenario.completed
    
    def complete_active_scenario(self) -> None:
        self.active_file.current_scenario.completed = True
    
    def deactivate_scenario(self) -> bool:
        try:
            with open(self._user_folder + self.active_file.read_file_name, "wb") as fp:
                XsdatFile.write_bool(fp, False)
        except Exception as ex:
            print(ex)
        self.active_file = None
    
    def _sync_scenario_items(self, unlocked_items: list[Age2ItemData]) -> None:
        items = [*CATEGORY_TO_ITEMS[ScenarioItem], *CATEGORY_TO_ITEMS[Mercenary]]
        for item in set(unlocked_items).intersection(items):
            managed_item = self._scenario_items.get(item)
            if managed_item is not None:
                managed_item.unlocked = True

        for scenario in self.scenarios.values():
            if scenario.unlocked == False:
                continue
            try:
                with open(self._user_folder + scenario.data.xsdat_write_name, "wb") as fp:
                    XsdatFile.write_int(fp, scenario.completed)
                    for item in scenario.items:
                        managed_item = self._scenario_items.get(item)
                        if managed_item is not None and managed_item.unlocked == True:
                            XsdatFile.write_int(fp, item.id)
            except Exception:
                logger.exception("Could not write scenario items for %s.", scenario.data.scenario_name)

    def try_flush_from_folder(self):
        for scn in self.scenarios:
            if os.path.exists(self._user_folder + scn.xsdat_write_name):
                os.remove(self._user_folder + scn.xsdat_write_name)
            if os.path.exists(self._user_folder + scn.xsdat_read_name):
                os.remove(self._user_folder + scn.xsdat_read_name)
        for cpn in self._campaigns:
            if os.path.exists(self._user_folder + cpn.xsdat_read_name):
                os.remove(self._user_folder + cpn.xsdat_read_name)
    
    def __add_campaign_to_folder():
        pass
    
    def __add_scenario_to_age2campaign():
        pass
    
    def __update_age2campaign_json():
        pass