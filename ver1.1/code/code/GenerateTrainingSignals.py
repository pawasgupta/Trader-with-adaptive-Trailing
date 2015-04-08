from __future__ import division #hello
__author__ = 'pawas'

#---------------MODULES REQUIRED---------------

import MySQLdb as mariadb
import time
import numpy as np

#---------------------------------------------

#-----My Functions in separate files--------
from CreateOHLC import CreateOHLCMatrix
from PositionCalculation import FindPos
from Strategy import OmegaStrategy
from rina import GenerateRina
#-----------------------------------------------

# ---------------GLOBAL VARIABLES--------------

loopvar=1
rnge_start=0 # pointer to mark start of 15 min period
rnge_end=0   # pointer to mark end of 15 min period
ohlc_count=0 # to count number of bars created


win=80  # to start our algorithm only aget win samples of data are ready
bars_refered_by_omega=2

qty=10000
WaitTimer=0
WaitTimer2=8
RunInteractive=0
GenerateRinaCsv=1
innerLoopCount=1
ContinueWaitCount=0
LiveSession=0
l_iLastTime="9:00:00"
l_TrainingTable="tbl_USDTrainingData"
l_TestingTable = "tbl_USDTestingData"
# ------------------------------------------------------columnIndices of table-----------------
DAY=0
TIME=1
OPEN=2
HIGH=3
LOW=4
CLOSE=5
l_iTimeUnit = 15


# --------------------------------------------------------------------------------------------
#----------SOME NEW VARIABLES---------------------

OneMinuteLineNumber=0
OneMinuteMatrix=[]
OHLCMatrix=[]
PositionGot=[]
MarketPosition=0.0
MarketEnterPrice=0.0
trail=0.0
trailprice=0.0
CurrentClose=0.0


print "Start date "  + time.strftime("%x")
print "Start time " + time.strftime("%X")


# -----------------START---------------------------

