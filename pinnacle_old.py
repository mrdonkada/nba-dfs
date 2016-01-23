#!/usr/local/bin/python2.7

import requests
import MySQLdb
import csv
from bs4 import BeautifulSoup
import datetime


def getweek():
    
    today = datetime.date.today()
    week1 = datetime.date(2015, 9, 8)       #### Tuesday of Week 1
    datedict = {}
    
    for i in range(1,18):
        datedict[i] = week1 + datetime.timedelta(days=7*(i-1))      #### Week Starting Tuesday
    
    for key in datedict.keys():
        if today >= datedict[key] and today < datedict[key + 1]:
            weekNum = key
            
    return weekNum

def consensus(fldr):

    # Bring in team list    
    teamlist = []
    with open(fldr + 'team_list.csv', 'rU') as f:
        w = csv.DictReader(f)
        for row in w:
            teamlist.append(row)
    
    #### Scrape oddsshark 
    r = requests.get("http://www.oddsshark.com/nfl/consensus-picks").text

    soup = BeautifulSoup(r)

    data = soup.find('table', {'class': 'base-table'})

    games = data.find_all('tr')

    gameset = []

    for rows in games[1:]:
        temp = []
        for item in rows.find_all('td'):
            if '@' in item.text:
                consensus = item.find('span', {'class': 'highlighted'}).text.strip()
                temp.append(consensus)
                teams = item.text.strip().split('@')
                for team in teams:
                    temp.append(team.strip())
            elif '%' in item.text:
                pct = int(item.text[:-1])/100.0
                temp.append(pct)
            else:
                temp.append(item.text.strip())
        gameset.append(temp)
        temp = []

    betlist = []
    for game in gameset:
        gamedict = {}
        if game[0] == game[1]:
            gamedict['team'] = game[1]
            gamedict['opp'] = game[2]
            gamedict['spread'] = float(game[3])
            gamedict['consensus'] = round(game[4], 2)
            betlist.append(gamedict)
            gamedict = {}
            gamedict['team'] = game[2]
            gamedict['opp'] = game[1]
            gamedict['spread'] = -float(game[3])
            gamedict['consensus'] = round(1.0 - game[4], 2)
            betlist.append(gamedict)
        else:
            gamedict['team'] = game[2]
            gamedict['opp'] = game[1]
            gamedict['spread'] = float(game[3])
            gamedict['consensus'] = round(game[4], 2)
            betlist.append(gamedict)
            gamedict = {}
            gamedict['team'] = game[1]
            gamedict['opp'] = game[2]
            gamedict['spread'] = -float(game[3])
            gamedict['consensus'] = round(1.0 - game[4], 2)
            betlist.append(gamedict)
    
    ##### Change team name to fit pinnacle
    for line in betlist:
        for team in teamlist:
            if line['team'] == team['oddsshark_team']:
                line['team'] = team['pinnacle_team']
    
    return betlist

def getData():
    
    r = requests.get("http://www.pinnaclesports.com/webapi/1.14/api/v1/GuestLines/NonLive/4/487").json()
    # League ID 487, SportID = 4 (NBA)
    
    events = r["Leagues"][0]["Events"]
    game = []
    gameList = []
    for event in events:

        if event['Totals'] and event['PeriodNumber'] == 0:      ### Only get Full Game Line (fix this later!)
            total = float(event['Totals']['Min'])
        
            print '\n', event['EventId']
            print 'Over Price', event['Totals']['OverPrice']
            print 'Under Price', event['Totals']['UnderPrice']
            print 'Total', event['Totals']['Min']

            gamedate = event['DateAndTime'][:10]
            gametime = event['DateAndTime'][11:-1]        
            game.append(event['EventId'])
            game.append(gamedate)
            game.append(gametime)
            game.append(event['Totals']['OverPrice'])
            game.append(event['Totals']['UnderPrice'])
            game.append(event['Totals']['Min'])
        
        
            for participants in event['Participants']:
                spread = float(participants['Handicap']['Min'])
                teamTotal = ((total/2)-(spread/2))
                game.append(participants['Name'])
                game.append(participants['MoneyLine'])
                game.append(participants['Handicap']['Min'])
                game.append(participants['Handicap']['Price'])
                game.append(teamTotal)
                print 'Name', participants['Name']
                print 'ML', participants['MoneyLine']
                print 'Spread', participants['Handicap']['Min']
                print 'Odds', participants['Handicap']['Price']
                print teamTotal
            gameList.append(game)
            print game
        game = []
    return gameList


