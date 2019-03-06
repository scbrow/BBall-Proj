import requests
import json
import re


def populate():
    games = {}
    req = requests.get("https://data.nba.com/data/5s/v2015/json/mobile_teams/nba/2018/scores/00_todays_scores.json")
    file = json.loads(req.text)
    for a in file["gs"]["g"]:
        games.update({a["v"]["ta"]: a["gid"]})
    return games


def score(gameid):
    result = []
    req = requests.get("https://data.nba.com/data/5s/v2015/json/mobile_teams/nba/2018/scores/00_todays_scores.json")
    file = json.loads(req.text)
    for a in file["gs"]["g"]:
        if a["gid"] == gameid:
            result.append(float(a["v"]["s"]) + float(a["h"]["s"]))
            result.append(float(a["v"]["s"]))
            result.append(float(a["h"]["s"]))
            break
    return result


def time(gameid):
    result = 0
    req = requests.get("https://data.nba.com/data/5s/v2015/json/mobile_teams/nba/2018/scores/00_todays_scores.json")
    file = json.loads(req.text)
    for a in file["gs"]["g"]:
        if a["gid"] == gameid:
            try:
                remain_time = float(a["cl"].split(':')[0]) + float(a["cl"].split(':')[1]) / 60
                quart = float(re.search(r'\d+', a["stt"]).group())
                result = (4 - float(quart))*12 + remain_time
            except AttributeError:
                result = float(24)
            break
    return result


def poss(gameid):
    req = requests.get("https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2018/scores/gamedetail/"
                       + gameid + "_gamedetail.json")
    file = json.loads(req.text)
    tFGA = float(file["g"]["vls"]["tstsg"]["fga"])
    tFTA = float(file["g"]["vls"]["tstsg"]["fta"])
    tORB = float(file["g"]["vls"]["tstsg"]["oreb"])
    tDRB = float(file["g"]["vls"]["tstsg"]["dreb"])
    tFG = float(file["g"]["vls"]["tstsg"]["fgm"])
    tTO = float(file["g"]["vls"]["tstsg"]["tov"])
    oFGA = float(file["g"]["hls"]["tstsg"]["fga"])
    oFTA = float(file["g"]["hls"]["tstsg"]["fta"])
    oORB = float(file["g"]["hls"]["tstsg"]["oreb"])
    oDRB = float(file["g"]["hls"]["tstsg"]["dreb"])
    oFG = float(file["g"]["hls"]["tstsg"]["fgm"])
    oTO = float(file["g"]["hls"]["tstsg"]["tov"])

    result = 0.5 * ((tFGA + 0.4 * tFTA - 1.07 * (tORB / (tORB + oDRB)) * (tFGA - tFG) + tTO)
                    + (oFGA + 0.4 * oFTA - 1.07 * (oORB / (oORB + tDRB)) * (oFGA - oFG) + oTO))
    return result


def ortg(team1, team2):
    result = []
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 '
            'Safari/537.36'}
    req = requests.get("https://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division"
                       "=&GameScope=&GameSegment=&LastNGames=5&LeagueID=00&Location=&MeasureType=Advanced&Month=0"
                       "&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience"
                       "=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2018-19&SeasonSegment=&SeasonType=Regular+Season"
                       "&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=", headers=headers)
    file = json.loads(req.text)
    rating1 = file['resultSets'][0]['rowSet'][team1][8]
    rating2 = file['resultSets'][0]['rowSet'][team2][8]
    result.append(float(rating1)/100)
    result.append(float(rating2)/100)
    return result
