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

    return gamelist[0]
    
print playergamedata()