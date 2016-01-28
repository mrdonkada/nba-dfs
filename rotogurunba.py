#!/usr/local/bin/python2.7

import requests
from bs4 import BeautifulSoup
import MySQLdb
import datetime
import time

def getdailyresults(month, day, year, playerdict, league):
    
    positions = ['Guards', 'Forwards', 'Centers', 'Unlisted']
    
    datestr = str(year) + '-' + str(month) + '-' + str(day)
    ### Start with Fanduel results for the day
    
    link = "http://rotoguru1.com/cgi-bin/hyday.pl?mon=" + str(month) + "&day=" + str(day) + "&year=" + str(year) + "&game=" + league
    r = requests.get(link).text

    soup = BeautifulSoup(r)
    playerSet = soup.find_all("tr")
    boldind = []
    playerSet = [t for t in playerSet if (not t.find_all("hr"))]
    for i in playerSet:
        rows = i.find_all("td")
        for row in rows:
            if row.find("b"):
                if row.text.strip() in positions:
                    boldind.append(playerSet.index(i))
    
    # print boldind
    
    if len(boldind) == 4:
        playerSet = playerSet[:boldind[3]]
    
        boldind = boldind[:3]
    
    for i in boldind[::-1]:
        # print i
        del playerSet[i]
    
    for players in playerSet[boldind[0]:]:
        playerdata = []
        rows = players.find_all("td")
        
        links = players.find("a")   # Add player ID
        try:
            plLink = links['href']
            plid = plLink[plLink.index('cgi?')+4:-1]        ## there is an 'x' at the end that needs to be removed
        except:
            plid = ''
        
        
        for row in rows:
            playerdata.append(row.text.strip())
        playerdata.append(plid)
        if playerdata[1][-1] == '^':
            playerdata[1] = playerdata[1][:-1]
            playerdata.insert(2, 1)
        else:
            playerdata.insert(2, 0)
        # print playerdata
        
        if len(playerdict) != 0:
            keyset = playerdict.keys()
            
            if playerdata[-1] not in keyset:
                
                playerdict[playerdata[-1]] = {}
                playerdict[playerdata[-1]]['pos'] = playerdata[0]
                
                playername = cleanName(playerdata[1])
                playerdict[playerdata[-1]]['fullNm'] = playername[0]
                playerdict[playerdata[-1]]['lastNm'] = playername[1]
                playerdict[playerdata[-1]]['firstNm'] = playername[2]
                
                playerdict[playerdata[-1]]['start'] = playerdata[2]
                playerdict[playerdata[-1]]['fdsal'] = ''
                playerdict[playerdata[-1]]['dksal'] = ''
                playerdict[playerdata[-1]]['fdp'] = ''
                playerdict[playerdata[-1]]['dkp'] = ''
                
                salary = cleanSal(playerdata[4])
                playerdict[playerdata[-1]][league + 'sal'] = salary
                playerdict[playerdata[-1]][league + 'p'] = playerdata[3]
                playerdict[playerdata[-1]]['team'] = playerdata[5]
                
                location = homeaway(playerdata[6])
                playerdict[playerdata[-1]]['homeaway'] = location[0]
                playerdict[playerdata[-1]]['opp'] = location[1]
        
            else:
                salary = cleanSal(playerdata[4])
                playerdict[playerdata[-1]][league + 'sal'] = salary
                playerdict[playerdata[-1]][league + 'p'] = playerdata[3]
                
        else:
            playerdict[playerdata[-1]] = {}
            playerdict[playerdata[-1]]['pos'] = playerdata[0]
            
            playername = cleanName(playerdata[1])
            playerdict[playerdata[-1]]['fullNm'] = playername[0]
            playerdict[playerdata[-1]]['lastNm'] = playername[1]
            playerdict[playerdata[-1]]['firstNm'] = playername[2]
            
            playerdict[playerdata[-1]]['start'] = playerdata[2]
            playerdict[playerdata[-1]]['fdsal'] = ''
            playerdict[playerdata[-1]]['dksal'] = ''
            playerdict[playerdata[-1]]['fdp'] = ''
            playerdict[playerdata[-1]]['dkp'] = ''
            
            salary = cleanSal(playerdata[4])
            playerdict[playerdata[-1]][league + 'sal'] = salary
            playerdict[playerdata[-1]][league + 'p'] = playerdata[3]
            
            playerdict[playerdata[-1]]['team'] = playerdata[5]
            
            location = homeaway(playerdata[6])
            playerdict[playerdata[-1]]['homeaway'] = location[0]
            playerdict[playerdata[-1]]['opp'] = location[1]
    
    return playerdict

