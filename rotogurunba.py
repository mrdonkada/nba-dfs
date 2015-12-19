#!/usr/local/bin/python2.7

import requests
from bs4 import BeautifulSoup
import MySQLdb
import datetime

def getdailyresults(month, day, year, playerdict, league):
    
    positions = ['Guards', 'Forwards', 'Centers', 'Unlisted']
    
    datestr = str(year) + '-' + str(month) + '-' + str(day)
    ### Start with Fanduel results for the day
    
    r = requests.get("http://rotoguru1.com/cgi-bin/hyday.pl?mon=" + str(month) + "&day=" + str(day) + "&year=" + str(year) + "&game=" + league).text

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
                playerdict[playerdata[-1]]['name'] = playerdata[1]
                playerdict[playerdata[-1]]['start'] = playerdata[2]
                playerdict[playerdata[-1]]['fdsal'] = ''
                playerdict[playerdata[-1]]['dksal'] = ''
                playerdict[playerdata[-1]][league + 'sal'] = playerdata[4]
                playerdict[playerdata[-1]]['team'] = playerdata[5]
                playerdict[playerdata[-1]]['opp'] = playerdata[6]
        
            else:
                playerdict[playerdata[-1]][league + 'sal'] = playerdata[4]
                
        else:
            playerdict[playerdata[-1]] = {}
            playerdict[playerdata[-1]]['pos'] = playerdata[0]
            playerdict[playerdata[-1]]['name'] = playerdata[1]
            playerdict[playerdata[-1]]['start'] = playerdata[2]
            playerdict[playerdata[-1]]['fdsal'] = ''
            playerdict[playerdata[-1]]['dksal'] = ''
            playerdict[playerdata[-1]][league + 'sal'] = playerdata[4]
            playerdict[playerdata[-1]]['team'] = playerdata[5]
            playerdict[playerdata[-1]]['opp'] = playerdata[6]
    
    return playerdict

leagues = ['fd', 'dk']    
playerdict = {}
dailyresults = {}

year = 2015
month = 12
day = 11

for i in range(8,12):
    if i < 10:
        day = '0' + str(i)
    else:
        day = str(i)
    datestr = str(year) + '-' + str(month) + '-' + day
    for league in leagues:
        dailyresults[datestr] = getdailyresults(month, i, year, playerdict, league)
print dailyresults, dailyresults.keys()