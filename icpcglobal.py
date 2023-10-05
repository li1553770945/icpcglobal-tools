import requests
import configparser
from domain import Team, Person
from constant import *
with open("token.txt","r") as f:
    token = f.read()


def get_team(team_id):

    team_info_url = f"https://icpc.global/api/team/{team_id}"
    team_members_url = f"https://icpc.global/api/team/members/team/{team_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(team_info_url, headers=headers)
    try:
        response = response.json()
        team_name = response['name']
        contest_id = response['contest']['id']
        contest_name = response['contest']['name']
    except Exception as err:
        print(f"获取队伍{team_id}信息失败,status_code:{response.status_code},text:{response.text},error:{err}")
        return None
    try:
        members = requests.get(team_members_url, headers=headers).json()
    except Exception as err:
        print(f"获取队伍{team_id}成员失败,status_code:{response.status_code},text:{response.text},error:{err}")
        return None
    coach = None
    contestants = list()
    cocoach = list()
    for member in members:
        if member['role'] == 'CONTESTANT':
            contestants.append(Person(member['name'], member['name'], member['email']))
        elif member['role'] == 'COACH':
            coach = Person(member['name'], member['name'], member['email'])
        elif member['role'] == 'COCOACH':
            cocoach.append(Person(member['name'],member['name'],member['email']))

    team = Team("",team_name, team_name, team_id, contestants, coach)
    team.status = response['status']
    team.contest_id = contest_id
    team.contest_name = contest_name
    team.cocoach = cocoach
    return team


def test_token():
    url = "https://icpc.global/api/person/info/basic"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(url,headers=headers)
        response = response.json()
        name = f"{response['firstName']} {response['lastName']}"
        print(f"欢迎{name}")
        return True
    except:
        return False


def set_ac(team_id):
    url = f"https://icpc.global/api/team/{team_id}/accept"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(f"设置{team_id} AC失败:{response.status_code},{response.text}")
        return False


def get_all_ac_team():
    url = "https://icpc.global/api/team/search/7696/all?q=proj:teamId,rank,site,team,country,institution,coachName,status,action%3Bfilter:status%23ACCEPTED%3B&page=1&size=1000"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    teams = response.json()
    with open("acs.csv","w") as f:
        for team in teams:
            f.write(f"{team['team']['id']}")


def get_contest_name():
    url = f"https://icpc.global/api/contest/{CONTEST_ID}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers).json()
    return response['name']

if __name__ == "__main__":
    # team = get_team("904992")
    get_all_ac_team()
    # print(f"{team.name},{team.status},{team.coach.name},{team.contestants[0].name},{team.contestants[1].name},{team.contestants[2].name}")
