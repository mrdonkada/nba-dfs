#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import re
import time
import MySQLdb
import datetime


def getdata():

    headerList = ['week', 'playerID', 'playernm_full', 'playernm_first', 'playernm_last', 'Pos', 'GameInfo', \
    'dk_salary', 'dkp', 'dk_value', 'playerLink', 'fd_salary', 'fdp', 'fd_value']


    ####### Sign into Rotogrinders
    r = requests.get("https://rotogrinders.com/sign-in")

    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {'username':'MurrDogg4','password':'tro2bro'}

    session = requests.Session()
    session.post('https://rotogrinders.com/sign-in',headers=headers,data=payload)

    ####### Start Draftkings scrape
    r = session.get("https://rotogrinders.com/projected-stats/nba?site=draftkings").text
    soup = BeautifulSoup(r)

    table = soup.find("table", id="proj-stats")

    playerSet = table.find_all("tr", class_="player")
    # print playerSet

    player = []
    playerList = []

    for rows in playerSet:
        items = rows.find_all("td")
        plLink = rows.find("a")                     # Find player ID link
        plLink = plLink['href']                     # Capture player ID link
        testing = re.finditer('-.+-',plLink)        # Search player ID link for the ID using firstnm-lastnm-ID
        for i in testing:
            pidchar = i.span()[1]                   # Gets the span (start, end) of the regex and uses the end
        plID = int(plLink[pidchar:])                     # Get the ID from the link using pidchar as the start char
        player.append(plID)
        for item in items:
            player.append(item.text.strip().replace('    ',' '))
        player.append(plLink)
        playerList.append(player)
        player = []

    return playerList

print getdata()
    
# time.sleep(2)                               # Sleep for 2 seconds between data pulls
#
# ####### Start Fanduel scrape
#
# r = session.get("https://rotogrinders.com/projected-stats/nfl?site=fanduel").text
# soup = BeautifulSoup(r)
#
# table = soup.find_all("tbody")
#
# playerSet = soup.find_all("tr", class_="player")
# # print playerSet
#
# player = []
# fdplayerList = []
#
# for rows in playerSet:
#     items = rows.find_all("td")
#     plLink = rows.find("a")                     # Find player ID link
#     plLink = plLink['href']                     # Capture player ID link
#     testing = re.finditer('-.+-',plLink)        # Search player ID link for the ID using firstnm-lastnm-ID
#     for i in testing:
#         pidchar = i.span()[1]                   # Gets the span (start, end) of the regex and uses the end
#     plID = int(plLink[pidchar:])                     # Get the ID from the link using pidchar as the start char
#     player.append(plID)
#     for item in items:
#         player.append(item.text.strip().replace('    ',' '))
#     player.append(plLink)
#     fdplayerList.append(player)
#     player = []
#
# ##### Pre-append placeholders for FD data
#
# for player in playerList:
#     for i in range(0,3):
#         player.append('')
#
# ##### Add Fanduel info to master list based on player ID
#
# for player in playerList:
#     for fdplayer in fdplayerList:
#         if player[0] == fdplayer[0]:
#             player[8] = fdplayer[4]
#             player[9] = fdplayer[5]
#             player[10] = fdplayer[6]
#             continue
#
# ###### Check for any Fanduel players that aren't in DK
# counter = 0
# for fdplayer in fdplayerList:
#     for player in playerList:
#         if fdplayer[0] == player[0]:
#             counter += 1
#             continue
#     if counter == 0:
#         for i in range(0,3):
#             fdplayer.insert(4, 0)
#         playerList.append(fdplayer)
#
# ####### Convert salaries from $X.XK to XXXX (int)
# for player in playerList:
#     try:
#         player[4] = int(round(float(player[4].replace('$','').replace('K','')),1) * 1000)
#     except:
#         player[4] = 0
#     try:
#         player[8] = int(round(float(player[8].replace('$','').replace('K','')),1) * 1000)
#     except:
#         player[8] = 0
#
# for player in playerList:               # Finishing touches - add week num + first, last name
#     player.insert(0, weekNum)
#     if player[3] != 'DST':
#         playerNm = player[2].split(' ',1)
#         player.insert(3, playerNm[0])
#         player.insert(4, playerNm[1])
#     else:
#         player.insert(3,'')
#         player.insert(4,'')
# print playerList
#
# ####### Add to Dictionary
# #
# # dictList = []
# # for players in playerList:  # Create a dictionary from each row, then add to a list for csv export
# #     playerdict = {}
# #     for header in headerList:
# #         playerdict[header] = players[headerList.index(header)]
# #     dictList.append(playerdict)
# #
# # print dictList
#
# ####### Add to database
# local = False
# if local == False:
#     con = MySQLdb.connect(host='mysql.server', user='MurrDogg4', passwd='syracuse', db='MurrDogg4$dfs-nfl')
# else:
#     con = MySQLdb.connect('localhost', 'root', '', 'test')          #### Localhost connection
#
# query = "DELETE FROM rotogrinders_wkly_proj WHERE week = %d" % (weekNum)
# x = con.cursor()
# x.execute(query)
#
# for row in playerList:
#     print row
#     with con:
#         query = "INSERT INTO rotogrinders_wkly_proj (week, player_id, playernm_full, playernm_first, playernm_last, \
#             pos, gameinfo, dk_salary, dkp, dk_value, weblink, fd_salary, fdp, fd_value) \
#             VALUES (%d, %d, "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", "'"%s"'", %d, %1.2f, %1.2f, "'"%s"'", \
#             %d, %1.2f, %1.2f)" % \
#             (int(row[0]), int(row[1]), row[2], row[3], row[4], row[5], row[6], int(row[7]), \
#             round(float(row[8]),2), round(float(row[9]),2), row[10], int(row[11]), round(float(row[12]),2), round(float(row[13]),2))
#         x = con.cursor()
#         x.execute(query)