##### Current Output:
##### {'2015-12-09': {u'4026': {'lastNm': u'Stuckey', 'opp': u'gsw', 'dkp': u'10.5', 'fdp': u'9.4', 'firstNm': u'Rodney', 'homeaway': 'Home', 'pos': u'SG', 'dksal': u'5000', 'start': 0, 'team': u'ind', 'fullNm': u'Stuckey, Rodney', 'fdsal': u'4800'}, u'4024': {'lastNm': u'Splitter', 'opp': u'dal', 'dkp': u'0', 'fdp': u'0', 'firstNm': u'Tiago', 'homeaway': 'Away', 'pos': u'C', 'dksal': u'3000', 'start': 0, 'team': u'atl', 'fullNm': u'Splitter, Tiago', 'fdsal': u'3500'}, u'4023': {'lastNm': u'Smith', 'opp': u'den', 'dkp': u'17.5', 'fdp': u'16.9', 'firstNm': u'Jason', 'homeaway': 'Away', 'pos': u'PF', 'dksal': u'3200', 'start': 0, 'team': u'orl', 'fullNm': u'Smith, Jason', 'fdsal': u'3500'}, u'4020': {'lastNm': u'Sessions', 'opp': u'hou', 'dkp': u'18.25', 'fdp': u'18.2', 'firstNm': u'Ramon', 'homeaway': 'Home', 'pos': u'PG', 'dksal': u'3600', 'start': 0, 'team': u'was', 'fullNm': u'Sessions, Ramon', 'fdsal': u'3800'}


def cleanName(name):
    # takes in a name in format 'Smith, Jason' and returns a list of ['fullNm', 'lastNm', 'firstNm']
    #(fullNm is in original format)
    playername = []
    playername = name.split(', ')
    playername.insert(0, name)
    
    return playername
    
def homeaway(location):
    # takes in the opposing team and based on the data returns a cleaned Opp and home/away
    homeaway = []
    homeaway = location.split(' ')
    if homeaway[0] == 'v':
        homeaway[0] = 'Home'
    else:
        homeaway[0] = 'Away'
        
    return homeaway
    
def cleanSal(salary):
    # takes in salary of type '$5,000' and returns an integer '5000'
    cleansal = salary.replace('$','').replace(',','')
    return cleansal
    
def addtoDb(con, playerDict):
    
    
    for date in playerDict.keys():
        
        query = "DELETE FROM rotoguru_gamelog WHERE day = %s" % (date)
        x = con.cursor()
        x.execute(query)

        try:
            for key in playerDict[date].keys():
                with con:
                    query = "INSERT INTO rotoguru_gamelog (day, player_id, playernm_full, playernm_last, playernm_first, team, opp, \
                            homeaway, pos, start, dksal, fdsal, dkp, fdp) \
                            VALUES ("'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", \
                                    "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'")" % \
                        (date, key, playerDict[date][key]['fullNm'], playerDict[date][key]['lastNm'], playerDict[date][key]['firstNm'], playerDict[date][key]['team'], playerDict[date][key]['opp'], \
                        playerDict[date][key]['homeaway'], playerDict[date][key]['pos'], playerDict[date][key]['start'], playerDict[date][key]['dksal'], playerDict[date][key]['fdsal'], playerDict[date][key]['dkp'], playerDict[date][key]['fdp'])
                    x = con.cursor()
                    x.execute(query)
        except:
            continue

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
    leagues = ['fd', 'dk']    
    playerdict = {}
    dailyresults = {}
    
    today = datetime.date.today()
    
    local = False

    if local == False:
        fldr = 'nba-dfs/'
        serverinfo = security('mysql', fldr)
        con = MySQLdb.connect(host='mysql.server', user=serverinfo[0], passwd=serverinfo[1], db='MurrDogg4$dfs-nba')
           
    else:
        fldr = ''
        con = MySQLdb.connect('localhost', 'root', '', 'dfs-nba')            #### Localhost connection

    year = today.year
    month = today.month
    day = today.day - 1
    
    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)
    
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)

    datestr = str(year) + '-' + month + '-' + day
    try:
        for league in leagues:
            dailyresults[datestr] = getdailyresults(month, day, year, playerdict, league)
        print datestr, "complete"
        time.sleep(1)
    except:
        print datestr, "unavailable"

    print dailyresults
    
    addtoDb(con, dailyresults)
    
if __name__ == '__main__':
    main()