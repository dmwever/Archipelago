"""Recapture test/easy_source_answers.json after a deliberate logic change.

    python -m worlds.age2de.tools.recapture_easy_sources     # from the repository root

`TestEveryEasySourceAnswersAsBefore` asks every scenario for every resource across 302 states and
seven option sets, and fails when an answer moves. That is the point: it catches a rule change
reaching further than intended. Recapture only once you have decided the movement is correct, and
say in the ticket which answers moved and why.

**Check the writer before you trust the diff.** On an unmodified tree, run this and confirm

    git diff --quiet -- worlds/age2de/test/easy_source_answers.json

succeeds. If it does not, the writer disagrees with the committed formatting and the diff you are
about to read is noise, not behaviour. Ask `git diff`, not `git status`: the repo checks out CRLF
(`core.autocrlf=true`) and this writes LF, so `git status` calls the file modified even when every
answer is identical. The index stores LF either way.

Reading the diff: `states` is one string per state, one character per question, `1` for yes. The
questions are listed once, in order, so a flipped character is a scenario and resource you can
name. Answers moving from `1` to `0` are a tightening, `0` to `1` a loosening.
"""
from __future__ import annotations

import json


def recapture() -> dict:
    from worlds.age2de.test.test_economy_routes import (
        EASY_SOURCE_ANSWERS,
        EasySourceEquivalenceBase,
    )

    class Capture(EasySourceEquivalenceBase):
        def runTest(self) -> None:
            pass

    answers = Capture().every_config_answers()
    EASY_SOURCE_ANSWERS.write_text(json.dumps(answers, indent=1) + "\n",
                                   encoding="utf-8", newline="\n")
    return {"path": EASY_SOURCE_ANSWERS, "configs": list(answers)}


if __name__ == "__main__":
    written = recapture()
    print(f"wrote {written['path']}")
    print(f"configs: {', '.join(written['configs'])}")
