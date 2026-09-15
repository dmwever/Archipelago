import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from ...Options import Techsanity
from ...campaign import CampaignWriter, ScenarioParser
from ...campaign.CampaignReader import Campaign
from ...generation import Identity, SlotData
from ...locations.Ages import Age2AgeData
from ...locations.Campaigns import Age2CampaignData
from ...locations.Civilizations import Age2CivData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Techs import Age2TechData
from ...logic.goal_logic import CAMPAIGN_TO_SCENARIOS
from .FolderHandler import FolderHandler
from .install import TechData

logger = logging.getLogger("Client")

CAMPAIGN_SUBPATH = "resources/_common/campaign"
XS_SUBPATH = "resources/_common/xs"
SLOT_DATA_FILE = "SlotData.xs"
TECH_DATA_FILE = "TechData.xs"

class InstallError(Exception):
    pass

@dataclass
class IncludedCampaign:
    data: Age2CampaignData
    display_name: str
    file_name: str
    write_name: str

class InstallHandler(FolderHandler):
    _user_folder: str = ''
    _tag: str = ''
    _player_slot: int = -1

    def __init__(self):
        self._included_campaigns: list[IncludedCampaign] = []
        self._slot_data: dict = {}
        self._scenarios: list[Age2ScenarioData] = []
        self._civs: list[Age2CivData] = []
        self._techs: list[Age2TechData] = []
        self._parsed = 0
        self._to_parse = 0
        self.installing = False
        self.logger: Callable[[str], None] = logger.info
        super().__init__()

    def setup(self, campaigns: list[Age2CampaignData], slot: int, tag: str,
              slot_data: dict = None, location_ids: Iterable[int] = ()):
        self._included_campaigns = [
            IncludedCampaign(
                data=cpn,
                display_name=Identity.tagged(cpn.file_stem, tag),
                file_name=Identity.campaign_file_name(cpn.file_stem, ''),
                write_name=Identity.campaign_file_name(cpn.file_stem, tag),
            )
            for cpn in campaigns
        ]
        self._player_slot = slot
        self._tag = tag
        self._slot_data = dict(slot_data or {})
        self._scenarios = [scenario for campaign in campaigns
                           for scenario in CAMPAIGN_TO_SCENARIOS[campaign]]
        self._civs = list(dict.fromkeys(scenario.civ for scenario in self._scenarios))
        self._techs = [Age2TechData(id) for id in location_ids
                                if id in Age2TechData]

    def campaign_dir(self) -> Path:
        return Path(self._user_folder, CAMPAIGN_SUBPATH)

    def xs_dir(self) -> Path:
        return Path(self._user_folder, XS_SUBPATH)

    def slot_data_path(self) -> Path:
        return self.xs_dir() / SLOT_DATA_FILE

    def tech_data_path(self) -> Path:
        return self.xs_dir() / TECH_DATA_FILE

    def techsanity(self) -> dict[str, int]:
        return SlotData.techsanity(self._slot_data)

    def scenario_needs_age_up(self) -> bool:
        techsanity = self.techsanity()
        return (techsanity[SlotData.TS_MODE] != Techsanity.option_none
                and TechData.rebases(techsanity[SlotData.TS_EXISTING]))

    def grant_age(self) -> Age2AgeData:
        """The deepest age an installed scenario starts in, or None if none was rebased."""
        if not self.scenario_needs_age_up():
            return None
        ages = [scenario.vanilla_age for scenario in self._scenarios]
        return max(ages) if ages else None

    def source_path(self, campaign: IncludedCampaign) -> Path:
        return self.campaign_dir() / campaign.file_name

    def install_path(self, campaign: IncludedCampaign) -> Path:
        return self.campaign_dir() / campaign.write_name

    def install(self) -> list[Path]:
        if not self._user_folder:
            raise InstallError("No Age2 user folder is set.")

        missing = [campaign for campaign in self._included_campaigns
                   if not self.source_path(campaign).is_file()]
        if missing:
            raise InstallError(
                "Could not find " +
                ", ".join(campaign.file_name for campaign in missing) +
                f" in {self.campaign_dir()}. Install the Ageipelago files into your "
                "Age2 user folder first.")

        if not self.xs_dir().is_dir():
            raise InstallError(
                f"Could not find {self.xs_dir()}. Install the Ageipelago files into your "
                "Age2 user folder first.")

        self._parsed = 0
        self._to_parse = sum(1 for data in self._scenarios if self.steps_for(data))
        written = [self._install_campaign(campaign) for campaign in self._included_campaigns]
        written.append(self._write_slot_data())
        written.append(self._write_tech_data())
        return written

    def scenario_data(self, file_name: str) -> Age2ScenarioData:
        stem = Path(file_name).stem
        return next((data for data in self._scenarios if data.file_stem == stem), None)

    def steps_for(self, data: Age2ScenarioData) -> list[ScenarioParser.Step]:
        """The edits this seed needs in this scenario, in one pass over it."""
        steps = []
        if (self.scenario_needs_age_up() and data is not None
                and data.vanilla_age > Age2AgeData.DARK):
            steps.append(ScenarioParser.rebase_to_dark)
        return steps

    def _install_campaign(self, included: IncludedCampaign) -> Path:
        campaign = Campaign(str(self.source_path(included)))
        for scenario in campaign.scenarios:
            data = self.scenario_data(scenario.file_name)
            steps = self.steps_for(data)
            name = data.scenario_name if data else Path(scenario.file_name).stem
            scenario.body = ScenarioParser.apply(
                scenario.body, steps, name, (self._parsed, self._to_parse), self.logger)
            if steps:
                self._parsed += 1
        target = self.install_path(included)
        CampaignWriter.write(campaign, target, included.display_name)
        return target

    def _write_slot_data(self) -> Path:
        target = self.slot_data_path()
        target.write_text(
            SlotData.render(SlotData.slot_fields(self._player_slot, self._tag, self._slot_data)),
            encoding="utf-8")
        return target

    def _write_tech_data(self) -> Path:
        target = self.tech_data_path()
        if self.techsanity()[SlotData.TS_MODE] == Techsanity.option_none:
            target.write_text(TechData.render(), encoding="utf-8")
            return target
        table = TechData.rows(self._techs, self.grant_age(), self._civs)
        target.write_text(TechData.render(table, self._tag), encoding="utf-8")
        return target
