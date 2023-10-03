from constant import *
from read_data import read_excel_data
from icpcglobal import get_team, test_token, set_ac
from dao import ACTeamRecord, ErrorRecord, init_database
from datetime import datetime
from mail_utils import Mail


def print_data(schools):
    for school in schools:
        print(f"学校\"{school.name}\"共报名{len(school.teams)}支队伍：\n")
        for team in school.teams:
            print(f"{team.name},{team.english_name},{team.team_id}")
            print(f"教练：{team.coach.name}({team.coach.english_name})")
            print(f"队员:{team.contestants[0].name}({team.contestants[0].english_name})"
                  f",{team.contestants[1].name}({team.contestants[1].english_name})"
                  f",{team.contestants[2].name}({team.contestants[2].english_name})")
            print("\n")

        print("--------------")


def send_ac(team, send_to):
    if send_to == "CONTESTANTS":
        for contestant in team.contestants:
            msg = f"{contestant.name}同学你好，我是{CONTEST_NAME}工作人员，你们的队伍\"{team.name}({team.english_name})\"与icpc.global信息核对已通过，预祝同学取得优异成绩！"
            mail.send(contestant.email, f"{CONTEST_SHORT_NAME}队伍审核通过通知", msg)
    if send_to == "COACH":
        msg = f"尊敬的{team.school}{team.coach.name}教练，我是{CONTEST_NAME}工作人员，贵校报名的队伍\"{team.name}({team.english_name})\"与icpc.global信息核对已通过，预祝贵校取得优异成绩！"
        mail.send(team.coach.email, f"{CONTEST_SHORT_NAME}队伍审核通过通知", msg)


def send_error(team, send_to, errors):
    if send_to == "CONTESTANTS":
        for contestant in team.contestants:
            msg = f"{contestant.name}同学你好，我是{CONTEST_NAME}工作人员，你们的队伍\"{team.name}({team.english_name})\"与icpc.global信息核对因以下原因暂未核对通过，请及时更正：<br><br>"
            for i, error in enumerate(errors):
                msg += f"{i + 1}.{error}<br>"
            msg += "<br>请更正后耐心等待，我们将会不定期重新对所有队伍进行核验，核验结果将通过邮件通知。<br>"
            msg += f"如有疑问需联系工作人员，请提供以下信息：队伍id:{team.team_id},核验id:{check_id}"
            mail.send(contestant.email, f"{CONTEST_SHORT_NAME}队伍审核未通过通知", msg)
    if send_to == "COACH":
        msg = f"尊敬的{team.school}{team.coach.name}教练，我是{CONTEST_NAME}工作人员，贵校报名的队伍\"{team.name}({team.english_name})\"与icpc.global信息核对因以下原因暂未核对通过，请您及时更正：<br><br>"
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

    print(f"核验失败,{team.team_id},{errors}")


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

    print(f"核验通过,{team.team_id}")


def check(team):

    ac_team: ACTeamRecord = session.query(ACTeamRecord).filter_by(team_id=team.team_id).first()
    if ac_team is not None:  # 已经AC直接跳过
        print(f"{team.team_id}已存在AC记录，跳过核验")
        handle_success(team)
        return True

    icpc_team = get_team(team.team_id)
    errors = list()
    if icpc_team.english_name.lower().replace('\xa0', ' ') != team.english_name.lower().replace('\xa0', ' '):
        errors.append(
            f"队伍名称不匹配，icpc.global报名的名称为\"{icpc_team.english_name}\",报名表中填写名称为\"{team.english_name}\"，请确保以上两项<b>逐字符相同</b>。")

    if icpc_team.coach.english_name.lower().replace('\xa0', ' ') != team.coach.english_name.lower().replace('\xa0', ' '):
        for cocoach in icpc_team.cocoach:
            if cocoach.english_name.lower().replace('\xa0', ' ') == team.coach.english_name.lower().replace('\xa0', ' '):
                break
        else:
            errors.append(
                f"教练姓名不匹配，icpc.global报名的名称为\"{icpc_team.coach.english_name}\",报名表中填写名称为\"{team.coach.english_name}\"，"
                f"请确保以上两项<b>逐字符相同</b>,例如\"Zhang San\"、\"San Zhang\"会被认为是不同姓名。")

    contests_icpc = [icpc_team.contestants[0].english_name, icpc_team.contestants[1].english_name,
                     icpc_team.contestants[2].english_name]
    for contestant in team.contestants:
        is_find = False
        for contestant_icpc in icpc_team.contestants:
            if contestant_icpc.english_name.lower() == contestant.english_name.lower():
                is_find = True
                break
        if not is_find:
            errors.append(
                f"报名表中队员\"{contestant.english_name}\"未能在icpc.global中找到。icpc.global中队员为{contests_icpc}"
                f"请确保队员姓名与icpc.global上<b>逐字符相同</b>,例如\"Zhang San\"、\"San Zhang\"会被认为是不同姓名")

    if len(errors) == 0:
        handle_success(team)
        return True
    else:
        handle_error(team, errors)
        return False


if __name__ == "__main__":

    check_id: str = "002"
    if test_token():
        session = init_database()
        mail = Mail()
        schools = read_excel_data(FILE_NAME)

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
        print(f"已完成，共检查{total_num}队，AC{ac_num}队，有错误{error_num}队")
    else:
        print("token已失效")
