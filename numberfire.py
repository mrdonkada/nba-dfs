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

    print dailyProj[0].keys()
    print teams.keys()
    print players.keys()
    print teams
    print players


    for player in dailyProj:
        player['last_name'] = players[player['nba_player_id']]['last_name']
        player['first_name'] = players[player['nba_player_id']]['first_name']
        player['name'] = players[player['nba_player_id']]['name']
        player['position'] = players[player['nba_player_id']]['position']

    print dailyProj[0]

    return dailyProj

def addtoDb(con, dates, playerlist):

    query = "DELETE FROM numberfire_proj WHERE day_id = %s" % (dates[1])
    x = con.cursor()
    x.execute(query)

    for i in playerlist:
        with con:
            query = "INSERT INTO bbmon_proj (day, day_id, player_id, playernm_last, playernm_first, team, pos, opp, \
                                            minutes, pts, fg3m, reb, ast, stl, blk, \
                                            tov, fg2m, ftm, ft_miss, fgm, fg_miss, dbl_dbl, \
                                            tpl_dbl, fd_sal, yahoo_sal, dk_sal, fd_pos, yahoo_pos, dk_pos) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (dates[0], dates[1], )
            x = con.cursor()
            x.execute(query)

    return

def main():

    # con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nba')
    today = datetime.date.today()
    dates = datestring(today)
    getplayerdata()

    return

if __name__ == '__main__':
    main()