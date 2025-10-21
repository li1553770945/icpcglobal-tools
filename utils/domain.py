from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Coach:
    """教练信息类"""
    chinese_name: Optional[str]
    english_name: Optional[str]
    email: Optional[str]


@dataclass
class TeamMember:
    """队员信息类"""
    chinese_name: Optional[str]
    english_name: Optional[str]
    gender: Optional[str]
    phone: Optional[str]
    email: Optional[str]


@dataclass
class LocalTeam:
    """队伍信息类"""
    chinese_name: str  # 中文队名
    english_name: str  # 英文队名
    school: str  # 队伍学校
    icpc_id: str  # ICPC_id
    coach: List[Coach]  # 教练信息
    members: List[TeamMember]  # 队员列表（最多3个）

    def __post_init__(self):
        """初始化后处理"""
        # 确保成员不超过3个
        if len(self.members) > 3:
            self.members = self.members[:3]

@dataclass
class ICPCTeam:
    """从icpc.global获取的队伍信息类"""
    chinese_name: str  # 中文队名
    english_name: str  # 英文队名
    school: str  # 队伍学校
    contest_id: str  # 比赛ID
    contest_name: str  # 比赛名称
    icpc_id: str  # ICPC_id
    coach: List[Coach]  # 教练信息
    members: List[TeamMember]  # 队员列表（最多3个）

    def __post_init__(self):
        """初始化后处理"""
        # 确保成员不超过3个
        if len(self.members) > 3:
            self.members = self.members[:3]