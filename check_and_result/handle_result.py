from constant import *
from utils.icpcglobal import get_team, logger,set_ac
from utils.domain import LocalTeam
from utils.dao import ACTeamRecord, ErrorRecord
from sqlalchemy.orm import Session
from utils.mail import Mail
from datetime import datetime

mail = Mail()

def send_ac(team:LocalTeam, send_to:str):
    if send_to == "CONTESTANTS":
        for contestant in team.members:
            msg = f"{contestant.chinese_name}同学你好，我是{CONTEST_NAME}工作人员，你们的队伍\"{team.english_name}({team.english_name},队伍id为{team.team_id})\"与icpc.global信息核对已通过，预祝同学取得优异成绩！"
            mail.send(contestant.email, f"{CONTEST_SHORT_NAME}队伍审核通过通知", msg)
    if send_to == "COACH":
        for coach in team.coach:
            msg = f"尊敬的{team.school}{coach.chinese_name}教练，我是{CONTEST_NAME}工作人员，贵校报名的队伍\"{team.english_name}({team.english_name},队伍id为{team.team_id})\"与icpc.global信息核对已通过，预祝贵校取得优异成绩！"
            mail.send(coach.email, f"{CONTEST_SHORT_NAME}队伍审核通过通知", msg)


def send_error(check_id:str,team:LocalTeam, send_to:str, errors:list):
    if send_to == "CONTESTANTS":
        for contestant in team.members:
            msg = f"{contestant.chinese_name}同学你好，我是{CONTEST_NAME}工作人员，你们的队伍\"{team.english_name}({team.english_name},队伍id为{team.icpc_id})\"与icpc.global信息核对因以下原因暂未核对通过，请及时更正：<br><br>"
            for i, error in enumerate(errors):
                msg += f"{i + 1}.{error}<br>"
            msg += "<br>请更正后耐心等待，我们将会不定期重新对所有队伍进行核验，核验结果将通过邮件通知。<br>"
            msg += f"如有疑问需联系工作人员，请提供以下信息：队伍id:{team.icpc_id},核验id:{check_id}"
            mail.send(contestant.email, f"{CONTEST_SHORT_NAME}队伍审核未通过通知", msg)
    if send_to == "COACH":
        msg = f"尊敬的{team.school}{team.coach[0].chinese_name}教练，我是{CONTEST_NAME}工作人员，贵校报名的队伍\"{team.english_name}({team.english_name},队伍id为{team.icpc_id})\"与icpc.global信息核对因以下原因暂未核对通过，请您及时更正：<br><br>"
        for i, error in enumerate(errors):
            msg += f"{i + 1}.{error}<br>"
        msg += "<br>请您更正后耐心等待，我们将会不定期重新对所有队伍进行核验，核验结果将通过邮件通知。<br>"
        msg += f"如有疑问需联系工作人员，请提供以下信息：队伍id:{team.icpc_id},核验id:{check_id}"
        mail.send(team.coach[0].email, f"{CONTEST_SHORT_NAME}队伍审核未通过通知", msg)


def handle_error(session:Session,check_id:str,team:LocalTeam, errors:list[str]):
    error_team: ErrorRecord = session.query(ErrorRecord).filter_by(team_id=team.icpc_id, check_id=check_id).first()
    if error_team is None:
        error_team = ErrorRecord(team_id=team.icpc_id, check_id=check_id, errors=str(errors))
        session.add(error_team)
        session.commit()
    if SEND_ERROR_TO_CONTESTANTS and not error_team.is_send_to_contestant:
        send_error(check_id=check_id,team=team,send_to="CONTESTANTS", errors=errors)
        error_team.is_send_to_contestant = True
        error_team.send_to_contestant_time = datetime.now()
        session.commit()

    if SEND_ERROR_TO_COACH and not error_team.is_send_to_coach:
        send_error(check_id=check_id,team=team,send_to="COACH", errors=errors)
        error_team.is_send_to_coach = True
        error_team.send_to_coach_time = datetime.now()
        session.commit()

    logger.warning(f"核验失败,{team.icpc_id},{errors}")


def handle_success(session:Session,team:LocalTeam):
    ac_team: ACTeamRecord = session.query(ACTeamRecord).filter_by(team_id=team.icpc_id).first()
    if ac_team is None:
        ac_team = ACTeamRecord(team_id=team.icpc_id)
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
        if set_ac(team.icpc_id):
            ac_team.is_ac_on_icpcglobal = True
            ac_team.ac_on_icpcglobal_time = datetime.now()
            session.commit()

    logger.info(f"核验通过,{team.icpc_id}")