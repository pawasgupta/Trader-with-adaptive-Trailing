from __future__ import division
__author__ = 'pawas'
import numpy as np


def OmegaStrategy(OHLCMat,ohlcCount,Posi,positioninmarket,cur,db):
    #variables required

    t=ohlcCount-1
    date=OHLCMat[t,0]
    time=OHLCMat[t,1]
    #openprice=OHLCMat[t,2]
    #highprice=OHLCMat[t,3]
    #lowprice=OHLCMat[t,4]
    closeprice=float(OHLCMat[t,5])
    enterprice=0.0

    if not hasattr(OmegaStrategy, "tradetype"):
        OmegaStrategy.tradetype=np.zeros(2)
    else:
        OmegaStrategy.tradetype=np.append(OmegaStrategy.tradetype,OmegaStrategy.tradetype[t-1])

    tradetype=OmegaStrategy.tradetype
    qty=10000;

    #/-------------TAKE POSITIONS--------------------/
    if (Posi[t-1]==0 and Posi[t]==-1 and positioninmarket==0): #Generate Sell1 Signal
    	cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Enter_Short1'))
        db.commit()
        tradetype[t]=1
        enterprice=closeprice
        positioninmarket=-1

    if (Posi[t-1]==0 and Posi[t]==1 and positioninmarket==0):  #Generate Buy1 Signal
    	cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'BUY',qty,'Enter_Long1'))
        db.commit()
        tradetype[t]=1
        enterprice=closeprice
        positioninmarket=1

    if (Posi[t-1]==1 and Posi[t]==-1 and tradetype[t-1]==1 and positioninmarket==1):   #clear off your Long1 position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Long_Exit1'))
        db.commit()
        positioninmarket=0

    if (Posi[t-1]==1 and Posi[t]==-1 and tradetype[t-1]==2 and positioninmarket==1): #clear off your Long2 position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Long_Exit2'))
        db.commit()
        positioninmarket=0

    if (Posi[t-1]==1 and Posi[t]==-1 and positioninmarket==0):    #Generate a SELL2 signal
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Enter_Short2'))
        db.commit()
        tradetype[t]=2
        enterprice=closeprice
        positioninmarket=-1

    if (Posi[t-1]==-1 and Posi[t]==1 and tradetype[t-1]==1 and positioninmarket==-1):   #clear off your Short1 position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Short_Exit1'))
        db.commit()
        positioninmarket=0

    if (Posi[t-1]==-1 and Posi[t]==1 and tradetype[t-1]==2 and positioninmarket==-1): #clear off your Short2 position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Short_Exit2'))
        db.commit()
        positioninmarket=0


    if (Posi[t-1]==-1 and Posi[t]==1 and positioninmarket==0):    #Generate a BUY2 signal
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Enter_Long2'))
        db.commit()
        tradetype[t]=2
        enterprice=closeprice
        positioninmarket=1

    if (Posi[t-1]==-1 and Posi[t]==0 and tradetype[t-1]==1 and positioninmarket==-1): #clear off sell1 your position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'BUY',qty,'Short_Exit3'))
        db.commit()
        positioninmarket=0


    if (Posi[t-1]==-1 and Posi[t]==0 and tradetype[t-1]==2 and positioninmarket==-1): #clear off sell2 your position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'BUY',qty,'Short_Exit4'))
        db.commit()
        positioninmarket=0

    if (Posi[t-1]==1 and Posi[t]==0 and tradetype[t-1]==1 and positioninmarket==1):  #clear off your Buy1 position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Long_Exit3'))
        db.commit()
        positioninmarket=0

    if (Posi[t-1]==1 and Posi[t]==0 and tradetype[t-1]==2 and positioninmarket==1): #clear off your Buy2 position
        cur.execute("Insert into tbl_TrainingSignals(Date,Time,Price,TradeType,Qty,Remarks) values(%s,%s,%s,%s,%s,%s);",(date,time,closeprice,'SELL',qty,'Long_Exit4'))
        db.commit()
        positioninmarket=0

    return [enterprice,positioninmarket]








