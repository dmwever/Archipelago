"""A location the server already holds clears its scenario trigger on its own.

The bug: a scenario entered again, or a save reloaded, after its locations were checked asked the
player to redo every objective behind them. Trigger enable state is part of a save, so a trigger
that had fired comes back live. Every AP location trigger now carries an OR'd Script Call
condition asking whether the locations it checks are already checked on the server.

The scenarios and their XS live in the Ageipelago repo, so these tests read it through
`AGEIPELAGO_PATH` and skip without it.

Condition separators bind `AND` > `OR` > none: conditions with no separator between them are
AND'd, but that implicit AND binds loosest. `A B OR C D` is `A and (B or C) and D`, so an `OR`
appended to a trigger of several unseparated conditions would only stand in for the last one.
Before this change no AP trigger carried an `AND` separator, so a trigger's conditions with every
`AND` removed are the conditions it had.
"""
import itertools
import os
import pathlib
import re
import unittest
from functools import cache

AGEIPELAGO = os.environ.get("AGEIPELAGO_PATH")
COMMON = pathlib.Path(AGEIPELAGO or ".", "age 2 files", "resources", "_common")

from ..AoE2ScenarioParser.datasets.conditions import ConditionId
from ..AoE2ScenarioParser.datasets.effects import EffectId

SCRIPT_CALL_CONDITION = ConditionId.SCRIPT_CALL
OR = ConditionId.OR
AND = ConditionId.AND
SEPARATORS = (OR, AND)
SCRIPT_CALL_EFFECT = EffectId.SCRIPT_CALL
CHANGE_VARIABLE = EffectId.CHANGE_VARIABLE

WRAPPER = re.compile(r"\bvoid\s+(\w+)\s*\(\s*\)\s*\{(.*?)\n\}", re.S)
PREDICATE = re.compile(r"\bbool\s+(\w+)\s*\(\s*\)\s*\{(.*?)\n\}", re.S)
CHECK = re.compile(r"AP_Check_Location\((\d+)\)")
ASKS = re.compile(r"IsCheckedOnServer\((\d+)\)")
CALL = re.compile(r"([A-Za-z_]\w*)\s*\(\s*\)")

# Each of these adds to the variable its scenario's AP Victory waits on. Firing one because its
# location is already checked would hand the player that share of the victory.
FEEDS_VICTORY = {
    ("AP_Attila_2", "AP Beat the Romans"),
    ("AP_Attila_2", "AP Build TC"),
    ("AP_Attila_4", "AP Defeat Burgundy All"),
    ("AP_Attila_4", "AP Castle Burgundy All"),
    ("AP_Attila_4", "AP Defeat or Ally Burgundy Any"),
    ("AP_Attila_6", "AP Defeat the Italians"),
    ("AP_Attila_6", "AP Meet the Pope"),
}
WONDERS = {"AP Destroy Purple Wonder", "AP Destroy Green Wonder", "AP Destroy Red Wonder",
           "AP Destroy Orange Wonder", "AP Destroy Purple Wonder 2"}


def stems() -> list[str]:
    return sorted(path.stem for path in (COMMON / "scenario").glob("AP_*.aoe2scenario"))


@cache
def scenario(stem: str):
    from ..campaign.ScenarioParser import restore_unsupported_properties
    from ..AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
    restore_unsupported_properties()
    return AoE2DEScenario.from_file(str(COMMON / "scenario" / f"{stem}.aoe2scenario"))


@cache
def xs(stem: str) -> str:
    return (COMMON / "xs" / f"{stem}.xs").read_text()


@cache
def wrappers(stem: str) -> dict[str, tuple[list[int], bool]]:
    """Every function the scenario's triggers call to check a location: its ids, and whether it
    also wins the scenario."""
    found = {}
    for name, body in WRAPPER.findall(xs(stem)):
        ids = [int(each) for each in CHECK.findall(body)]
        if ids:
            found[name] = (ids, "GiveVictory" in body)
    return found


def location_function_body(returns: str, name: str, params: str = "") -> str | None:
    """The body of a function in ScenarioLocations.xs, or None if it is not defined there."""
    source = (COMMON / "xs" / "ScenarioLocations.xs").read_text()
    match = re.search(rf"\b{returns}\s+{name}\s*\(\s*{params}\s*\)\s*\{{(.*?)\n\}}", source, re.S)
    return match.group(1) if match else None


def displayed(trigger) -> list:
    return [trigger.conditions[index] for index in trigger.condition_order]


def location_calls(stem: str, trigger) -> list[str]:
    calls = [call for effect in trigger.effects if effect.effect_type == SCRIPT_CALL_EFFECT
             for call in CALL.findall(effect.message or "")]
    return [call for call in calls if call in wrappers(stem)]


def location_triggers():
    """(stem, trigger, location wrappers it calls) for every trigger that checks a location."""
    for stem in stems():
        for trigger in scenario(stem).trigger_manager.triggers:
            calls = location_calls(stem, trigger)
            if calls:
                yield stem, trigger, calls


