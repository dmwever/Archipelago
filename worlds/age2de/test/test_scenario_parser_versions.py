"""The install reads scenarios of different versions one after another in one process."""
import unittest

from ..campaign.ScenarioParser import restore_unsupported_properties


class TestAPropertyDisabledForAnOlderScenarioComesBack(unittest.TestCase):
    """The parser disables a property an older scenario lacks on the class itself - a 1.58
    scenario turns off Unit.capture_flag, and a 1.59 one written next can't write its units."""

    def capture_flag_link(self):
        from AoE2ScenarioParser.objects.data_objects.unit import Unit
        link = next(each for group in Unit._link_list for each in getattr(group, "group", [group])
                    if each.name == "capture_flag")
        return Unit, link

    def disable_as_the_parser_does(self, unit_cls, link) -> None:
        """What RetrieverObjectLink.overwrite_unsupported_properties does for a 1.58 scenario."""
        def _get(self_):
            raise AttributeError("capture_flag is supported since 1.59")

        def _set(self_, val):
            if val is not None:
                raise AttributeError("capture_flag is supported since 1.59")
        setattr(unit_cls, link.name, property(_get, _set))
        link.disabled = True

    def tearDown(self) -> None:
        restore_unsupported_properties()

    def test_the_next_scenario_reads_and_writes_it_again(self):
        unit_cls, link = self.capture_flag_link()
        self.disable_as_the_parser_does(unit_cls, link)
        restore_unsupported_properties()
        self.assertFalse(link.disabled)
        self.assertNotIsInstance(unit_cls.__dict__.get("capture_flag"), property)
        unit = unit_cls.__new__(unit_cls)
        unit.capture_flag = 3
        self.assertEqual(3, unit.capture_flag)

    def test_nothing_disabled_is_left_alone(self):
        unit_cls, link = self.capture_flag_link()
        restore_unsupported_properties()
        self.assertFalse(link.disabled)
        self.assertNotIn("capture_flag", unit_cls.__dict__)


if __name__ == "__main__":
    unittest.main()
