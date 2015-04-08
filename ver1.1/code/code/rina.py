__author__ = 'pawas'
def GenerateRina(Signals):
    if not hasattr(GenerateRina,"flag"):
        GenerateRina.flag=1
        fileid=open("RinaCsvOutput","w")
        fileid.write('"Trade #","Date","Time","Signal","Price","Contracts","% Profit","Runup","Entry Eff","Total","System"\n')
        fileid.write('"Type","Date","Time","Signal","Price","Profit","Cum Profit","Drawdown","Exit Eff","Eff","Market"\n')
        fileid.close()
    if not hasattr(GenerateRina,"tradenum"):
        GenerateRina.tradenum=1
    if not hasattr(GenerateRina,"entertype"):
        GenerateRina.entertype=''
    if not hasattr(GenerateRina,'cumprofit'):
        GenerateRina.cumprofit=0
    if not hasattr(GenerateRina,'enterprice'):
        GenerateRina.enterprice=0.0


    prof=0
    perprof=GenerateRina.tradenum
    cumprof=GenerateRina.tradenum
    entereff=0
    exiteff=0
    DD=0
    runup=0
    tot=0
    eff=0
    system='portfolio_1'
    market='USDINR1'
    datasize=len(Signals)
    fileid=open("RinaCsvOutput","a")

    if (datasize>0):
        counter=0;
        while(counter<datasize):
            if (GenerateRina.flag==1):
                enterdate=Signals[counter][0]
                entertime=Signals[counter][1]
                GenerateRina.enterprice=Signals[counter][2]
                GenerateRina.entertype=Signals[counter][3]
                entercontracts=Signals[counter][4]
                entersignalname=Signals[counter][5]
                newenterdate=enterdate.replace('-','/')
                temp='"'+str(GenerateRina.tradenum)+'","'+newenterdate+'","'+entertime+'","'+entersignalname+'","'+str(GenerateRina.enterprice)+'","'+str(entercontracts)+'","'+str(perprof)+'","'+str(runup)+'","'+str(entereff)+'","'+'","'+str(tot)+'","'+str(system)+"\n"
                #print temp
                fileid.write(temp)
                #fileid.write('"'+str(GenerateRina.tradenum))#+'","'+newenterdate+'","'+entertime+'","'+entersignalname+'","'+enterprice+'"+"'+str(entercontracts)+'","'+str(perprof)+'","'+str(runup)+'","'+str(entereff)+'","'+str(tot)+'","'+str(system)+"\n")
                counter=counter+1
                GenerateRina.flag=2

            elif(GenerateRina.flag==2):
                exitdate=Signals[counter][0]
                exittime=Signals[counter][1]
                exitprice=Signals[counter][2]
                exittype=Signals[counter][3]
                exitcontracts=Signals[counter][4]
                exitsignalname=Signals[counter][5]

                newexitdate=exitdate.replace('-','/')
                temp='"'+str(GenerateRina.entertype)+'","'+newexitdate+'","'+exittime+'","'+exitsignalname+'","'+str(exitprice)+'","'+str(prof)+'","'+str(cumprof)+'","'+str(DD)+'","'+str(exiteff)+'","'+str(eff)+'","'+market+'\n'
                fileid.write(temp)
                #fileid.write('"'+str(GenerateRina.entertype)+'","'+newexitdate+'","'+exittime+'","'+exitsignalname+'","'+exitprice+'","'+str(prof)+'","'+str(cumprof)+'","'+str(DD)+'","'+str(exiteff)+'","'+str(eff)+'","'+market+'\n')
                GenerateRina.tradenum=GenerateRina.tradenum+1

                #if GenerateRina.entertype=='BUY':
                #    GenerateRina.cumprofit=GenerateRina.cumprofit+((-GenerateRina.enterprice+exitprice)*10000)-70.0
                #if GenerateRina.entertype=='SELL':
                #    GenerateRina.cumprofit=GenerateRina.cumprofit+((GenerateRina.enterprice-exitprice)*10000)-70.0
                #print 'cumulative profit is', GenerateRina.cumprofit

                perprof=GenerateRina.tradenum
                cumprof=GenerateRina.tradenum
                counter=counter+1
                GenerateRina.flag=1

    fileid.close()
    return
