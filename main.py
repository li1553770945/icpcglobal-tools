from constant import *
from utils.icpcglobal import get_team, test_token, set_ac, get_contest_name, logger
from utils.dao import ACTeamRecord, ErrorRecord, init_database
from datetime import datetime
from utils.mail import Mail
import re
from utils.logger import setup_logger
import sys
from utils.parse_teams import parse_teams_from_csv
from utils.domain import LocalTeam

from check_and_result.check import check
from check_and_result.handle_result import handle_success, handle_error





if __name__ == "__main__":
    team_file = "data/ICPC队伍信息表_20251018001555.csv"
    if len(sys.argv) < 2:
        logger = setup_logger()
        logger.error("缺少必要的命令行参数：check_id")
        logger.error("用法: python main.py <check_id>")
        sys.exit(1)
    
    check_id: str = sys.argv[1]

    logger = setup_logger()
    if test_token():
        contest_name = get_contest_name()
        session = init_database()
        mail = Mail()
        csv_teams = parse_teams_from_csv(team_file)
        for csv_team in csv_teams:
            try:
                ok,errors = check(session=session,local_team=csv_team)
                logger.info(f"队伍{csv_team.icpc_id}核验结果: {ok}, 错误信息: {errors}")
                if ok:
                    handle_success(session=session,team=csv_team)
                else:
                    handle_error(session=session,check_id=check_id,team=csv_team, errors=errors)
            except Exception as err:
                logger.error(f"处理队伍{csv_team.icpc_id}时发生异常: {err}")
                handle_error(session=session,check_id=check_id,team=csv_team, errors=["处理队伍时发生异常: "+str(err)])
                continue

    else:
        logger.info("token已失效")
