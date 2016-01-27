#!/usr/local/bin/python2.7
import MySQLdb

sqlfile = 'sql/consistency.sql'

with open(sqlfile) as f:
    
    g = f.read()

    query = g.replace('\n',' ')
    print query
#
# for line in open(sqlfile):
#     print line
    
# f.close()#
#
con = MySQLdb.connect('localhost', 'root', '', 'dfs-nba')

with con:
    x = con.cursor()
    x.execute(query)

    rows = x.fetchall()

    for row in rows:
        print row