from dataclasses import dataclass
from pathlib import Path

from .FolderHandler import FolderHandler

from .install.MercenaryData import MercenaryData

from ...generation import Identity, SlotData
from ...items.Items import Age2ItemData
from ...campaign import CampaignWriter
from ...campaign.CampaignReader import Campaign
from ...locations.Campaigns import Age2CampaignData

CAMPAIGN_SUBPATH = "resources/_common/campaign"
XS_SUBPATH = "resources/_common/xs"
SLOT_DATA_FILE = "SlotData.xs"
MERCENARY_DATA_FILE = "MercenaryData.xs"


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
        self._mercenaries: list[Age2ItemData] = []
        super().__init__()

    def setup(self, campaigns: list[Age2CampaignData], mercenaries: list[Age2ItemData], slot: int,
              tag: str, player_name: str):
        # display_name and write_name must share a stem: the engine names the .xsdat it writes
        # after the campaign it is playing, and which of the two it reads is untested.
        self._included_campaigns = [
            IncludedCampaign(
                data=cpn,
                display_name=Identity.file_stem(cpn.file_stem, tag, player_name),
                file_name=Identity.source_campaign_file_name(cpn.file_stem),
                write_name=Identity.campaign_file_name(cpn.file_stem, tag, player_name),
            )
            for cpn in campaigns
        ]
        self._mercenaries = list(mercenaries)
        self._player_slot = slot
        self._tag = tag

    def campaign_dir(self) -> Path:
        return Path(self._user_folder, CAMPAIGN_SUBPATH)

    def xs_dir(self) -> Path:
        return Path(self._user_folder, XS_SUBPATH)

    def slot_data_path(self) -> Path:
        return self.xs_dir() / SLOT_DATA_FILE

    def mercenary_data_path(self) -> Path:
        return self.xs_dir() / MERCENARY_DATA_FILE

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

        written = [self._install_campaign(campaign) for campaign in self._included_campaigns]
        written.append(self._write_slot_data())
        written.append(self._write_mercenary_data())
        return written

    def _install_campaign(self, included: IncludedCampaign) -> Path:
        campaign = Campaign(str(self.source_path(included)))
        target = self.install_path(included)
        CampaignWriter.write(campaign, target, included.display_name)
        return target

    def _write_slot_data(self) -> Path:
        target = self.slot_data_path()
        target.write_text(
            SlotData.render(SlotData.fields(self._player_slot, self._tag)), encoding="utf-8")
        return target

    def _write_mercenary_data(self) -> Path:
        target = self.mercenary_data_path()
        target.write_text(MercenaryData(self._mercenaries).render(), encoding="utf-8")
        return target
