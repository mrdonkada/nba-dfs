#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import MySQLdb
import datetime
import re
import json

def datestring(dt):

    year = dt.year
    month = dt.month
    day = dt.day

    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)

    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)

    datestr = str(year) + '-' + month + '-' + day
    dayid = str(year) + month + day

    dates = [datestr, dayid]

    return dates

def getplayerdata():

    r = requests.get("http://www.numberfire.com/nba/fantasy/full-fantasy-basketball-projections").text
    soup = BeautifulSoup(r)

    projData = soup.find_all("script", {"type" : "text/javascript"})

    projData = projData[2]


    reg = re.search('var NF_DATA.*', str(projData))

    reg = reg.group()[13:-2]

    projData = json.loads(reg)

    dailyProj = projData['daily_projections']
    teams = projData['teams']
    players = projData['players']

    print teams.keys()
    print players.keys()



    for player in dailyProj:
        player['last_name'] = players[player['nba_player_id']]['last_name']
        player['first_name'] = players[player['nba_player_id']]['first_name']
        player['name'] = players[player['nba_player_id']]['name']
        player['position'] = players[player['nba_player_id']]['position']
        player['team'] = teams[player['nba_team_id']]['abbrev']
        player['opp'] = teams[player['opponent_id']]['abbrev']

    print dailyProj[0]
    print dailyProj[0].keys()

    return dailyProj

def addtoDb(con, dates, playerlist):

    query = "DELETE FROM numberfire_proj WHERE day_id = %s" % (dates[1])
    x = con.cursor()
    x.execute(query)

    for i in playerlist:
        with con:
            query = "INSERT INTO numberfire_proj (day, day_id, season_id, game_id, player_id, playernm_last, playernm_first, \
                                            playernm_full, team, pos, opp, minutes, pts, fgm, \
                                            fga, ftm, fta, fg3m, fg3a, oreb, dreb, \
                                            reb, ast, stl, blk, tov, nerd, efg, \
                                            usg, drtg, game_start, game_play_prob, fd_sal, dk_sal, yahoo_sal, \
                                            fdp, dkp, yhp, fd_ratio, dk_ratio, yahoo_ratio) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (dates[0], dates[1], i['season'], i['nba_game_id'], i['nba_player_id'], i['last_name'], i['first_name'], \
                i['name'], i['team'], i['position'], i['opp'], i['minutes'], i['pts'], i['fgm'], \
                i['fga'], i['ftm'], i['fta'], i['p3m'], i['p3a'], i['oreb'], i['dreb'], \
                i['treb'], i['ast'], i['stl'], i['blk'], i['tov'], i['nerd'], i['efg'], \
                i['usg'], i['drtg'], i['game_start'], i['game_play_probability'], i['fanduel_salary'], i['draft_kings_salary'], i['yahoo_salary'], \
                i['fanduel_fp'], i['draft_kings_fp'], i['yahoo_fp'], i['fanduel_ratio'], i['draft_kings_ratio'], i['yahoo_ratio'])
            x = con.cursor()
            x.execute(query)

    return

def main():

    con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nba')
    today = datetime.date.today()
    dates = datestring(today)
    
    addtoDb(con, dates, getplayerdata())
    # getplayerdata()

    return

if __name__ == '__main__':
    main()