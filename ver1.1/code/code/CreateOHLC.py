__author__ = 'pawas'
def CreateOHLCMatrix(OneMinuteMatrix):
    NumberOfTicks=len(OneMinuteMatrix)
    Date=OneMinuteMatrix[NumberOfTicks-1][0]
    Time=OneMinuteMatrix[NumberOfTicks-1][1]
    barOpen=round(float(OneMinuteMatrix[0][2]),2)
    barClose=round(float(OneMinuteMatrix[NumberOfTicks-1][5]),2)

    RoundedHigh = [ round((OneMinuteMatrix[temp][3]), 2) for temp in range(0,NumberOfTicks) ]
    barHigh = max(RoundedHigh)

    RoundedLow = [ round((OneMinuteMatrix[temp][3]), 2) for temp in range(0,NumberOfTicks) ]
    barLow = min(RoundedLow)
    return [Date,Time,barOpen,barHigh,barLow,barClose]