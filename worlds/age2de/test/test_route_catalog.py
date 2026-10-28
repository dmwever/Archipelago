"""The economy route catalog is pinned.

A route added, renamed, repriced or multiplied arrives as a diff in `test/route_catalog.md` that
a human can read, instead of as a count nobody checks. Playtest #23's first design doubled the
catalog from 42 routes per scenario to 85 and nothing said so.
"""
import unittest

from ..tools.route_catalog import CATALOG, build_worlds, render


class TestRouteCatalogIsPinned(unittest.TestCase):

    maxDiff = None   # the diff is the whole point of this test; never truncate it

    def test_the_committed_catalog_matches_the_rules(self):
        committed = CATALOG.read_text(encoding="utf-8").splitlines()
        rendered = render(build_worlds()).splitlines()
        self.assertEqual(
            committed,
            rendered,
            "the economy route catalog has moved. Read the diff above: a route that gained a "
            "need, a scenario that lost one, or a route count that jumped is the change to "
            "explain. Regenerate with `python -m worlds.age2de.tools.route_catalog`.",
        )


if __name__ == "__main__":
    unittest.main()
