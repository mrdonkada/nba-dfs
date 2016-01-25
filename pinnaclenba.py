#!/usr/local/bin/python2.7

import requests
import MySQLdb
import csv
from bs4 import BeautifulSoup
import datetime



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
    
def getData(dates):
    
    r = requests.get("http://www.pinnaclesports.com/webapi/1.14/api/v1/GuestLines/NonLive/4/487").json()
    # League ID 487, SportID = 4 (NBA)
    
    events = r['Leagues'][0]['Events']
    game = []
    gameList = []
    for event in events:

        if event['Totals'] and event['PeriodNumber'] == 0:      ### Only get Full Game Line (fix this later!)
            total = float(event['Totals']['Min'])               ### Game Total
            gamedate = event['DateAndTime'][:10]
            gametime = event['DateAndTime'][11:-1]        
            game.append(event['EventId'])                       # Event ID
            game.append(gamedate)                               # Game Date
            game.append(gametime)                               # Game Time
            game.append(event['Totals']['Min'])
            game.append(event['Totals']['OverPrice'])
            game.append(event['Totals']['UnderPrice'])
            
            # print '\neventID:', event['EventId']                        # Game ID
            # print 'date:', gamedate
            # print 'time:', gametime
            # print 'total:', total
            # print 'Over Price:', event['Totals']['OverPrice']    # Over Odds
            # print 'Under Price:', event['Totals']['UnderPrice']  # Under Odds
            
        
            for participants in event['Participants']:
                spread = float(participants['Handicap']['Min'])
                teamTotal = ((total/2)-(spread/2))
                game.append(participants['Name'])
                game.append(participants['MoneyLine'])
                game.append(participants['Handicap']['Min'])
                game.append(participants['Handicap']['Price'])
                game.append(teamTotal)
                # print 'Team:', participants['Name']                  # Team
                # print 'ML:', participants['MoneyLine']               # Moneyline
                # print 'Spread:', participants['Handicap']['Min']     # Spread
                # print 'Odds:', participants['Handicap']['Price']     # Spread Odds
                # print 'Team Total:', teamTotal                     # Team Total
            if dates[0] == game[1]:
                gameList.append(game)
        game = []
    return gameList


def homeawaySplit(gameList, consensus):
    
    headers = ['HomeAway', 'game_id', 'date', 'time', 'total', 'team', 'ml', 'spread', 'odds', 'team_total', \
    'opp', 'opp_ml', 'opp_spread', 'opp_odds', 'opp_total', 'over_price', 'under_price']
    
    aworder = [0,1,2,3,6,7,8,9,10,11,12,13,14,15,4,5]
    hmorder = [0,1,2,3,11,12,13,14,15,6,7,8,9,10,4,5]

    holder = []
    gameinfo = []
    teamlist = []
    gameDict = {}

    for game in gameList:
        holder = [game[i] for i in hmorder]  # List method to put items into home team order
        holder.insert(0, 'Home')             # Add 'Home' to home teams
        gameinfo.append(holder)
        holder = [game[i] for i in aworder]  # List method to put items into away team order
        holder.insert(0, 'Away')             # Add 'Away' to away teams
        gameinfo.append(holder)
    

    for team in gameinfo:
        for header in headers:
            gameDict[header] = team[headers.index(header)]
        teamlist.append(gameDict)
        gameDict = {}
    
    #### Add consensus % to list
    for team in teamlist:
        if team['team'] not in consensus.keys():
            team['consensus'] = ''
        else:
            team['consensus'] = consensus[team['team']]
    
    return teamlist
    
