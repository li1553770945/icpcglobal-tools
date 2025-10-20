from data.constant import *
from utils.read_data import read_excel_data
from utils.icpcglobal import get_team, test_token, set_ac, get_contest_name, logger
from utils.dao import ACTeamRecord, ErrorRecord, init_database
from datetime import datetime
from utils.mail_utils import Mail
import re
from utils.logger import setup_logger

def print_data(schools):
    for school in schools:
        logger.info(f"学校\"{school.name}\"共报名{len(school.teams)}支队伍：\n")
        for team in school.teams:
            logger.info(f"{team.name},{team.english_name},{team.team_id}")
            logger.info(f"教练：{team.coach.name}({team.coach.english_name})")
            logger.info(f"队员:{team.contestants[0].name}({team.contestants[0].english_name})"
                  f",{team.contestants[1].name}({team.contestants[1].english_name})"
                  f",{team.contestants[2].name}({team.contestants[2].english_name})")
            logger.info("\n")

        logger.info("--------------")


def send_ac(team, send_to):
    if send_to == "CONTESTANTS":
        for contestant in team.contestants:
            msg = f"{contestant.name}同学你好，我是{CONTEST_NAME}工作人员，你们的队伍\"{team.name}({team.english_name},队伍id为{team.team_id})\"与icpc.global信息核对已通过，预祝同学取得优异成绩！"
            mail.send(contestant.email, f"{CONTEST_SHORT_NAME}队伍审核通过通知", msg)
    if send_to == "COACH":
        msg = f"尊敬的{team.school}{team.coach.name}教练，我是{CONTEST_NAME}工作人员，贵校报名的队伍\"{team.name}({team.english_name},队伍id为{team.team_id})\"与icpc.global信息核对已通过，预祝贵校取得优异成绩！"
        mail.send(team.coach.email, f"{CONTEST_SHORT_NAME}队伍审核通过通知", msg)


def send_error(team, send_to, errors):
    if send_to == "CONTESTANTS":
        for contestant in team.contestants:
            msg = f"{contestant.name}同学你好，我是{CONTEST_NAME}工作人员，你们的队伍\"{team.name}({team.english_name},队伍id为{team.team_id})\"与icpc.global信息核对因以下原因暂未核对通过，请及时更正：<br><br>"
            for i, error in enumerate(errors):
                msg += f"{i + 1}.{error}<br>"
            msg += "<br>请更正后耐心等待，我们将会不定期重新对所有队伍进行核验，核验结果将通过邮件通知。<br>"
            msg += f"如有疑问需联系工作人员，请提供以下信息：队伍id:{team.team_id},核验id:{check_id}"
            mail.send(contestant.email, f"{CONTEST_SHORT_NAME}队伍审核未通过通知", msg)
    if send_to == "COACH":
        msg = f"尊敬的{team.school}{team.coach.name}教练，我是{CONTEST_NAME}工作人员，贵校报名的队伍\"{team.name}({team.english_name},队伍id为{team.team_id})\"与icpc.global信息核对因以下原因暂未核对通过，请您及时更正：<br><br>"
        for i, error in enumerate(errors):
            msg += f"{i + 1}.{error}<br>"
        msg += "<br>请您更正后耐心等待，我们将会不定期重新对所有队伍进行核验，核验结果将通过邮件通知。<br>"
        msg += f"如有疑问需联系工作人员，请提供以下信息：队伍id:{team.team_id},核验id:{check_id}"
        mail.send(team.coach.email, f"{CONTEST_SHORT_NAME}队伍审核未通过通知", msg)


def handle_error(team, errors):
    error_team: ErrorRecord = session.query(ErrorRecord).filter_by(team_id=team.team_id, check_id=check_id).first()
    if error_team is None:
        error_team = ErrorRecord(team_id=team.team_id, check_id=check_id, errors=str(errors))
        session.add(error_team)
        session.commit()
    if SEND_ERROR_TO_CONTESTANTS and not error_team.is_send_to_contestant:
        send_error(team, "CONTESTANTS", errors)
        error_team.is_send_to_contestant = True
        error_team.send_to_contestant_time = datetime.now()
        session.commit()

    if SEND_ERROR_TO_COACH and not error_team.is_send_to_coach:
        send_error(team, "COACH", errors)
        error_team.is_send_to_coach = True
        error_team.send_to_coach_time = datetime.now()
        session.commit()

    logger.warning(f"核验失败,{team.team_id},{errors}")


