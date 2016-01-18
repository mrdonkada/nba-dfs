#!/usr/local/bin/python2.7

import requests
import csv
import datetime
import MySQLdb


#####
#
#   To Do: add FD, DK, Yahoo points columns to database
#   Switch to CSV_v2 file, which includes player IDs for each site
#
#####

# Downloads the file into a csv
# with open('2013-0.csv', 'wb') as ofile:
#     for chunk in r.iter_content(chunk_size=1024):
#         ofile.write(chunk)
#         ofile.flush()

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

    cookies = {'ASP.NET_SessionId': '0dcma2pabd0tqdpwfseac5ij', 'RotoMonsterUserId': 'OQFkRaBrhi18wC9M7v4lsAi7q3Krk3Nusr/mW3b/s/g='}
    r = requests.get(
        url=('https://basketballmonster.com/Daily.aspx?exportcsv=6ldEjuwAcaR0fcSRnjvuxci[@]mg4Kol[@]fkswLqTAzm/c='),
        cookies=cookies)

    playerdata = r.text.split('\r\n')[:-1]          # Last item is blank list
    # print test
    playerlist = []
    for line in playerdata:
        # print line, "\n"
        player = line.split(',')
        playerlist.append(player)

    headers = playerlist.pop(0)

    ## ['id', 'last_name', 'first_name', 'team', 'position', 'opponent', 'minutes', 'points', 'threes', 'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 'twos', 'free throws', 'free_throws_missed', 'field goals', 'field_goals_missed', 'double doubles', 'triple doubles', 'price_fanduel', 'price_yahoo', 'price_draftkings', 'price_draftday', 'price_starstreet', 'price_fantasyfeud', 'price_fanthrowdown', 'price_starfantasyleagues', 'price_fantasyaces', 'positions_fanduel', 'positions_yahoo', 'positions_draftkings', 'positions_draftday', 'positions_starstreet', 'positions_fantasyfeud', 'positions_fanthrowdown', 'positions_starfantasyleagues', 'positions_fantasyaces']

    players = []

    for player in playerlist:
        playerdict = {}
        for i in headers:
            playerdict[i] = player[headers.index(i)]
        players.append(playerdict)
        playerdict = {}

    return players

def fantasyValues(player):

    categories = ['points', 'rebounds', 'assists', 'blocks', 'steals', 'turnovers', 'threes', 'double doubles', 'triple doubles']
    print player
    for i in categories:
        if player[i] == '':
            player[i] = 0.00

    fdp = float(player['points']) + float(player['rebounds']) * 1.2 + float(player['assists']) * 1.5 + float(player['blocks']) * 2 + float(player['steals']) * 2 + (float(player['turnovers']) * -1)
    dkp = float(player['points']) + float(player['rebounds']) * 1.25 + float(player['assists']) * 1.5 + float(player['blocks']) * 2 + float(player['steals']) * 2 + (float(player['turnovers']) * -0.5) + float(player['threes']) * 0.5 + float(player['double doubles']) * 1.5 + float(player['triple doubles']) * 3
    yhp = float(player['points']) + float(player['rebounds']) * 1.2 + float(player['assists']) * 1.5 + float(player['blocks']) * 2 + float(player['steals']) * 2 + (float(player['turnovers']) * -1) + float(player['threes']) * 0.5

    fpts = {'fdp': fdp, 'dkp': dkp, 'yhp': yhp}

    return fpts

def addtoDb(con, dates, playerlist):

    query = "DELETE FROM bbmon_proj WHERE day_id = %s" % (dates[1])
    x = con.cursor()
    x.execute(query)

    for i in playerlist:
        season = '2016'
        fpts = fantasyValues(i)
        with con:
            query = "INSERT INTO bbmon_proj (day, day_id, player_id, playernm_last, playernm_first, team, pos, opp, \
                                            minutes, pts, fg3m, reb, ast, stl, blk, \
                                            tov, fg2m, ftm, ft_miss, fgm, fg_miss, dbl_dbl, \
                                            tpl_dbl, fd_sal, yahoo_sal, dk_sal, fd_pos, yahoo_pos, dk_pos, fdp, dkp, yhp, season) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (dates[0], dates[1], i['id'], i['last_name'], i['first_name'], i['team'], i['position'], i['opponent'], \
                 i['minutes'], i['points'], i['threes'], i['rebounds'], i['assists'], i['steals'], i['blocks'], \
                 i['turnovers'], i['twos'], i['free throws'], i['free_throws_missed'], i['field goals'], i['field_goals_missed'], i['double doubles'], \
                 i['triple doubles'], i['price_fanduel'], i['price_yahoo'], i['price_draftkings'], i['positions_fanduel'], i['positions_yahoo'], i['positions_draftkings'], fpts['fdp'], fpts['dkp'], fpts['yhp'], season)
            x = con.cursor()
            x.execute(query)

    return

def main():

    con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nba')
    today = datetime.date.today()
    dates = datestring(today)

    addtoDb(con, dates, getplayerdata())

    return

if __name__ == '__main__':
    main()