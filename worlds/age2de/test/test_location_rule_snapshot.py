"""A temporary guard for moving the defeat rules into per-scenario logic (ADR 0001).

The move must not change what any location asks for, so every location's resolved rule was
fingerprinted on v0.3.0 and a freshly built world is compared against those fingerprints. The
comparison reads through names: Named and ScenarioQuestion wrappers are looked through, so "can
beat Red" becoming "can defeat Red" passes, and so does wrapping a rule in a new name or a new
cached question. And and Or are compared as flattened sets of operands, since naming a rule or
lifting it out of a name can change how they nest without changing what they ask.

Only Named and ScenarioQuestion are looked through: if defeats(player) returns any other wrapper,
teach Fingerprints to look through it too, or every defeat location fails here. Entrance rules
are not covered, only location rules; the move is not meant to touch them.

Delete this file and its snapshot once Attila, Joan and Genghis have all moved: the counter changes
that follow alter resolved rules on purpose.

Capturing the snapshot is a one-off step, run from the repository root on the commit to compare
against, never by the test suite:

    python -m worlds.age2de.test.test_location_rule_snapshot
"""
import dataclasses
import enum
import hashlib
import json
from pathlib import Path

from BaseClasses import Location
from rule_builder.rules import And, Or, Rule

from . import bases
from ..locations.Campaigns import Age2CampaignData
from ..logic.custom_logic.Named import Named
from ..logic.custom_logic.ScenarioQuestions import ScenarioQuestion

SNAPSHOT = Path(__file__).parent / "location_rule_snapshot.json"

CONNECTED_CAMPAIGNS = [
    Age2CampaignData.ATTILA.campaign_name,
    Age2CampaignData.JOAN.campaign_name,
    Age2CampaignData.GENGHIS.campaign_name,
]

NO_RULE = "no rule"
"""A location left on the default rule, reachable whenever its region is."""

class Fingerprints:
    """Label-blind fingerprints of resolved rules, shared subtrees hashed once per world."""

    IGNORED_FIELDS = {"player", "caching_enabled"}

    def __init__(self):
        self.operands: dict[int, frozenset[str]] = {}
        """And and Or, by id: the flattened set of operand fingerprints."""
        self.fingerprints: dict[int, str] = {}

    def of_location(self, location: Location) -> str:
        rule = location.access_rule
        # Read through the class, the staticmethod hands back the same function an instance does.
        if rule is Location.access_rule:
            return NO_RULE
        if not isinstance(rule, Rule.Resolved):
            raise TypeError(f"{location.name} has a {type(rule).__name__} rule, which cannot be "
                            f"fingerprinted")
        return self.of(rule)

    def of(self, rule: Rule.Resolved) -> str:
        if id(rule) in self.fingerprints:
            return self.fingerprints[id(rule)]
        if isinstance(rule, Named.Resolved):
            fingerprint = self.of(rule.child)
        elif isinstance(rule, ScenarioQuestion.Resolved):
            fingerprint = self.of(rule.answer)
        elif isinstance(rule, (And.Resolved, Or.Resolved)):
            operands = self.operands_of(rule)
            if len(operands) == 1:
                [fingerprint] = operands
            else:
                fingerprint = self.hashed(rule.rule_name, *sorted(operands))
        else:
            fingerprint = self.hashed(
                rule.rule_name,
                *(
                    f"{field.name}={self.of_value(getattr(rule, field.name))}"
                    for field in dataclasses.fields(rule)
                    if field.name not in self.IGNORED_FIELDS
                ),
            )
        self.fingerprints[id(rule)] = fingerprint
        return fingerprint

    def operands_of(self, rule: And.Resolved | Or.Resolved) -> frozenset[str]:
        """An And inside an And is the same question as its operands asked alongside the rest."""
        if id(rule) in self.operands:
            return self.operands[id(rule)]
        operands = set()
        for child in rule.children:
            child = self.unwrapped(child)
            if type(child) is type(rule):
                operands |= self.operands_of(child)
            else:
                operands.add(self.of(child))
        self.operands[id(rule)] = frozenset(operands)
        return self.operands[id(rule)]

    def unwrapped(self, rule: Rule.Resolved) -> Rule.Resolved:
        while True:
            if isinstance(rule, Named.Resolved):
                rule = rule.child
            elif isinstance(rule, ScenarioQuestion.Resolved):
                rule = rule.answer
            else:
                return rule

    def of_value(self, value) -> str:
        if isinstance(value, Rule.Resolved):
            return self.of(value)
        if isinstance(value, (tuple, list)):
            return "(" + ",".join(self.of_value(item) for item in value) + ")"
        if isinstance(value, (set, frozenset)):
            return "{" + ",".join(sorted(self.of_value(item) for item in value)) + "}"
        if isinstance(value, dict):
            return "{" + ",".join(sorted(
                f"{self.of_value(key)}:{self.of_value(item)}" for key, item in value.items()
            )) + "}"
        if isinstance(value, enum.Enum):
            return f"{type(value).__name__}.{value.name}"
        if isinstance(value, (str, int, float, bool, type(None))):
            return repr(value)
        raise TypeError(f"no stable fingerprint for a {type(value).__name__} field value")

    def hashed(self, *parts: str) -> str:
        return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]

class TestLocationRuleSnapshot(bases.Age2RuleTestBase):
    campaigns = CONNECTED_CAMPAIGNS
    starting_campaigns = [Age2CampaignData.GENGHIS.campaign_name]

    def fingerprint_every_location(self) -> dict[str, str]:
        self.build()
        fingerprints = Fingerprints()
        return {
            location.name: fingerprints.of_location(location)
            for location in self.multiworld.get_locations(self.world.player)
        }

    def test_every_location_asks_what_it_asked_on_v0_3_0(self):
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        built = self.fingerprint_every_location()
        self.assertEqual(sorted(snapshot), sorted(built), "the set of locations changed")
        for name in snapshot:
            with self.subTest(location=name):
                self.assertEqual(snapshot[name], built[name],
                                 f"{name} resolves to a different rule than it did on v0.3.0")

if __name__ == "__main__":
    test = TestLocationRuleSnapshot()
    snapshot = test.fingerprint_every_location()
    SNAPSHOT.write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                        newline="\n")
    print(f"Wrote {len(snapshot)} location fingerprints to {SNAPSHOT}")
