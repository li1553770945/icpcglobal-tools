import requests
import urllib3
from sqlalchemy.dialects.postgresql.psycopg import logger

from utils.domain import Team, Person
from data.constant import *
from utils.logger import setup_logger

import yaml  # Import the yaml module

logger = setup_logger()
# Load the YAML configuration file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Access configuration data
http_proxy = config['network']['http_proxy']
https_proxy = config['network']['https_proxy']

proxies = {
    'http': http_proxy,   # 替换为你的HTTP代理地址
    'https': https_proxy, # 替换为你的HTTPS代理地址
}

with open("data/token.txt", "r") as f:
    token = f.read()

MAX_RETRY = 5

def get_team(team_id):

    team_info_url = f"https://icpc.global/api/team/{team_id}"
    team_members_url = f"https://icpc.global/api/team/members/team/{team_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    for i in range(MAX_RETRY):
        try:
            response = requests.get(team_info_url, headers=headers, proxies=proxies)
            break
        except Exception as err:
            logger.error(
                f"获取队伍{team_id}信息失败,网络连接错误,error:{err}")
            if i == MAX_RETRY - 1:
                return None
    try:
        if response.status_code != 200:
            logger.error(f"获取队伍{team_id}信息失败,status_code:{response.status_code},text:{response.text}")
            return None
        response = response.json()

        team_name = response['name']
        contest_id = response['contest']['id']
        contest_name = response['contest']['name']
    except Exception as err:
        logger.error(f"获取队伍{team_id}信息失败,status_code:{response.status_code},text:{response.text},error:{err}")
        return None
    for i in range(0,MAX_RETRY):
        try:
            members = requests.get(team_members_url, headers=headers,proxies=proxies).json()
            break
        except Exception as err:
            logger.error(f"获取队伍{team_id}成员失败,response:{members},error:{err}")
            if i == MAX_RETRY - 1:
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
        response = requests.get(url,headers=headers,proxies=proxies)
        response = response.json()
        name = f"{response['firstName']} {response['lastName']}"
        logger.info(f"欢迎{name}")
        return True
    except:
        return False


def set_ac(team_id):
    url = f"https://icpc.global/api/team/{team_id}/accept"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(url, headers=headers,proxies=proxies)
    if response.status_code == 200:
        return True
    else:
        logger.error(f"设置{team_id} AC失败:{response.status_code},{response.text}")
        return False


def get_all_ac_team():
    url = f"https://icpc.global/api/team/search/{CONTEST_ID}/all?q=proj:teamId,rank,site,team,country,institution,coachName,status,action%3Bfilter:status%23ACCEPTED%3B&page=1&size=1000"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers,proxies=proxies)
    teams = response.json()
    return teams
    # with open("acs.csv","w") as f:
    #     for team in teams:
    #         f.write(f"{team['team']['id']}\n")


def get_contest_name():
    url = f"https://icpc.global/api/contest/{CONTEST_ID}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers,proxies=proxies).json()
    return response['name']

if __name__ == "__main__":
    # team = get_team("904992")
    get_all_ac_team()
    # logger.info(f"{team.name},{team.status},{team.coach.name},{team.contestants[0].name},{team.contestants[1].name},{team.contestants[2].name}")
