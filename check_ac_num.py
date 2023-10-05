from dao import ACTeamRecord,init_database
from icpcglobal import get_team, test_token

if __name__ == "__main__":

    teams = list()
    if test_token():
        session = init_database()
        ac_teams = session.query(ACTeamRecord).all()
        for ac_team in ac_teams:
            if ac_team.team_id in teams:
                raise AssertionError(f"{ac_team.team_id}重复！")
            # icpc_team = get_team(ac_team.team_id)
            # if icpc_team.status != "ACCEPTED":
            #     print(f"team {ac_team.team_id}已经审核AC，但未在icpc.global AC")
            # else:
            #     print(f"{ac_team.team_id}已经AC")
    else:
        print("token已失效")