def consensus():
    
    game = []
    gameList = []
    r = requests.get("http://www.oddsshark.com/nba/consensus-picks").text

    soup = BeautifulSoup(r)

    data = soup.find('table', {'class': 'consensus-table'})
    
    for rows in data.find_all('tr')[1:-1]:
        if 'class' in rows.attrs.keys() and 'favoured' in rows.attrs['class']:
            game.append('consensus')
        for items in rows.find_all('td'):
            if len(items.text.strip()) > 0:
                game.append(items.text.strip())

    gameList = [game[i:i+10] for i in range(0, len(game), 10)]
    
    bet_pct = {}
    for game in gameList:
        if game[0] == 'consensus':
            pct = float(game[1][:-1])/100
            bet_pct[game[3].split(' ', 1)[1]] = round(pct,2)
            bet_pct[game[6].split(' ', 1)[1]] = round(1-pct,2)
            # print game[3], pct, game[6], 1-pct
        else:
            pct = float(game[0][:-1])/100
            bet_pct[game[2].split(' ', 1)[1]] = round(1-pct,2)
            # print game[2], ":", game[6]
            # print pct
            bet_pct[game[6].split(' ', 1)[1]] = round(pct,2)
            # print game[2], 1-pct, game[6], pct

    return bet_pct
    
    
def linemovement(con, gameinfo, dates):
    # See if there is data in the table - if there is not, they are opening lines
    
    changes = ['total_chg', 'team_total_chg', 'opp_total_chg', 'spread_chg']
    
    with con:

    # bring in past results
        cur = con.cursor()
        cur.execute("SELECT * FROM pinnacle_odds WHERE day = %s" % (dates[0]))

        rows = cur.fetchall()
        if len(rows) > 0:
            firstPull = False
        else:
            firstPull = True
    
    # If this is the first run, insert in placeholders and make the opening lines set to the current lines
    if firstPull:
        for game in gameinfo:
            for i in changes:
                game[i] = 0.00
            game['total_open'] = game['total']
            game['team_total_open'] = game['team_total']
            game['opp_total_open'] = game['opp_total']
            game['spread_open'] = game['spread']
            
    # If this isn't the first run, calculate the change and insert into the list
    else:
        holder = []
        pastresults = []
        for row in rows:
            for item in row[1:]:            # All items except primary key ID
                holder.append(item)
            pastresults.append(holder)
            holder = []
        print "\n\n", pastresults, "\n\n"
                
        for past in pastresults:
            for game in gameinfo:
                if past[5] == game['team'] and past[6] == game['opp']:
                    game['total_chg'] = float(past[19]) - float(game['total'])
                    game['team_total_chg'] = float(past[20]) - float(game['team_total'])
                    game['opp_total_chg'] = float(past[21]) - float(game['opp_total'])
                    game['spread_chg'] = float(past[22]) - float(game['spread'])
        
    return gameinfo
    
def addtoDb(con, dates, gamelist):

    query = "DELETE FROM pinnacle_odds WHERE day_id = %s" % (dates[1])
    x = con.cursor()
    x.execute(query)

    for i in gamelist:
        with con:
            query = "INSERT INTO pinnacle_odds (day, day_id, game_id, time, home_away, team, opp, team_total, \
                                            opp_total, total, ml, spread, odds, consensus, opp_ml, \
                                            opp_spread, opp_odds, over_price, under_price, total_open, team_total_open, opp_total_open, \
                                            spread_open, total_chg, team_total_chg, opp_total_chg, spread_chg) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (i['date'], dates[1], i['game_id'], i['time'], i['HomeAway'], i['team'], i['opp'], i['team_total'], \
                 i['opp_total'], i['total'], i['ml'], i['spread'], i['odds'], i['consensus'], i['opp_ml'], \
                 i['opp_spread'], i['opp_odds'], i['over_price'], i['under_price'], i['total_open'], i['team_total_open'], i['opp_total_open'], \
                 i['spread_open'], i['total_chg'], i['team_total_chg'], i['opp_total_chg'], i['spread_chg'])
            x = con.cursor()
            x.execute(query)
    
    print dates[0], "complete"
    
    return

def main():
    
    local = False

    if local == False:
        fldr = 'nba-dfs/'
        con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nba')
            
    else:
        fldr = ''
        con = MySQLdb.connect('localhost', 'root', '', 'dfs-nba')            #### Localhost connection

    today = datetime.date.today()
    dates = datestring(today)
    
    gameList = linemovement(con, homeawaySplit(getData(dates), consensus()), dates)
    addtoDb(con, dates, gameList)
    
    
if __name__ == '__main__':
    main()