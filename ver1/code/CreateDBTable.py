__author__ = 'pawas'

import MySQLdb as mariadb

db=mariadb.connect(user='pawasgupta', passwd='@1234', db='test_db')
cur = db.cursor()

cur.execute("create table tbl_USDTrainingData(Date text NOT NULL,Time text NOT NULL,Open REAL NOT NULL,High REAL NOT NULL,Low REAL NOT NULL,Close REAL NOT NULL)")
cur.execute("create table tbl_TrainingResults(Date text NOT NULL,Time text NOT NULL,Position int NOT NULL)")
cur.execute("create table tbl_TrainingSignals(Date text NOT NULL,Time text NOT NULL,Price Real NOT NULL,TradeType text NOT NULL,Qty int NOT NULL,Remarks text)")
#-------------------------------------------------------------------------------------------
