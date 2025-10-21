from constant import *
from utils.icpcglobal import get_team, logger
from utils.domain import LocalTeam
from utils.dao import ACTeamRecord, ErrorRecord
from sqlalchemy.orm import Session
from utils.domain import ICPCTeam

def check_is_have_team_ac_on_icpcglobal(team_id: str) -> tuple[bool, ICPCTeam|None, list[str]]:
    icpc_team = get_team(team_id)
    if icpc_team is None:
        return False, None, [f"icpc.global获取队伍{team_id}失败，请检查队伍id是否正确。"]
    return True, icpc_team, []

def check_contest_correct(icpc_team: ICPCTeam) -> tuple[bool,list[str]]:
    if icpc_team.contest_id != CONTEST_ID:
        return False, [
            f"比赛id核验失败，您报名的比赛是\"{icpc_team.contest_name}(id为{icpc_team.contest_id})\",本届比赛是\"{CONTEST_NAME}(id为{CONTEST_ID})\"，请检查您的队伍id是否正确，并且是否报名了正确的比赛。"
        ]
    return True,[]

def check_team_name(icpc_team: ICPCTeam, team: ICPCTeam) -> tuple[bool,list[str]]:
    if icpc_team.english_name != team.english_name:
        return False, [
            f"队伍英文名称核验失败，icpc.global上的队伍名称是\"{icpc_team.english_name}\",您提交的队伍名称是\"{team.english_name}\"。"
        ]
    return True,[]

def check_name_ok(name1: str, name2: str) -> bool:
    """
    比较两个名字是否相同，考虑以下情况：
    1. 大小写不同
    2. 名字格式不同（可能有空格分割）
    3. 名姓顺序可能不同（如 "Zhang San" vs "San Zhang"）
    """
    name1 = name1.replace("'", "")
    name2 = name2.replace("'", "")
    # 统一转小写并分割
    name1_lower = name1.lower().strip()
    name2_lower = name2.lower().strip()
    
    # 分割成单词列表
    name1_parts = name1_lower.split()
    name2_parts = name2_lower.split()
    
    # 如果其中一个是空的，直接比较
    if not name1_parts or not name2_parts:
        return name1_lower == name2_lower
    
    # 先检查完全无空格版本
    name1_no_space = ''.join(name1_parts)
    name2_no_space = ''.join(name2_parts)
    if name1_no_space == name2_no_space:
        return True
    
    # 处理单词数不同的情况，尝试多种组合方式
    # 将所有单词组合生成可能的名字表示
    def generate_combinations(parts):
        combinations = set()
        # 原始顺序
        combinations.add(' '.join(parts))
        # 逆序
        combinations.add(' '.join(reversed(parts)))
        # 如果是2个字或3个字，生成不同的组合方式
        if len(parts) == 2:
            combinations.add(parts[0] + parts[1])  # 无空格
            combinations.add(parts[1] + parts[0])  # 逆序无空格
        elif len(parts) == 3:
            # 各种可能的组合方式
            combinations.add(parts[0] + parts[1] + parts[2])
            combinations.add(parts[2] + parts[1] + parts[0])
            combinations.add(parts[0] + ' ' + parts[1] + parts[2])
            combinations.add(parts[0] + parts[1] + ' ' + parts[2])
            combinations.add(parts[2] + ' ' + parts[1] + parts[0])
            combinations.add(parts[2] + parts[1] + ' ' + parts[0])
        return combinations
    
    # 生成两个名字的所有可能组合
    name1_combinations = generate_combinations(name1_parts)
    name2_combinations = generate_combinations(name2_parts)
    
    # 检查有空格的各种组合
    return bool(name1_combinations & name2_combinations)  # 使用集合交集

def check_coach_info(local_team: LocalTeam, icpc_team: ICPCTeam) -> tuple[bool,list[str]]:
    local_coaches = []
    for coach in local_team.coach:
        local_coaches.append(coach.english_name)
    
    icpc_coaches = []
    for coach in icpc_team.coach:
        icpc_coaches.append(coach.english_name)
    for coach_name in local_coaches:
        found = False
        for icpc_coach_name in icpc_coaches:
            if check_name_ok(icpc_coach_name, coach_name):
                found = True
                break
        if not found:
            return False, [
                f"教练信息核验失败，报名表中的教练姓名是\"{coach_name}\",但icpc.global上的教练姓名列表是\"{icpc_coaches}\"，无法在icpc.global上找到对应教练(报名表中姓名英文使用中文自动生成，如确认官网正确，可忽略本条）。"
            ]
    return True,[]

def check_member_info(local_team: LocalTeam, icpc_team: LocalTeam) -> tuple[bool,list[str]]:
    
    local_member_names = []
    for member in local_team.members:
        local_member_names.append(member.english_name)
    
    icpc_member_names = []
    for member in icpc_team.members:
        icpc_member_names.append(member.english_name)
    for member_name in local_member_names:
        found = False
        for icpc_member_name in icpc_member_names:
            if check_name_ok(icpc_member_name, member_name):
                found = True
                break
        if not found:
            return False, [
                f"队员信息核验失败，报名表中的队员姓名是\"{member_name}\",但icpc.global上的队员姓名列表是\"{icpc_member_names}\"，无法在icpc.global上找到对应队员(报名表中姓名英文使用中文自动生成，如确认官网正确，可忽略本条）。"
                ]
    return True,[]

def check(session:Session,local_team: LocalTeam)-> tuple[bool, list]:
    logger.info(f"正在核验{local_team.icpc_id},{local_team.english_name}...")
    ac_team: ACTeamRecord = session.query(ACTeamRecord).filter_by(team_id=local_team.icpc_id).first()
    if ac_team is not None:  # 已经AC直接跳过
        logger.info(f"{local_team.icpc_id}已存在AC记录，跳过核验")
        return True,[]

    errors = list()

    # 1. 从icpc.global获取队伍信息
    ok, icpc_team, icpc_errors = check_is_have_team_ac_on_icpcglobal(local_team.icpc_id)
    if not ok or icpc_team is None:
        errors.extend(icpc_errors)
        return False,errors
    else:
        logger.info(f"成功获取队伍{local_team.icpc_id}的icpc.global信息")

    # 2. 核验报名比赛是否是当前比赛
    ok, contest_errors = check_contest_correct(icpc_team)
    if not ok:
        errors.extend(contest_errors)
        return False,errors
    else:
        logger.info(f"队伍{local_team.icpc_id}报名比赛核验通过")
    
    # 3. 核验队伍名称
    ok, name_errors = check_team_name(icpc_team, local_team)
    if not ok:
        errors.extend(name_errors)
    else:
        logger.info(f"队伍{local_team.icpc_id}名称核验通过")

    # 4. 核验教练信息
    ok, coach_errors = check_coach_info(local_team, icpc_team)
    if not ok:
        errors.extend(coach_errors)
    else:
        logger.info(f"队伍{local_team.icpc_id}教练信息核验通过")
    
    # 5. 核验队员信息
    ok, member_errors = check_member_info(local_team, icpc_team)
    if not ok:
        errors.extend(member_errors)
    else:
        logger.info(f"队伍{local_team.icpc_id}队员信息核验通过")
            
    if len(errors) == 0:
        return True,[]
    else:
        return False,errors
