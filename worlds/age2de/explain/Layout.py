"""Indented, coloured lines for UT's log, wrapped here rather than by the log: a line the log wraps
itself loses its indentation."""
from __future__ import annotations

from NetUtils import JSONMessagePart

INDENT = "    "
BUDGETED_ITEMS = "Budgeted Items"
"""What /explain takes for the seed's budget order rather than a location."""
WIDTH = 70
"""Characters a line may run to before it continues on the next, one level deeper."""


def text(value: str) -> JSONMessagePart:
    return {"type": "text", "text": value}


def colored(value: str, ok: bool) -> JSONMessagePart:
    return {"type": "color", "color": "green" if ok else "salmon", "text": value}


def truth(ok: bool) -> JSONMessagePart:
    return colored("True" if ok else "False", ok)


class Lines:
    """One log entry: lines of parts, each at an indentation level."""

    def __init__(self) -> None:
        self._lines: list[tuple[int, list[JSONMessagePart]]] = []

    def add(self, depth: int, *parts: JSONMessagePart) -> None:
        self._lines.append((depth, list(parts)))

    def add_segments(self, depth: int, head: str, segments: list[list[JSONMessagePart]],
                     separator: str = " · ", tail: tuple[JSONMessagePart, ...] = ()) -> None:
        """`head` then the segments joined by `separator`, continuing one level deeper whenever
        the next segment would run the line past WIDTH; `tail` - a drill-down marker - ends it."""
        line: list[JSONMessagePart] = [text(head)]
        length = len(INDENT * depth) + len(head)
        current = depth
        for index, segment in enumerate(segments):
            size = sum(len(part["text"]) for part in segment)
            joiner = separator if index else ""
            if index and length + len(joiner) + size > WIDTH:
                self._lines.append((current, line))
                current = depth + 1
                line, length, joiner = [], len(INDENT * current), ""
            line += [text(joiner), *segment] if joiner else list(segment)
            length += len(joiner) + size
        self._lines.append((current, line + list(tail)))

    def parts(self) -> list[JSONMessagePart]:
        out: list[JSONMessagePart] = []
        for index, (depth, line) in enumerate(self._lines):
            out.append(text(("\n" if index else "") + INDENT * depth))
            out += line
        return out

    def plain(self) -> str:
        """The entry as plain text, for tests and logs."""
        return "".join(part["text"] for part in self.parts())


def _ranges(numbers: list[int]) -> str:
    """1, 2, 3, 5 -> "1–3, 5"."""
    runs: list[list[int]] = []
    for number in numbers:
        if runs and number == runs[-1][-1] + 1:
            runs[-1].append(number)
        else:
            runs.append([number])
    return ", ".join(f"{run[0]}–{run[-1]}" if len(run) > 1 else f"{run[0]}" for run in runs)
