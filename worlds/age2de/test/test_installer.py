import tempfile
import unittest
from pathlib import Path

from .test_campaign_bundle import SEED, build_fixture
from ..campaign.CampaignReader import Campaign
from ..client.handlers.CampaignHandler import CampaignHandler
from ..client.handlers.InstallHandler import InstallError, InstallHandler
from ..generation import Identity, SlotData
from ..locations.Campaigns import Age2CampaignData

SCENARIO_SUBPATH = "resources/_common/scenario"
PLAYER = "Dave"


def fake_user_folder(root: Path, campaigns=tuple(Age2CampaignData)) -> Path:
    layout = InstallHandler()
    layout.set_user_folder(str(root))
    layout.campaign_dir().mkdir(parents=True)
    layout.xs_dir().mkdir(parents=True)
    (root / SCENARIO_SUBPATH).mkdir(parents=True)

    for campaign in campaigns:
        bundle = build_fixture(Identity.source_campaign_stem(campaign.file_stem), [
            (f"{campaign.file_stem}_{index}.aoe2scenario", bytes([index]) * (64 + index))
            for index in range(1, 4)
        ])
        (layout.campaign_dir()
         / Identity.source_campaign_file_name(campaign.file_stem)).write_bytes(bundle)
        (root / SCENARIO_SUBPATH / f"{campaign.file_stem}_1.aoe2scenario").write_bytes(b"authoring")

    layout.slot_data_path().write_text(SlotData.render(), encoding="utf-8")
    return root


class InstallerTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fake_user_folder(Path(self._tmp.name))
        self.handler = InstallHandler()
        self.handler.set_user_folder(str(self.root))
        self.tag = Identity.seed_tag(SEED, 3)

    def install(self, campaigns, slot=3, tag=None, player_name=PLAYER, mercenaries=()):
        self.handler.setup(campaigns, list(mercenaries), slot,
                           self.tag if tag is None else tag, player_name)
        return self.handler.install()

    def installed_name(self, stem, tag=None, player_name=PLAYER):
        return Identity.campaign_file_name(stem, self.tag if tag is None else tag, player_name)

    def campaign_dir(self) -> Path:
        return self.handler.campaign_dir()

    def mercenary_data(self) -> Path:
        return self.root / "resources/_common/xs/MercenaryData.xs"

    def slot_data(self) -> Path:
        return self.handler.slot_data_path()

    def bundles_present(self):
        return sorted(p.name for p in self.campaign_dir().iterdir())


class TestInstall(InstallerTestBase):
    def test_writes_a_tagged_bundle_and_slot_data(self):
        written = self.install([Age2CampaignData.ATTILA])

        self.assertIn(self.installed_name("AP Attila the Hun"), self.bundles_present())
        self.assertEqual(written[0], self.campaign_dir()
                         / self.installed_name("AP Attila the Hun"))
        self.assertTrue(written[0].is_file())
        self.assertIn(self.slot_data(), written)
        self.assertEqual(
            self.slot_data().read_text(encoding="utf-8").replace("\r\n", "\n"),
            SlotData.render(SlotData.fields(3, self.tag)))

    def test_only_the_enabled_campaigns_are_installed(self):
        self.install([Age2CampaignData.JOAN])
        present = self.bundles_present()
        self.assertIn(self.installed_name("AP Joan of Arc"), present)
        self.assertNotIn(self.installed_name("AP Attila the Hun"), present)

    def test_source_bundles_are_left_alone(self):
        before = {
            campaign.file_stem: (self.campaign_dir()
                                 / Identity.source_campaign_file_name(
                                     campaign.file_stem)).read_bytes()
            for campaign in Age2CampaignData
        }
        self.install(list(Age2CampaignData))
        for campaign in Age2CampaignData:
            path = self.campaign_dir() / Identity.source_campaign_file_name(campaign.file_stem)
            self.assertEqual(path.read_bytes(), before[campaign.file_stem])

    def test_the_scenario_folder_is_untouched(self):
        before = {p.name: p.read_bytes() for p in (self.root / SCENARIO_SUBPATH).iterdir()}
        self.install(list(Age2CampaignData))
        after = {p.name: p.read_bytes() for p in (self.root / SCENARIO_SUBPATH).iterdir()}
        self.assertEqual(after, before)

    def test_installing_twice_is_identical(self):
        self.install([Age2CampaignData.ATTILA])
        tagged = self.campaign_dir() / self.installed_name("AP Attila the Hun")
        first = tagged.read_bytes()
        first_slot_data = self.slot_data().read_bytes()

        self.install([Age2CampaignData.ATTILA])
        self.assertEqual(tagged.read_bytes(), first)
        self.assertEqual(self.slot_data().read_bytes(), first_slot_data)

    def test_another_slot_writes_different_files(self):
        other = Identity.seed_tag(SEED, 5)
        self.install([Age2CampaignData.ATTILA])
        self.install([Age2CampaignData.ATTILA], slot=5, tag=other)

        present = self.bundles_present()
        self.assertIn(self.installed_name("AP Attila the Hun"), present)
        self.assertIn(self.installed_name("AP Attila the Hun", tag=other), present)
        self.assertIn("AP_SLOT_ID = 5", self.slot_data().read_text(encoding="utf-8"))

    def test_the_tagged_bundle_carries_the_tagged_display_name(self):
        self.install([Age2CampaignData.ATTILA])
        path = self.campaign_dir() / self.installed_name("AP Attila the Hun")
        campaign = Campaign(str(path))
        self.assertEqual(campaign.header.name, path.name[:-len(".aoe2campaign")])

    def test_the_scenario_entries_are_not_tagged(self):
        source = Campaign(str(self.campaign_dir() / "AP Attila the Hun Template.aoe2campaign"))
        self.install([Age2CampaignData.ATTILA])
        installed = Campaign(str(
            self.campaign_dir() / self.installed_name("AP Attila the Hun")))
        self.assertEqual([scn.file_name for scn in installed.scenarios],
                         [scn.file_name for scn in source.scenarios])
        self.assertEqual([scn.name for scn in installed.scenarios],
                         [scn.name for scn in source.scenarios])
        for scn in installed.scenarios:
            self.assertNotIn(self.tag, scn.file_name)

    def test_the_client_looks_for_what_was_installed(self):
        self.install([Age2CampaignData.ATTILA])
        handler = CampaignHandler(list(Age2CampaignData))
        handler.set_tag(self.tag)
        handler.set_player_name(PLAYER)
        installed = self.campaign_dir() / self.installed_name("AP Attila the Hun")
        self.assertEqual(handler.campaign_read_name(Age2CampaignData.ATTILA),
                         installed.name.replace(".aoe2campaign", ".xsdat"))


