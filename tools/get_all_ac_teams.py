import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import setup_logger
from utils.icpcglobal import test_token,get_all_ac_team
from utils.parse_teams import parse_teams_from_csv
if __name__ == "__main__":
    logger = setup_logger()
    all_teams = parse_teams_from_csv("data/ICPC队伍信息表_20251018001555.csv")
    if test_token():
        teams = get_all_ac_team()
        for team in teams:
            find = False
            for local_team in all_teams:
                # print(team['id'], local_team.icpc_id)
                if str(team['id']).strip() == str(local_team.icpc_id).strip():
                    find = True
            if not find:
                logger.info(f"队伍ID:{team['id']}已AC但未在报名表！")

        for local_team in all_teams:
            find = False
            for team in teams:
                if str(team['id']).strip() == str(local_team.icpc_id).strip():
                    find = True
            if not find:
                logger.info(f"队伍ID:{local_team.icpc_id}未AC！")
                
    else:
        logger.info("token已失效")
