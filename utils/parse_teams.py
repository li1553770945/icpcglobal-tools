"""
解析ICPC队伍信息CSV文件的脚本
"""

import csv
from typing import List, Optional
from dataclasses import dataclass
from utils.domain import LocalTeam, Coach, TeamMember


def parse_teams_from_csv(csv_file_path: str) -> List[LocalTeam]:
    """
    从CSV文件解析队伍信息
    
    Args:
        csv_file_path: CSV文件路径
        
    Returns:
        Team对象列表
    """
    teams_dict = {}  # 用字典存储队伍，key为(队伍编号, icpc_id)
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            icpc_id = row.get('icpc_id', '').strip()
            chinese_name = row.get('中文队名', '').strip()
            english_name = row.get('英文队名', '').strip()
            school = row.get('队伍学校', '').strip()
            
            # 教练信息
            coach_chinese_name = row.get('教练名', '').strip() or None
            coach_english_name = row.get('Coach Name', '').strip() or None
            coach_email = row.get('教练邮箱', '').strip() or None
            
            # 队员信息
            member_chinese_name = row.get('队员姓名', '').strip() or None
            member_english_name = row.get('Team Member Name', '').strip() or None
            member_gender = row.get('队员性别', '').strip() or None
            member_phone = row.get('队员手机', '').strip() or None
            member_email = row.get('队员邮箱', '').strip() or None

            # 用(icpc_id,)作为唯一标识
            key = (icpc_id,)
            
            # 如果这个队伍还没有被创建
            if key not in teams_dict:
                coach = Coach(
                    chinese_name=coach_chinese_name,
                    english_name=coach_english_name,
                    email=coach_email
                )
                teams_dict[key] = LocalTeam(
                    chinese_name=chinese_name,
                    english_name=english_name,
                    school=school,
                    icpc_id=icpc_id,
                    coach=[coach],
                    members=[]
                )
            
            # 添加队员信息（避免重复）
            if member_chinese_name or member_english_name:
                member = TeamMember(
                    chinese_name=member_chinese_name,
                    english_name=member_english_name,
                    gender=member_gender,
                    phone=member_phone,
                    email=member_email
                )
                
                # 检查是否已经添加过这个队员
                if member not in teams_dict[key].members:
                    teams_dict[key].members.append(member)
    
    # 转换为列表并排序
    teams = list(teams_dict.values())
    return teams


def print_teams(teams: List[LocalTeam]):
    """
    打印队伍信息
    
    Args:
        teams: Team对象列表
    """
    for i, team in enumerate(teams, 1):
        print(f"\n{'='*60}")
        print(f"队伍 {i}")
        print(f"{'='*60}")
        print(f"中文队名: {team.chinese_name}")
        print(f"英文队名: {team.english_name}")
        print(f"学校: {team.school}")
        print(f"ICPC ID: {team.icpc_id}")
        
        print(f"\n教练信息:")
        for j, coach in enumerate(team.coach, 1):
            print(f"  教练 {j}:")
            print(f"    中文名: {coach.chinese_name}")
            print(f"    英文名: {coach.english_name}")
            print(f"    邮箱: {coach.email}")

        print(f"\n队员信息 ({len(team.members)}):")
        for j, member in enumerate(team.members, 1):
            print(f"  队员 {j}:")
            print(f"    中文名: {member.chinese_name}")
            print(f"    英文名: {member.english_name}")
            print(f"    性别: {member.gender}")
            print(f"    手机: {member.phone}")
            print(f"    邮箱: {member.email}")


if __name__ == '__main__':
    csv_file = 'data/ICPC队伍信息表_20251018001555.csv'
    
    teams = parse_teams_from_csv(csv_file)
    print(f"成功读取 {len(teams)} 个队伍")
    print_teams(teams)
    
 