class TestPlayerNameInTheFileName(InstallerTestBase):
    def test_the_player_name_sits_before_the_tag(self):
        self.install([Age2CampaignData.ATTILA])
        self.assertIn(f"AP Attila the Hun_{PLAYER}_{self.tag}.aoe2campaign",
                      self.bundles_present())

    def test_the_tag_is_still_recoverable(self):
        self.install([Age2CampaignData.ATTILA])
        installed = self.installed_name("AP Attila the Hun")
        self.assertEqual(Identity.tag_of(installed.replace(".aoe2campaign", ".xsdat")), self.tag)

    def test_forbidden_characters_are_stripped_from_the_file_name(self):
        self.install([Age2CampaignData.ATTILA], player_name=Identity.sanitize_player('Da:ve|B'))
        self.assertIn(f"AP Attila the Hun_DaveB_{self.tag}.aoe2campaign", self.bundles_present())

    def test_the_display_name_matches_the_file_name(self):
        self.install([Age2CampaignData.ATTILA])
        path = self.campaign_dir() / self.installed_name("AP Attila the Hun")
        self.assertEqual(Campaign(str(path)).header.name, path.stem)

    def test_two_players_on_one_machine_do_not_collide(self):
        self.install([Age2CampaignData.ATTILA], player_name="Dave")
        self.install([Age2CampaignData.ATTILA], player_name="Erin")
        present = self.bundles_present()
        self.assertIn(f"AP Attila the Hun_Dave_{self.tag}.aoe2campaign", present)
        self.assertIn(f"AP Attila the Hun_Erin_{self.tag}.aoe2campaign", present)


class TestInstallRefusals(InstallerTestBase):
    def test_missing_source_bundle_is_reported(self):
        (self.campaign_dir() / "AP Attila the Hun Template.aoe2campaign").unlink()
        with self.assertRaises(InstallError) as caught:
            self.install([Age2CampaignData.ATTILA])
        self.assertIn("AP Attila the Hun Template.aoe2campaign", str(caught.exception))

    def test_missing_xs_folder_is_reported(self):
        for path in self.handler.xs_dir().iterdir():
            path.unlink()
        self.handler.xs_dir().rmdir()
        with self.assertRaises(InstallError):
            self.install([Age2CampaignData.ATTILA])

    def test_no_user_folder_is_reported(self):
        handler = InstallHandler()
        handler.setup([Age2CampaignData.ATTILA], [], 3, self.tag, PLAYER)
        with self.assertRaises(InstallError):
            handler.install()


class TestIncludedCampaigns(unittest.TestCase):
    def test_derived_from_the_unlocked_keys(self):
        handler = CampaignHandler(list(Age2CampaignData))
        self.assertEqual(handler.included_campaigns(), [])

        handler.setup_victory_requirements({"Joan of Arc_unlocked": False})
        self.assertEqual(handler.included_campaigns(), [Age2CampaignData.JOAN])

    def test_a_key_that_starts_locked_is_still_included(self):
        handler = CampaignHandler(list(Age2CampaignData))
        handler.setup_victory_requirements({
            "Joan of Arc_unlocked": True, "Attila the Hun_unlocked": False})
        self.assertEqual(set(handler.included_campaigns()), set(Age2CampaignData))
