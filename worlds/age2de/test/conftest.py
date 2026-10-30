from rule_builder.rules import CustomRuleRegister


def pytest_runtest_teardown(item, nextitem):
    if nextitem is None or nextitem.cls is not item.cls:
        CustomRuleRegister.resolved_rules.clear()
