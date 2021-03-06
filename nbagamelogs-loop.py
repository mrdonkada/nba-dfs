#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import MySQLdb
import datetime
import re
import json


def playergamedata():
    r = requests.get("http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=2015-16&SeasonType=Regular+Season&Sorter=PTS").json()

    headers = r['resultSets'][0]['headers']
    gameset = r['resultSets'][0]['rowSet']

    gamelist = []
    for games in gameset:
        playerdict = {}
        for i in headers:
            playerdict[i] = games[headers.index(i)]
        gamelist.append(playerdict)
        playerdict = {}

    return gamelist

def addtoDb(gamelist, datestr, con):
    
    headers = ["SEASON_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "TEAM_NAME", "GAME_ID", "MATCHUP", \
    "WL", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", \
    "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "PLUS_MINUS"]
    
    ### other available headers: 'VIDEO_AVAILABLE', 'PLAYER_ID', 'GAME_DATE'
    
    playerdict = {}
    playerdict[datestr] = {}
    for i in gamelist:
        if i['GAME_DATE'] == datestr:
            playerid = i['PLAYER_ID']
            playerdict[datestr][playerid] = {}
            for header in headers:
                playerdict[datestr][playerid][header] = i[header]
            
    query = "DELETE FROM nba_gamelog WHERE day = %s" % (datestr)
    x = con.cursor()
    x.execute(query)

    for key in playerdict[datestr].keys():
        with con:
            query = "INSERT INTO nba_gamelog (day, season_id, player_id, playernm_full, team_abbr, team, game_id, matchup, \
                    wl, min, fgm, fga, fg_pct, fg3m, fg3a, \
                    fg3_pct, ftm, fta, ft_pct, oreb, dreb, reb, \
                    ast, stl, blk, tov, pf, pts, plus_minus) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (datestr, playerdict[datestr][key]['SEASON_ID'], key, playerdict[datestr][key]['PLAYER_NAME'], playerdict[datestr][key]['TEAM_ABBREVIATION'], playerdict[datestr][key]['TEAM_NAME'], playerdict[datestr][key]['GAME_ID'], playerdict[datestr][key]['MATCHUP'], \
                playerdict[datestr][key]['WL'], playerdict[datestr][key]['MIN'], playerdict[datestr][key]['FGM'], playerdict[datestr][key]['FGA'], playerdict[datestr][key]['FG_PCT'], playerdict[datestr][key]['FG3M'], playerdict[datestr][key]['FG3A'], \
                playerdict[datestr][key]['FG3_PCT'], playerdict[datestr][key]['FTM'], playerdict[datestr][key]['FTA'], playerdict[datestr][key]['FT_PCT'], playerdict[datestr][key]['OREB'], playerdict[datestr][key]['DREB'], playerdict[datestr][key]['REB'], \
                playerdict[datestr][key]['AST'], playerdict[datestr][key]['STL'], playerdict[datestr][key]['BLK'], playerdict[datestr][key]['TOV'], playerdict[datestr][key]['PF'], playerdict[datestr][key]['PTS'], playerdict[datestr][key]['PLUS_MINUS'])
            x = con.cursor()
            x.execute(query)
            
    return playerdict

def security(site,fldr):
    
    info = []
    myfile = fldr + 'myinfo.txt'

    siteDict = {}
    with open(myfile) as f:
        g = f.read().splitlines()
        for row in g:
            newlist = row.split(' ')
            siteDict[newlist[0]] = {}
            siteDict[newlist[0]]['username'] = newlist[1]
            siteDict[newlist[0]]['password'] = newlist[2]
                
    info = [siteDict[site]['username'],siteDict[site]['password']]
    
    return info
    
def main():
    
    datelist = []
    
    local = False

    if local == False:
        fldr = 'nba-dfs/'
        serverinfo = security('mysql', fldr)
        con = MySQLdb.connect(host='mysql.server', user=serverinfo[0], passwd=serverinfo[1], db='MurrDogg4$dfs-nba')
                    
    else:
        fldr = ''
        con = MySQLdb.connect('localhost', 'root', '', 'dfs-nba')            #### Localhost connection
    
    year = 2015
    for i in range(10,13):
        for x in range(1,32):
            if i < 10:
                month = '0' + str(i)
            else:
                month = str(i)
            if x < 10:
                day = '0' + str(x)
            else:
                day = str(x)
                
            datestr = str(year) + "-" + month + "-" + day
            datelist.append(datestr)
    
    for dates in datelist:
        addtoDb(playergamedata(), dates, con)
        print dates, "complete"
    
if __name__ == '__main__':
    main()