def wins(stem: str, calls: list[str]) -> bool:
    return any(wrappers(stem)[call][1] for call in calls)


def excluded(stem: str, trigger, calls: list[str]) -> bool:
    return wins(stem, calls) or (stem, trigger.name) in FEEDS_VICTORY


def predicate_name(call: str) -> str:
    return f"{call}Checked"


def is_predicate(condition) -> bool:
    return (condition.condition_type == SCRIPT_CALL_CONDITION
            and bool(re.fullmatch(r"\s*\w+Checked\(\);\s*", condition.xs_function or "")))


def evaluate(tokens: list, truth: dict) -> bool:
    """Evaluate displayed conditions as the game does: `AND` > `OR` > no separator.

    `tokens` is the display order, each entry a separator id or a key into `truth`."""
    chunks, chunk = [], []
    for token in tokens:
        if chunk and token not in SEPARATORS and chunk[-1] not in SEPARATORS:
            chunks.append(chunk)
            chunk = []
        chunk.append(token)
    chunks.append(chunk)

    def chunk_value(each: list) -> bool:
        terms, term = [], []
        for token in each:
            if token == OR:
                terms.append(term)
                term = []
            elif token != AND:
                term.append(truth[token])
        terms.append(term)
        return any(all(term) for term in terms)

    return all(chunk_value(each) for each in chunks)


def tokens_of(trigger) -> list:
    return [condition.condition_type if condition.condition_type in SEPARATORS else index
            for index, condition in enumerate(displayed(trigger))]


@unittest.skipUnless(AGEIPELAGO, "AGEIPELAGO_PATH is not set")
class TestCheckedLocationTriggersClearThemselves(unittest.TestCase):
    def targets(self):
        return [(stem, trigger, calls) for stem, trigger, calls in location_triggers()
                if not excluded(stem, trigger, calls)]

    def test_every_location_trigger_asks_whether_its_locations_are_checked(self):
        """The trigger ends `OR` and then one predicate per location it checks, AND'd together, so
        a trigger checking several locations clears only once all of them are checked."""
        targets = self.targets()
        self.assertGreater(len(targets), 100)
        for stem, trigger, calls in targets:
            with self.subTest(scenario=stem, trigger=trigger.name):
                conditions = displayed(trigger)
                wanted = [predicate_name(call) for call in calls]
                tail = conditions[-(2 * len(wanted)):]
                self.assertEqual(OR, tail[0].condition_type)
                self.assertEqual([AND] * (len(wanted) - 1),
                                 [each.condition_type for each in tail[2::2]])
                self.assertEqual(wanted, [each.xs_function.strip().removesuffix("();")
                                          for each in tail[1::2]])
                self.assertTrue(all(is_predicate(each) for each in tail[1::2]))

    def test_the_original_conditions_are_joined_explicitly(self):
        """Every adjacent pair ahead of the appended `OR` has a separator between them, so the
        `OR` sits at the top level instead of standing in for the last condition."""
        for stem, trigger, calls in self.targets():
            with self.subTest(scenario=stem, trigger=trigger.name):
                head = tokens_of(trigger)[:-(2 * len(calls))]
                for left, right in itertools.pairwise(head):
                    self.assertFalse(left not in SEPARATORS and right not in SEPARATORS,
                                     f"{head} has two conditions with no separator")

    def test_a_trigger_fires_whenever_all_its_locations_are_checked(self):
        for stem, trigger, calls in self.targets():
            with self.subTest(scenario=stem, trigger=trigger.name):
                tokens = tokens_of(trigger)
                predicates = {index for index, each in enumerate(displayed(trigger))
                              if is_predicate(each)}
                real = [token for token in tokens
                        if token not in SEPARATORS and token not in predicates]
                for values in itertools.product((False, True), repeat=len(real)):
                    truth = dict(zip(real, values)) | dict.fromkeys(predicates, True)
                    self.assertTrue(evaluate(tokens, truth), values)

    def test_with_its_locations_unchecked_a_trigger_evaluates_as_it_did(self):
        """Its conditions with the predicates false agree with the conditions it had - the same
        list with no `AND` and no appended branch - for every combination, which is what holds
        the triggers that already carried an `OR` to their old grouping."""
        for stem, trigger, calls in self.targets():
            with self.subTest(scenario=stem, trigger=trigger.name):
                tokens = tokens_of(trigger)
                head = tokens[:-(2 * len(calls))]
                original = [token for token in head if token != AND]
                predicates = [token for token in tokens[len(head):] if token not in SEPARATORS]
                real = [token for token in head if token not in SEPARATORS]
                for values in itertools.product((False, True), repeat=len(real)):
                    truth = dict(zip(real, values)) | dict.fromkeys(predicates, False)
                    self.assertEqual(evaluate(original, truth), evaluate(tokens, truth), values)

    def test_triggers_that_already_carried_an_or_are_covered(self):
        carrying = sorted((stem, trigger.name) for stem, trigger, calls in self.targets()
                          if OR in tokens_of(trigger)[:-(2 * len(calls))])
        self.assertEqual([("AP_Attila_1", "AP Resolve Scout Any"),
                          ("AP_Joan_2", "AP Bring Joan to Orleans"),
                          ("AP_Joan_5", "AP Loyalists")], carrying)

    def test_the_disabled_wonder_triggers_ask_and_stay_disabled(self):
        """Attila 6's wonder triggers start disabled; a Constructs Wonder trigger turns each on,
        which is the earliest its objective exists. They carry the branch like any other."""
        wonders = {trigger.name: trigger for trigger in scenario("AP_Attila_6").trigger_manager.triggers
                   if trigger.name in WONDERS}
        self.assertEqual(WONDERS, set(wonders))
        for name, trigger in wonders.items():
            with self.subTest(trigger=name):
                self.assertFalse(trigger.enabled)
                self.assertTrue(is_predicate(displayed(trigger)[-1]))


