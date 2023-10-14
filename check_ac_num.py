from utils.icpcglobal import get_all_ac_team
from utils.dao import ACTeamRecord,init_database
if __name__ == "__main__":
    all_teams = get_all_ac_team()
    icpc_ids = [str(team['id']) for team in all_teams]
    icpc_ids = set(icpc_ids)

    session = init_database()
    ac_teams = session.query(ACTeamRecord).all()
    print(ac_teams)
    local_ids = [team.team_id for team in ac_teams]
    local_ids = set(local_ids)

    print(icpc_ids - local_ids)
    print(local_ids - icpc_ids)

