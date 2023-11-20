from ...logic.combat_logic import CombatLogic
from ...logic.cooking_logic import CookingLogic
from ...logic.has_logic import HasLogicMixin
from ...logic.received_logic import ReceivedLogicMixin
from ...logic.skill_logic import SkillLogic
from ...logic.tool_logic import ToolLogic
from ...options import SkillProgression, ElevatorProgression
from ...stardew_rule import StardewRule, True_, And
from ...strings.ap_names.transport_names import ModTransportation
from ...strings.craftable_names import Bomb
from ...strings.performance_names import Performance
from ...strings.skill_names import Skill
from ...strings.tool_names import Tool, ToolMaterial


class DeepWoodsLogic:
    player: int
    skill_option: SkillProgression
    elevator_option: ElevatorProgression
    received: ReceivedLogicMixin
    has: HasLogicMixin
    combat: CombatLogic
    tool: ToolLogic
    skill: SkillLogic
    cooking: CookingLogic

    def __init__(self, player: int, skill_option: SkillProgression, elevator_option: ElevatorProgression, received: ReceivedLogicMixin, has: HasLogicMixin,
                 combat: CombatLogic, tool: ToolLogic,
                 skill: SkillLogic, cooking: CookingLogic):
        self.player = player
        self.skill_option = skill_option
        self.elevator_option = elevator_option
        self.received = received
        self.has = has
        self.combat = combat
        self.tool = tool
        self.skill = skill
        self.cooking = cooking

    def can_reach_woods_depth(self, depth: int) -> StardewRule:
        tier = int(depth / 25) + 1
        rules = []
        if depth > 10:
            rules.append(self.has(Bomb.bomb) | self.tool.has_tool(Tool.axe, ToolMaterial.iridium))
        if depth > 30:
            rules.append(self.received(ModTransportation.woods_obelisk))
        if depth > 50:
            rules.append(self.combat.can_fight_at_level(Performance.great) & self.cooking.can_cook() &
                         self.received(ModTransportation.woods_obelisk))
        if self.skill_option == SkillProgression.option_progressive:
            combat_tier = min(10, max(0, tier + 5))
            rules.append(self.skill.has_level(Skill.combat, combat_tier))
        return And(*rules)

    def has_woods_rune_to_depth(self, floor: int) -> StardewRule:
        if self.elevator_option == ElevatorProgression.option_vanilla:
            return True_()
        return self.received("Progressive Woods Obelisk Sigils", int(floor / 10))

    def can_chop_to_depth(self, floor: int) -> StardewRule:
        previous_elevator = max(floor - 10, 0)
        return (self.has_woods_rune_to_depth(previous_elevator) &
                self.can_reach_woods_depth(previous_elevator))