while(loopvar==1):
    db=mariadb.connect(user='pawasgupta', passwd='@1234', db='test_db')  # connect to database
    cur = db.cursor()
    #................READ 1 min data from DB------------------------------
    OneMinuteMatrix.append([]) #appending 1 line to the matrix
    OneMinuteLineNumber=OneMinuteLineNumber+1
    cur.execute("select * from tbl_USDTrainingData LIMIT %s,%s;",(OneMinuteLineNumber-1, 1))
    QueryResult=cur.fetchall()
    if not QueryResult:
        print 'No Data Present \n'
        print 'Done'
        print "End date "  + time.strftime("%x")
        print "End time " + time.strftime("%X")
        loopvar=0
        break
    TodayDate=''
    TodayTime=''
    for row_temp in QueryResult:
        OneMinuteMatrix[OneMinuteLineNumber-1].append(row_temp[DAY]) # date
        OneMinuteMatrix[OneMinuteLineNumber-1].append(row_temp[TIME]) # time
        OneMinuteMatrix[OneMinuteLineNumber-1].append(row_temp[OPEN]) # open
        OneMinuteMatrix[OneMinuteLineNumber-1].append(row_temp[HIGH]) # high
        OneMinuteMatrix[OneMinuteLineNumber-1].append(row_temp[LOW]) # low
        OneMinuteMatrix[OneMinuteLineNumber-1].append(row_temp[CLOSE]) # close
        CurrentClose=float(OneMinuteMatrix[OneMinuteLineNumber-1][CLOSE])
        CurrentDate=OneMinuteMatrix[OneMinuteLineNumber-1][DAY]
        CurrentTime=OneMinuteMatrix[OneMinuteLineNumber-1][TIME]

        rnge_end=OneMinuteLineNumber

    if (LiveSession):
        time.sleep(60) # if live session then wait for 1 minute to get the data

    if (((rnge_end-rnge_start)==l_iTimeUnit) or (OneMinuteMatrix[rnge_end-1][1]=="17:00")): #if you have l_iTimeunit of ticks elapsed or reached end of the day
        #give a call to OHLC_MATRIX for OneMinuteMatrix[rnge_start:rnge_end]
        OHLCMatrix.append([])
        OHLCMatrix[ohlc_count].extend(CreateOHLCMatrix(OneMinuteMatrix[rnge_start:rnge_end][:])) #Note:It is a list till now
        TodayDate=OHLCMatrix[ohlc_count][0]
        TodayTime=OHLCMatrix[ohlc_count][1]
        #print TodayTime
        #print TodayDate
        ohlc_count=ohlc_count+1
        rnge_start=rnge_end

        if (ohlc_count>=win):
            # give a call to calculate position
            PositionGot.append(FindPos(np.matrix(OHLCMatrix)[:,CLOSE],ohlc_count)) #Converting to np array when passing to functions
                                                                                          #All variables are lists here
        else:
            PositionGot.append(0)

        #------------Now we have a position---------r the concatenation axis must match exactly-----
        TodayPosition=PositionGot[ohlc_count-1]
        cur.execute("Insert into tbl_TrainingResults(Date,Time,Position) values(%s,%s,%s);", (TodayDate, TodayTime, TodayPosition)) #Write into DB
        db.commit()

        if (ohlc_count>=bars_refered_by_omega):
        #-------- give a call to omega strategy-----
            [MarketEnterPrice,MarketPosition]=OmegaStrategy(np.matrix(OHLCMatrix),ohlc_count,np.array(PositionGot,dtype='float64'),MarketPosition,cur,db)

    #--------NOW WE HAVE A POSITON IN THE MARKET SO IMPLEMENTING STOPLOSS,
    #--------AND TRAILING WHICH WILL BE CHECKED EVERY MINUTE

    #-------------------TRAILING-------------------------------------------------------
    #--------------Trailing long position----------------------------------------------
    if (MarketPosition==1 and trail==1 and CurrentClose>=trailprice):    #trail is ON and market is going up
        trailprice=CurrentClose
    elif (MarketPosition==1 and trail==1 and CurrentClose<=trailprice-0.005*trailprice): #trail is ON and market moved down
        MarketPosition=0
        trail=0
        trailprice=0.0
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(CurrentDate,CurrentTime,CurrentClose,'SELL',qty,'Long_TL_HIT'))
        db.commit()

    elif(MarketPosition==1 and trail==0 and CurrentClose>=MarketEnterPrice+MarketEnterPrice*0.025):
        trail=1
        trailprice=CurrentClose
    #-------------------------------------------------------------------------------------------
    #---------------------Trailing Short position-------------
    if (MarketPosition==-1 and trail==-1 and CurrentClose<=trailprice):    #trail is ON and market is going down
        trailprice=CurrentClose
    elif (MarketPosition==-1 and trail==-1 and CurrentClose>=trailprice+0.005*trailprice): #trail is ON and market moved up
        MarketPosition=0
        trail=0
        trailprice=0.0
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(CurrentDate,CurrentTime,CurrentClose,'BUY',qty,'SHORT_TL_HIT'))
        db.commit()

    elif(MarketPosition==-1 and trail==0 and CurrentClose<=MarketEnterPrice-MarketEnterPrice*0.025):
        trail=-1
        tralprice=CurrentClose

    #-----------------------------------------------------------------------------------------------------------------%

    #-------------------STOPLOSS------------------------%
    #---------------for Long position-------------------%
    if ((MarketPosition==1) and (CurrentClose<=(MarketEnterPrice-0.025*MarketEnterPrice))):
        MarketPosition=0
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(CurrentDate,CurrentTime,CurrentClose,'SELL',qty,'Long_StopLoss'))
        db.commit()

    #---------------for short position------------------%
    if ((MarketPosition==-1) and (CurrentClose>=(MarketEnterPrice+0.025*MarketEnterPrice))):
        MarketPosition=0
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(CurrentDate,CurrentTime,CurrentClose,'BUY',qty,'Short_StopLoss'))
        db.commit()
    #------------------------------------------------------%


    if (TodayTime=="17:00"): # reached end of the day
        #generate Rina CSV
        print TodayDate
        print TodayTime
        if (GenerateRinaCsv):
            cur.execute("Select * from tbl_TrainingSignals where date =%s;",(TodayDate,))
            Signals=cur.fetchall()
            if (Signals):
                GenerateRina(Signals)
        if (RunInteractive):
            print ('Reached end of the day....Wanna continue...\n Enter 0 to break \n Enter 1 to continue')
            loopvar=input('Enter your choice: ')   #we can delete the datamatrix here as it will not be needed any more
            if (loopvar==0):
                break