@unittest.skipUnless(AGEIPELAGO, "AGEIPELAGO_PATH is not set")
class TestExcludedTriggersAreUntouched(unittest.TestCase):
    def excluded(self):
        return [(stem, trigger, calls) for stem, trigger, calls in location_triggers()
                if excluded(stem, trigger, calls)]

    def assert_untouched(self, trigger):
        types = [each.condition_type for each in trigger.conditions]
        self.assertNotIn(AND, types)
        self.assertFalse(any(is_predicate(each) for each in trigger.conditions))

    def test_no_victory_trigger_is_touched(self):
        victories = [(stem, trigger) for stem, trigger, calls in self.excluded() if wins(stem, calls)]
        self.assertEqual(18, len(victories))
        self.assertIn("AP_Genghis_6", {stem for stem, _ in victories})
        for stem, trigger in victories:
            with self.subTest(scenario=stem, trigger=trigger.name):
                self.assert_untouched(trigger)

    def test_triggers_feeding_the_victory_variable_are_untouched(self):
        feeding = {(stem, trigger.name) for stem, trigger, calls in self.excluded()
                   if not wins(stem, calls)}
        self.assertEqual(FEEDS_VICTORY, feeding)
        for stem, trigger, calls in self.excluded():
            if (stem, trigger.name) in FEEDS_VICTORY:
                with self.subTest(scenario=stem, trigger=trigger.name):
                    self.assert_untouched(trigger)
                    self.assertIn(CHANGE_VARIABLE, [each.effect_type for each in trigger.effects])

    def test_only_excluded_triggers_carry_effects_beside_the_location_call(self):
        """A trigger whose effects do more than call XS fires those too when the branch clears it,
        so each one is a decision rather than a default."""
        for stem, trigger, calls in location_triggers():
            others = {each.effect_type for each in trigger.effects} - {SCRIPT_CALL_EFFECT}
            if others:
                with self.subTest(scenario=stem, trigger=trigger.name):
                    self.assertTrue(excluded(stem, trigger, calls))


@unittest.skipUnless(AGEIPELAGO, "AGEIPELAGO_PATH is not set")
class TestThePredicates(unittest.TestCase):
    def test_each_condition_names_a_predicate_asking_for_its_locations(self):
        for stem, trigger, calls in location_triggers():
            if excluded(stem, trigger, calls):
                continue
            predicates = dict(PREDICATE.findall(xs(stem)))
            for call in calls:
                with self.subTest(scenario=stem, predicate=predicate_name(call)):
                    body = predicates.get(predicate_name(call))
                    self.assertIsNotNone(body)
                    self.assertEqual(wrappers(stem)[call][0],
                                     [int(each) for each in ASKS.findall(body)])

    def test_the_predicate_is_silent_and_false_for_an_unknown_id(self):
        """It runs every tick on every AP trigger, so it may never chat: it looks the location up
        with FindLocationById, which says nothing on a miss, not GetLocationById, which does."""
        body = location_function_body("bool", "IsCheckedOnServer", r"int\s+\w+\s*=\s*-1")
        self.assertIsNotNone(body)
        self.assertNotIn("xsChatData", body)
        self.assertNotIn("GetLocationById", body)
        self.assertIn("FindLocationById", body)
        self.assertRegex(body, r"==\s*cInvalidVector\)\s*\{?\s*return\s*\(\s*false\s*\)")

    def test_a_location_already_on_the_server_is_never_queued_again(self):
        """The branch reaches AP_Check_Location, which sets scenarioComplete; only a location that
        is scenarioComplete and not serverComplete is queued for the server."""
        body = location_function_body("int", "FilterCompletedNotSent")
        self.assertIsNotNone(body)
        self.assertRegex(body, r"if\s*\(\s*scenarioComplete\s*==\s*true\s*&&\s*serverComplete\s*==\s*false\s*\)")


if __name__ == "__main__":
    unittest.main()
