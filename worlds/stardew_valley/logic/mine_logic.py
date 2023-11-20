from Utils import cache_self1
from .combat_logic import CombatLogic
from .received_logic import ReceivedLogicMixin
from .region_logic import RegionLogicMixin
from .skill_logic import SkillLogic
from .tool_logic import ToolLogic
from .. import options
from ..mods.logic.elevator_logic import ModElevatorLogic
from ..options import ToolProgression, SkillProgression, ElevatorProgression
from ..stardew_rule import StardewRule, And, True_
from ..strings.performance_names import Performance
from ..strings.region_names import Region
from ..strings.skill_names import Skill
from ..strings.tool_names import Tool, ToolMaterial


class MineLogic:
    tool_option: ToolProgression
    skill_option: SkillProgression
    elevator_option: ElevatorProgression
    received: ReceivedLogicMixin
    region: RegionLogicMixin
    combat: CombatLogic
    tool: ToolLogic
    skill: SkillLogic
    mod_elevator: ModElevatorLogic

    def __init__(self, player: int, tool_option: ToolProgression, skill_option: SkillProgression, elevator_option: ElevatorProgression,
                 received: ReceivedLogicMixin,
                 region: RegionLogicMixin, combat: CombatLogic, tool: ToolLogic, skill: SkillLogic):
        self.player = player
        self.tool_option = tool_option
        self.skill_option = skill_option
        self.elevator_option = elevator_option
        self.received = received
        self.region = region
        self.combat = combat
        self.tool = tool
        self.skill = skill

    def set_modded_elevator(self, mod_elevator: ModElevatorLogic):
        self.mod_elevator = mod_elevator

    # Regions
    def can_mine_in_the_mines_floor_1_40(self) -> StardewRule:
        return self.region.can_reach(Region.mines_floor_5)

    def can_mine_in_the_mines_floor_41_80(self) -> StardewRule:
        return self.region.can_reach(Region.mines_floor_45)

    def can_mine_in_the_mines_floor_81_120(self) -> StardewRule:
        return self.region.can_reach(Region.mines_floor_85)

    def can_mine_in_the_skull_cavern(self) -> StardewRule:
        return (self.can_progress_in_the_mines_from_floor(120) &
                self.region.can_reach(Region.skull_cavern))

    @cache_self1
    def get_weapon_rule_for_floor_tier(self, tier: int):
        if tier >= 4:
            return self.combat.can_fight_at_level(Performance.galaxy)
        if tier >= 3:
            return self.combat.can_fight_at_level(Performance.great)
        if tier >= 2:
            return self.combat.can_fight_at_level(Performance.good)
        if tier >= 1:
            return self.combat.can_fight_at_level(Performance.decent)
        return self.combat.can_fight_at_level(Performance.basic)

    @cache_self1
    def can_progress_in_the_mines_from_floor(self, floor: int) -> StardewRule:
        tier = floor // 40
        rules = []
        weapon_rule = self.get_weapon_rule_for_floor_tier(tier)
        rules.append(weapon_rule)
        if self.tool_option & ToolProgression.option_progressive:
            rules.append(self.tool.has_tool(Tool.pickaxe, ToolMaterial.tiers[tier]))
        if self.skill_option == options.SkillProgression.option_progressive:
            skill_tier = min(10, max(0, tier * 2))
            rules.append(self.skill.has_level(Skill.combat, skill_tier))
            rules.append(self.skill.has_level(Skill.mining, skill_tier))
        return And(*rules)

    @cache_self1
    def has_mine_elevator_to_floor(self, floor: int) -> StardewRule:
        if floor < 0:
            floor = 0
        if self.elevator_option != options.ElevatorProgression.option_vanilla:
            return self.received("Progressive Mine Elevator", floor // 5)
        return True_()

    @cache_self1
    def can_progress_in_the_skull_cavern_from_floor(self, floor: int) -> StardewRule:
        tier = floor // 50
        rules = []
        weapon_rule = self.combat.has_great_weapon
        rules.append(weapon_rule)
        if self.tool_option & ToolProgression.option_progressive:
            rules.append(self.received("Progressive Pickaxe", min(4, max(0, tier + 2))))
        if self.skill_option == options.SkillProgression.option_progressive:
            skill_tier = min(10, max(0, tier * 2 + 6))
            rules.extend({self.skill.has_level(Skill.combat, skill_tier),
                          self.skill.has_level(Skill.mining, skill_tier)})
        return And(*rules)