def handle_success(team):
    ac_team: ACTeamRecord = session.query(ACTeamRecord).filter_by(team_id=team.team_id).first()
    if ac_team is None:
        ac_team = ACTeamRecord(team_id=team.team_id)
        session.add(ac_team)
        session.commit()
    if SEND_AC_TO_CONTESTANTS and not ac_team.is_send_to_contestant:
        send_ac(team, "CONTESTANTS")
        ac_team.is_send_to_contestant = True
        ac_team.send_to_contestant_time = datetime.now()
        session.commit()

    if SEND_AC_TO_COACH and not ac_team.is_send_to_coach:
        send_ac(team, "COACH")
        ac_team.is_send_to_coach = True
        ac_team.send_to_coach_time = datetime.now()
        session.commit()

    if OPERATE_ICPC_GLOBAL and not ac_team.is_ac_on_icpcglobal:
        if set_ac(team.team_id):
            ac_team.is_ac_on_icpcglobal = True
            ac_team.ac_on_icpcglobal_time = datetime.now()
            session.commit()

    logger.info(f"核验通过,{team.team_id}")


def check_name(name1, name2):
    name1 = name1.lower().replace('\xa0', ' ').strip()
    name2 = name2.lower().replace('\xa0', ' ').strip()
    if name1 == name2:
        return True
    name1 = name1.split(' ')
    name2 = name2.split(' ')
    if len(name1) != len(name2):
        return False

    name1.sort()
    name2.sort()
    for i in range(0, len(name1)):
        if name1[i] != name2[i]:
            return False
    return True


def check(team):
    logger.info(f"正在核验{team.team_id}")
    ac_team: ACTeamRecord = session.query(ACTeamRecord).filter_by(team_id=team.team_id).first()
    if ac_team is not None:  # 已经AC直接跳过
        logger.info(f"{team.team_id}已存在AC记录，跳过核验")
        handle_success(team)
        return True

    errors = list()
    icpc_team = get_team(team.team_id)
    if icpc_team is None:
        errors.append(f"icpc.global获取队伍{team.team_id}失败，请检查队伍id是否正确。")
        handle_error(team, errors)
        return False

    if icpc_team.contest_id != CONTEST_ID:
        errors.append(
            f"比赛id核验失败，您报名的比赛是\"{icpc_team.contest_name}(id为{icpc_team.contest_id})\",本届比赛是\"{contest_name}(id为{CONTEST_ID})\"，请检查您的队伍id是否正确，并且是否报名了正确的比赛。")

    if icpc_team.english_name.lower().replace('\xa0', ' ') != team.english_name.lower().replace('\xa0', ' '):
        errors.append(
            f"队伍名称不匹配，icpc.global报名的名称为\"{icpc_team.english_name}\",报名表中填写名称为\"{team.english_name}\"，请确保以上两项<b>逐字符相同</b>。")

    pattern = r"^[a-zA-Z\s\-']+$"

    if not re.match(pattern, team.coach.english_name):
        errors.append(f"报名表中填写教练英文名为:{team.coach.english_name}，应该只包含大小写字母和空格。")
    if not check_name(icpc_team.coach.english_name, team.coach.english_name):
        for cocoach in icpc_team.cocoach:
            if check_name(cocoach.english_name, team.coach.english_name):
                break
        else:
            errors.append(
                f"教练姓名不匹配，icpc.global报名的名称为\"{icpc_team.coach.english_name}\",报名表中填写名称为\"{team.coach.english_name}\"，"
                f"请确保以上两项<b>逐字符相同</b>，例如\"Zhang San\"与\"San Zhang\"会被认为不同姓名。")

    contests_icpc = [contestant.english_name for contestant in icpc_team.contestants]
    for contestant in team.contestants:
        if contestant.english_name == "无":
            continue
        if not re.match(pattern, contestant.english_name):
            errors.append(f"报名表中填写队员英文名为:{contestant.english_name}，应该只包含大小写字母和空格。")
            continue

        is_find = False
        for contestant_icpc in icpc_team.contestants:
            if check_name(contestant_icpc.english_name, contestant.english_name):
                is_find = True
                break
        if not is_find:
            errors.append(
                f"报名表中队员\"{contestant.english_name}\"未能在icpc.global中找到。icpc.global中队员为{contests_icpc}"
                f"请确保队员姓名与icpc.global上<b>逐字符相同</b>，例如\"Zhang San\"与\"San Zhang\"会被认为不同姓名。")

    if len(errors) == 0:
        handle_success(team)
        return True
    else:
        handle_error(team, errors)
        return False


if __name__ == "__main__":
    check_id: str = "004"

    logger = setup_logger()
    if test_token():

        contest_name = get_contest_name()
        session = init_database()
        mail = Mail()
        schools = read_excel_data("data/"+FILE_NAME)

        total_num = 0
        ac_num = 0
        error_num = 0
        for school in schools:
            for team in school.teams:
                total_num += 1
                if check(team):
                    ac_num += 1
                else:
                    error_num += 1
        session.close()
        logger.info(f"已完成，共检查{total_num}队，AC{ac_num}队，有错误{error_num}队")
    else:
        logger.info("token已失效")
