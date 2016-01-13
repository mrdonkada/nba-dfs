#!/usr/local/bin/python2.7

import requests
from bs4 import BeautifulSoup
import MySQLdb
import datetime
import csv

## http://www.fantasylabs.com/api/playermodel/2/12_14_2015/?modelId=181330

fieldnames = ['Score','Player_Name','Position','Team','Opposing_TeamFB','B2B','Salary','ImpPts','PtVal','MinutesProj','ProjPlusMinus','OppPlusMinus',\
'Floor','AvgPts','Ceiling','Month_PPG','Season_PPG','Usage','UsageProj','PaceD','PER','Trend','MyTrends',\
'Month_Salary_Change','Season_Salary_Change','Total','Pts','OppPts','Spread','Vegas','Run_Change','Season_Plus_Minus','Plus_Minus','Days_Between_games',\
'OfficialPlusMinus','Refs','InjuryStatus','OppPlusMinusPct','Site_Salary','CeilingPct','Consistency','Month_Count','Season_Count','Confirmed','FloorPct','Pro_Pct','PtPerDPct','FloorPtPerDPct',\
'ProjPlusMinusPct','Upside','FantasyResultId','SpreadPct','ProjPct','Season_PPG_Percentile','Salary_Movement','MyTrends|custom','ActualPoints',\
'IsLocked','Month_X2','Month_X1','Month_X0','Season_X2','Season_X1','Season_X0','SourceId','PlayerId','EventTeamId', 'PositionId', 'EventId']

# playerlist = []
# with open('bbfl.txt', 'r') as f:
#     playerlist = f.read()

# playerlist = json.loads(playerlist)

def getflabsdata(month, day, year, model):
    
    if int(day) < 10:
        day = "0" + str(day)
    else:
        day = str(day)
        
    datestr = str(month) + "_" + str(day) + "_" + str(year)
    

    source = int(raw_input("Fanduel = 3, Draftkings = 4, Yahoo = 11: "))
    
    filenm = 'datafiles/' + str(model) + '_' + datestr + '.csv'

    playerlist = requests.get("http://www.fantasylabs.com/api/playermodel/2/" + datestr + "/?modelId=" + str(model)).json()

    with open(filenm, 'w') as w:
        writer = csv.DictWriter(w, fieldnames)
        writer.writeheader()
        for player in playerlist:
            league = player['Properties']['SourceId']
            if league == source:
                pldict = player['Properties']
                plkeys = pldict.keys()
                print plkeys
                if 'MyTrends|custom' not in plkeys:
                    print True
                    pldict['MyTrends|custom'] = 0
                    print pldict.keys()
                writer.writerow(pldict)
                pldict = {}
    
    return
    
def main():
    
    balesphan = 181330
    balesphanNew = 209433
    
    month = 1
    day = 11
    year = 2016
    
    getflabsdata(month, day, year, balesphanNew)
    
if __name__ == '__main__':
    main()