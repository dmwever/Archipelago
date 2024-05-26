from dataclasses import dataclass

from .game_item import Requirement
from ..strings.tool_names import ToolMaterial


@dataclass(frozen=True)
class BookRequirement(Requirement):
    book: str


@dataclass(frozen=True)
class ToolRequirement(Requirement):
    tool: str
    tier: str = ToolMaterial.basic
