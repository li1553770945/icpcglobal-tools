import requests
import configparser
from domain import Team, Person

with open("token.txt","r") as f:
    token = f.read()


def get_team(team_id):
    team_info_url = f"https://icpc.global/api/team/{team_id}"
    team_members_url = f"https://icpc.global/api/team/members/team/{team_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(team_info_url, headers=headers)
    response = response.json()
    team_name = response['name']

    members = requests.get(team_members_url, headers=headers).json()
    coach = None
    contestants = list()
    for member in members:
        if member['role'] == 'CONTESTANT':
            contestants.append(Person(member['name'], member['name'], member['email']))
        elif member['role'] == 'COACH':
            coach = Person(member['name'], member['name'], member['email'])

    team = Team("",team_name, team_name, team_id, contestants, coach)
    team.status = response['status']
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

if __name__ == "__main__":
    team = get_team("914160")

    print(f"{team.name},{team.status},{team.coach.name},{team.contestants[0].name},{team.contestants[1].name},{team.contestants[2].name}")
