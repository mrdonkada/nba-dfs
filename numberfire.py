#!/usr/local/bin/python2.7

from bs4 import BeautifulSoup
import requests
import MySQLdb
import datetime
import re
import json

r = requests.get("http://www.numberfire.com/nba/fantasy/full-fantasy-basketball-projections").text
soup = BeautifulSoup(r)

# weekNum = int(raw_input("Week number? "))

projData = soup.find_all("script", {"type" : "text/javascript"})


projData = projData[2]


reg = re.search('var NF_DATA.*', str(projData))

reg = reg.group()[13:-2]

projData = json.loads(reg)

dailyProj = projData['daily_projections']

print dailyProj[0].keys()