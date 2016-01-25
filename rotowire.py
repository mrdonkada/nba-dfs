#!/usr/local/bin/python2.7

import requests
import csv
import datetime
import MySQLdb
from bs4 import BeautifulSoup


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
    datelink = str(dt.month) + "/" + str(dt.day) + "/" + str(year)

    dates = [datestr, dayid, datelink]

    return dates

def getplayerdata(date):
    
    payload = {'username':'MurrDogg4', 'p1':'tro2bro', 'submit':'Login To RotoWire.com'}
    
    session = requests.Session()
    session.post('http://www.rotowire.com/users/loginuser2.htm', data=payload)
    
    
    r = session.get('http://www.rotowire.com/basketball/daily_projections.htm?projDate=' + date).text
    
    soup = BeautifulSoup(r)
    
    #### Need to get headers
    headers = soup.find('thead')
    headerlist = ['player_id']
    
    for header in headers.find_all('th')[3:]:
        headerlist.append(header.text)
    
    print headerlist        # headerlist = [u'Player Name', u'Team', u'Opp', u'Pos', u'MIN', u'PTS', u'REB', u'AST', u'STL', u'BLK', u'3PM', u'FG%', u'FT%', u'TO', u'OREB', u'DREB', u'3PA', u'3P%', u'FGM', u'FGA', u'FTM', u'FTA', u'PF']
    
    data = soup.find('table', {'class': 'tablesorter'})
    player = []
    playerdata = []
    playerlist = []
    for row in data.find_all('tr', {'class': 'dproj-precise'}):
        for tag in row.find_all('span'):
            tag.replace_with('')
        plLink = row.find("a")['href'][14:]
        player.append(plLink)
        for item in row.find_all('td'):
            player.append(item.text)
        playerdata.append(player)
        player = []
    
    playerDict = {}
    for player in playerdata:
        for header in headerlist:
            playerDict[header] = player[headerlist.index(header)]
        playerlist.append(playerDict)
        playerDict = {}
    
    return playerlist
    
def main():
    
    today = datetime.date.today()
    dates = datestring(today)
    print getplayerdata(dates[2])
    
if __name__ == '__main__':
    main()