def homeawaySplit(gameList, weekNum):
    
    hmorder = [11,6,12,13,14,15,7,8,9,10,3,4,5,0,1,2]
    aworder = [6,11,7,8,9,10,12,13,14,15,3,4,5,0,1,2]


    holder = []
    gameinfo = []

    for game in gameList:
        holder = [game[i] for i in hmorder]  # List method to put items into home team order
        holder.insert(0, weekNum)
        holder.insert(3, 'Home')             # Add 'Home' to home teams
        gameinfo.append(holder)
        holder = [game[i] for i in aworder]  # List method to put items into away team order
        holder.insert(0, weekNum)
        holder.insert(3, 'Away')             # Add 'Away' to away teams
        print holder
        gameinfo.append(holder)
    
    return gameinfo

def linemovement(con, gameinfo, betlist, weekNum):
    # See if there is data in the table - if there is not, they are opening lines
    with con:

    # bring in past results
        cur = con.cursor()
        cur.execute("SELECT * FROM pinnacle_odds WHERE week = %d" % (weekNum))

        rows = cur.fetchall()
        if len(rows) > 0:
            firstPull = False
        else:
            firstPull = True
    
    # If this is the first run, insert in placeholders and make the opening lines set to the current lines
    if firstPull:
        for game in gameinfo:
            for i in range(0,7):
                game.insert(15, 0.00)
            game[15] = game[7] 
            game[16] = game[5]
            game[17] = game[14]
            for team in betlist:
                if game[1] == team['team']:
                    game[21] = team['consensus']

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
        
        for game in gameinfo:
            for i in range(0,7):
                game.insert(15, 0.00)
            for team in betlist:
                if game[1] == team['team']:
                    game[21] = team['consensus']
                
        for past in pastresults:
            for game in gameinfo:
                if past[1] == game[1] and past[2] == game[2]:
                    print past
                    # game[15] = past[16]      # teamtotal_open
                    # game[16] = past[17]      # spread_open
                    # game[17] = past[18]      # total_open
                    for i in range(4,15):       # replace with new odds
                        past[i] = game[i]
                    past[18] = float(game[7]) - float(past[15])      # teamtotal_chg
                    past[19] = float(game[5]) - float(past[16])      # spread_chg
                    past[20] = float(game[14]) - float(past[17])      # total_chg
                    past[21] = game[21]
        gameinfo = pastresults
        
    return gameinfo

def addtoDb(con, gameinfo, weekNum):          ####### Add to database

    query = "DELETE FROM pinnacle_odds WHERE week = %d" % (weekNum)
    x = con.cursor()
    x.execute(query)

    for row in gameinfo:
        print row
        with con:
            query = "INSERT INTO pinnacle_odds (week, team, opp, home_away, ml, spread, odds, teamtotal, \
                    opp_ml, opp_spread, opp_odds, opp_total, over_price, under_price, total, teamtotal_open, \
                    spread_open, total_open, teamtotal_chg, spread_chg, total_chg, consensus, game_id, gamedate, gametime) \
                    VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                            "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], \
                row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], \
                row[19], row[20], row[21], row[22], row[23], row[24])
            x = con.cursor()
            x.execute(query)
    return

def main():
    
    local = False
    if local == False:
        fldr = 'nfl-dfs/'
    else:
        fldr = ''
    betlist = consensus(fldr)
    print betlist
    headers = ['team', 'opp', 'home_away', 'team_ml', 'team_spread', 'team_odds', 'team_total', 'opp_ml', 'opp_spread' \
                'opp_odds', 'opp_total', 'overprice', 'underprice', 'total', 'gamedate', 'gametime']

    ##### Get week number
    # f = open(fldr + 'weekinfo.txt', 'r')
    # # f = open('weekinfo.txt', 'r')             ### Local
    # ftext = f.read().split(',')
    # weekNum = int(ftext[0])
    weekNum = getweek()
    
    if local == True:
        con = MySQLdb.connect('localhost', 'root', '', 'test')            #### Localhost connection
    else:
        con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
    
    gameList = getData()
    gameinfo = linemovement(con, homeawaySplit(gameList, weekNum), betlist, weekNum)
    addtoDb(con, gameinfo, weekNum)
    
    
    
if __name__ == '__main__':
    main()