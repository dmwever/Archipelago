from dataclasses import dataclass
from typing import Iterable

from ....items.Items import Age2ItemData


@dataclass(frozen=True)
class Row:
    mercenary: Age2ItemData

    @property
    def unit_count(self) -> int:
        """Every soldier, not every kind. The queue file writes one id per soldier and carries no
        length, so this is what tells the reader where one seat's units end and the next begins."""
        return sum(unit.count for unit in self.mercenary.type.units)


class MercenaryData:
    """Renders MercenaryData.xs: the seed's mercenaries as a table the game loads at startup.

    Built with no arguments it renders the placeholder a shipped install carries, so the include in
    AP.xs resolves before anyone has run /install.
    """

    MERCENARY_CAPACITY = 100

    def __init__(self, mercenaries: Iterable[Age2ItemData] = ()):
        self._mercenaries = list(mercenaries)

    def rows(self) -> list[Row]:
        out = [Row(mercenary) for mercenary in self._mercenaries]
        for row in out:
            if '"' in row.mercenary.item_name:
                raise ValueError(
                    f"{row.mercenary.item_name} has a double quote in it, which would end the "
                    "string early in the generated XS")
            if row.unit_count < 1:
                raise ValueError(
                    f"{row.mercenary.item_name} has no units, so its seat would never finish")
        if len(out) > self.MERCENARY_CAPACITY:
            raise ValueError(
                f"{len(out)} mercenaries is past the XS capacity of {self.MERCENARY_CAPACITY}; "
                "raise MERCENARY_CAPACITY in MercenaryTable.xs to match")
        return out

    def render(self) -> str:
        lines = ["void LoadMercenaryTable() {"]
        body = len(lines)
        for row in self.rows():
            lines.append(f'    addMercenary({row.mercenary.id}, "{row.mercenary.item_name}", '
                         f'{row.unit_count});')
        if len(lines) == body:
            # The engine rejects an empty function body even where the linter accepts one.
            lines.append("    return;")
        lines.append("}")
        return "\n".join(lines) + "\n"
