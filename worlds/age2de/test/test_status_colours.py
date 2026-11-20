import itertools
import types
import unittest
from collections.abc import Callable
from unittest import mock

from ..client.ApClient import Age2CommandProcessor, Age2Context
from ..client.DataStorage import DataStorage
from ..locations.Campaigns import Age2CampaignData

SCENARIO_COLOURS = {
    "Active": "green",
    "Available": "cyan",
    "Unlocked": "white",
    "Completed": "slateblue",
    "Campaign Locked": "orange",
    "Missing": "red",
}

MERCENARY_COLOURS = {
    "In-Pavilion": "green",
    "Unlocked": "cyan",
    "Used": "slateblue",
    "Missing": "red",
}

MERCENARY_GROUP_ORDER = ["Used", "Missing", "Unlocked", "In-Pavilion"]

class FakeUi:
    def __init__(self) -> None:
        self.printed: list[list[dict]] = []

    def print_json(self, parts: list[dict]) -> None:
        self.printed.append(parts)

class StatusCommandHarness(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = DataStorage(list(Age2CampaignData))
        self.scenario_statuses = dict(zip(
            self.storage.scenarios,
            itertools.cycle(SCENARIO_COLOURS),
        ))
        self.mercenary_statuses = dict(zip(
            self.storage.mercenaries,
            itertools.cycle(MERCENARY_COLOURS),
        ))
        self.message_handler = mock.Mock()
        self.ctx = Age2Context.__new__(Age2Context)
        self.ctx.ui = None
        self.ctx.data_storage = self.storage
        self.ctx.game_ctx = types.SimpleNamespace(
            campaign_handler=types.SimpleNamespace(status=self.scenario_statuses.__getitem__),
            mercenary_handler=types.SimpleNamespace(
                status=self.mercenary_statuses.__getitem__,
                seated=list,
                queued=list,
            ),
            message_handler=self.message_handler,
        )
        self.processor = Age2CommandProcessor(self.ctx)

    def plain_scenario_lines(self) -> list[str]:
        return [
            f"{self.scenario_statuses[scenario]:<16}"
            f"{scenario.campaign.campaign_name}: {scenario.scenario_name}"
            for scenario in self.storage.scenarios
        ]

    def mercenaries_in_display_order(self) -> list:
        return sorted(
            self.storage.mercenaries,
            key=lambda mercenary: MERCENARY_GROUP_ORDER.index(self.mercenary_statuses[mercenary]),
        )

    def plain_mercenary_lines(self) -> list[str]:
        return [
            f"{self.mercenary_statuses[mercenary]:<12}{mercenary.item_name}"
            for mercenary in self.mercenaries_in_display_order()
        ]

    def run_with_ui(self, command: Callable[[], None]) -> list[list[dict]]:
        ui = FakeUi()
        self.ctx.ui = ui
        with self.assertNoLogs("Client", "INFO"):
            command()
        return ui.printed

    def run_without_ui(self, command: Callable[[], None]) -> list[str]:
        self.ctx.ui = None
        with self.assertLogs("Client", "INFO") as logs:
            command()
        return [record.getMessage() for record in logs.records]

class TestStatusColours(StatusCommandHarness):
    def test_every_scenario_status_is_coloured(self) -> None:
        self.assertEqual(set(SCENARIO_COLOURS), set(self.scenario_statuses.values()))
        printed = self.run_with_ui(self.processor._cmd_scenarios)
        self.assertEqual(len(self.storage.scenarios), len(printed))
        for scenario, parts in zip(self.storage.scenarios, printed):
            status = self.scenario_statuses[scenario]
            with self.subTest(scenario=str(scenario), status=status):
                self.assertEqual(
                    {"type": "color", "color": SCENARIO_COLOURS[status], "text": status},
                    parts[0],
                )
                self.assertTrue(all(part["type"] == "text" for part in parts[1:]))

    def test_every_mercenary_status_is_coloured(self) -> None:
        self.assertEqual(set(MERCENARY_COLOURS), set(self.mercenary_statuses.values()))
        printed = self.run_with_ui(self.processor._cmd_mercenaries)
        self.assertEqual(len(self.storage.mercenaries), len(printed))
        for mercenary, parts in zip(self.mercenaries_in_display_order(), printed):
            status = self.mercenary_statuses[mercenary]
            with self.subTest(mercenary=str(mercenary), status=status):
                self.assertEqual(
                    {"type": "color", "color": MERCENARY_COLOURS[status], "text": status},
                    parts[0],
                )
                self.assertTrue(all(part["type"] == "text" for part in parts[1:]))

    def test_coloured_scenario_lines_keep_their_text_and_padding(self) -> None:
        printed = self.run_with_ui(self.processor._cmd_scenarios)
        joined = ["".join(part["text"] for part in parts) for parts in printed]
        self.assertEqual(self.plain_scenario_lines(), joined)

    def test_coloured_mercenary_lines_keep_their_text_and_padding(self) -> None:
        printed = self.run_with_ui(self.processor._cmd_mercenaries)
        joined = ["".join(part["text"] for part in parts) for parts in printed]
        self.assertEqual(self.plain_mercenary_lines(), joined)

class TestStatusTextWithoutUi(StatusCommandHarness):
    def test_scenario_lines_are_plain_text(self) -> None:
        self.assertEqual(
            self.plain_scenario_lines(),
            self.run_without_ui(self.processor._cmd_scenarios),
        )

    def test_mercenary_lines_are_plain_text(self) -> None:
        self.assertEqual(
            self.plain_mercenary_lines(),
            self.run_without_ui(self.processor._cmd_mercenaries),
        )

class TestStatusLinesStayOutOfGameChat(StatusCommandHarness):
    def test_with_ui_nothing_reaches_game_chat(self) -> None:
        self.ctx.ui = FakeUi()
        with mock.patch("CommonClient.CommonContext.on_print_json"):
            self.processor._cmd_scenarios()
            self.processor._cmd_mercenaries()
        self.message_handler.add_message.assert_not_called()

    def test_without_ui_nothing_reaches_game_chat(self) -> None:
        self.ctx.ui = None
        with mock.patch("CommonClient.CommonContext.on_print_json"):
            self.processor._cmd_scenarios()
            self.processor._cmd_mercenaries()
        self.message_handler.add_message.assert_not_called()

if __name__ == "__main__":
    unittest.main()
