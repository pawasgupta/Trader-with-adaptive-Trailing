from __future__ import division
__author__ = 'pawas'
import numpy as np
import math
import cvxopt as cv
from svmutil import *

def ma(m,win):
    n=np.repeat(1.0,win)/win
    c=np.convolve(m,n,'valid')
    return c

def np2cv(mat1):
    dim1=len(mat1)
    dim2=len(np.transpose(mat1))
    col=[]
    for i in range (0,dim2,1):
        for j in range (0,dim1,1):
            col.append(mat1[j,i])

    mat2=cv.matrix(col,(dim1,dim2))
    return mat2


def FindPos(ClosePrice,t):
    ClosePrice=np.resize(ClosePrice,len(ClosePrice))
    ClosePrice=np.asfarray(ClosePrice, dtype='float64')
    sz=len(ClosePrice)

    smooth_price_temp=ma(ClosePrice,3)
    x=np.zeros(sz,dtype='float64')
    x[0:2]=0
    x[2:sz]=smooth_price_temp #Smooth series
                              #used to calculate features and returns

    y=ClosePrice # Contains Raw Series
                 #used to calculate profit

    d=5.0

    a=1000.0
    sf=0.0
    alpha=100.0
    betaa=60.0
    gamma=5.0
    dell=0.007
    win=80
    bars_back=25.0
    regressionwindow=20
    m = svm_load_model('regressionmodel')

    #-------Some global variables that are initialised once------
    # be careful with their use
    # 1st call
    if  not hasattr(FindPos, "Pos"):
        FindPos.Pos= np.zeros(win,dtype='float64')

    if  not hasattr(FindPos, "Prof"):
        FindPos.Prof=np.zeros(win,dtype='float64')

    if  not hasattr(FindPos, "total"):
        FindPos.total=np.zeros(win,dtype='float64')

    if not hasattr(FindPos, "temp"):
        FindPos.temp=np.zeros(win,dtype='float64')
        #FindPos.Fileid=open('Finaltemp.txt','w')
        #for loopvar in range(0,win):
        #    FindPos.Fileid.write('0 \n')

    if not hasattr(FindPos, "past"):
        FindPos.past=-1

    if not hasattr (FindPos, "phi"):
        FindPos.phi=np.zeros((bars_back,win),dtype='float64')  # declaring feature vector

    if not hasattr(FindPos, "r"):
        FindPos.r=np.zeros(win-1,'float64')
        localvar=1
        while (localvar<win-1):    #loop to assign all the values of r, cannot put abcd assignment here because it has to be in the same loop as the weight update
            FindPos.r[localvar]=x[localvar]-x[localvar-1]
            localvar=localvar+1

    if not hasattr (FindPos, "w"):
        FindPos.w=np.zeros((bars_back,win),dtype='float64')
        
    if not hasattr (FindPos, "maxCumProfit"):
        FindPos.maxCumProfit = -1

    #---now appending the columns to each data variable for current time instant
    FindPos.phi=np.hstack((FindPos.phi,np.reshape(x[t-bars_back:t],[-1,1]))) #appending a column to phi
    tot=np.sum(FindPos.phi,axis=0,dtype='float64')
    FindPos.phi[:,t]=FindPos.phi[:,t]/tot[t]

    FindPos.r=np.append(FindPos.r,(x[t-1]-x[t-2]))
    FindPos.w=np.hstack((FindPos.w,np.zeros((bars_back,1),dtype="float64")))
    FindPos.temp=np.append(FindPos.temp,0.0)
    FindPos.Pos=np.append(FindPos.Pos,0.0)
    FindPos.Prof=np.append(FindPos.Prof,0.0)
    FindPos.total=np.append(FindPos.total,0.0)
    FindPos.maxCumProfit = -1
    for i in range(1,19):
        for j in range (i,20):
            if (FindPos.total[t-20+j]-FindPos.total[t-20+i] > FindPos.maxCumProfit):
                FindPos.maxCumProfit = FindPos.total[t-20+j]-FindPos.total[t-20+i]


    #--------Ready with variables----------
    #-------------My main algo-----------

    phi_used=FindPos.phi[:,t-win:t+1]

    tot1=np.sum(phi_used,axis=1,dtype='float64')
    tot1=tot1/(win+1)
    tot1=np.reshape(tot1,(-1,1))
    tot1=np.repeat(tot1,win+1,axis=1)
    phi_used=phi_used-tot1


    bias=0.0

    l=np.zeros(win,dtype='float64')
    g=np.zeros(win,dtype='float64')



    mat1=np.zeros([win,win],dtype='float64')
    mat2=np.zeros([win,win],dtype='float64')
    mat3=np.zeros([win,win],dtype='float64')
    mat4=np.zeros([win,win],dtype='float64')

    H=np.zeros([2*win,2*win],dtype='float64')

    for i in range(0,win,1):
        for j in range(0,win,1):
            mat1[i,j]=FindPos.r[t-win+i]*FindPos.r[t-win+j]*(math.pow((1+np.dot((np.transpose(phi_used[:,[i]])),(phi_used[:,[j]]))),d))

            mat2[i,j]=FindPos.r[t-win+i]*dell*((math.pow((1+np.dot((np.transpose(phi_used[:,[i]])),(phi_used[:,[j+1]]))),d))-(math.pow((1+np.dot((np.transpose(phi_used[:,[i]])),(phi_used[:,[j]]))),d)))

            mat3[i,j]=FindPos.r[t-win+i]*dell*((math.pow((1+np.dot((np.transpose(phi_used[:,[i+1]])),(phi_used[:,[j]]))),d))-(math.pow((1+np.dot((np.transpose(phi_used[:,[i]])),(phi_used[:,[j]]))),d)))

            mat4[i,j]=dell*dell*((math.pow((1+np.dot((np.transpose(phi_used[:,[i+1]])),(phi_used[:,[j+1]]))),d))+(math.pow((1+np.dot((np.transpose(phi_used[:,[i]])),(phi_used[:,[j]]))),d))-(math.pow((1+np.dot((np.transpose(phi_used[:,[i+1]])),(phi_used[:,[j]]))),d))-(math.pow((1+np.dot((np.transpose(phi_used[:,[i]])),(phi_used[:,[j+1]]))),d)))



    H[0:win,0:win]=mat1

    H[0:win,win:2*win]=mat2

    H[win:2*win,0:win]=mat3

    H[win:2*win,win:2*win]=mat4

    tmp=0

    while (tmp<2*win):
        H[tmp,tmp]=H[tmp,tmp]+0.1;
        tmp=tmp+1;


    matA1=-1*(np.matrix(np.identity(2*win,dtype='float64')))
    matA2=(np.matrix(np.identity(2*win,dtype='float64')))

    matA=np.zeros([4*win,2*win],dtype='float64')
    matA[0:2*win,0:2*win]=matA1
    matA[2*win:4*win,0:2*win]=matA2




    matb=np.zeros([4*win,1],dtype='float64')
    matb[0:win,[0]]=-betaa*np.ones([win,1],dtype='float64')
    matb[win:2*win,[0]]=gamma*np.ones([win,1],dtype='float64')
    matb[2*win:3*win,[0]]=alpha*np.ones([win,1],dtype='float64')
    matb[3*win:4*win,[0]]=gamma*np.ones([win,1],dtype='float64')

    inipt=0.5*np.ones([2*win,1],dtype='float64')

    f_matrix=np.zeros([2*win, 1],dtype='float64')

    matQ=np2cv(H)
    matP=np2cv(f_matrix)
    matG=np2cv(matA)
    matH=np2cv(matb)

    inipt_cv=np2cv(inipt)


    sol=cv.solvers.qp(matQ,matP,matG,matH,None,None,None,inipt_cv)

    ftemp1=sol['x']

    ftemp2=[float(tempval) for tempval in ftemp1]

    fin=np.array(ftemp2)

    l[0:win]=fin[0:win]
    g[0:win]=fin[win:2*win]

    for i in range(0,win,1):
        FindPos.w[:,t]=FindPos.w[:,t]+((l[i]*FindPos.r[t-win+i]*phi_used[:,i]) + (g[i]*dell*(phi_used[:,i+1]-phi_used[:,i])))
        bias=bias+(1/a)*FindPos.r[t-win+i]*l[i]

    tempr=(np.dot((np.transpose(FindPos.w[:,[t]])),phi_used[:,win])+bias)/(np.linalg.norm(FindPos.w[:,[t]]))
    FindPos.temp[t]=round(tempr,2)
    #FindPos.Fileid.write(str(FindPos.temp[t]))
    #FindPos.Fileid.write('\n')

    dummytarget=[]
    dummytarget.append(0.2)
    regressioninput=[]
    regressioninput.append([])
    regressioninput[0].extend(FindPos.r[t-regressionwindow:t])

    p_label, p_acc, p_val = svm_predict(dummytarget, regressioninput, m)


    if FindPos.temp[t]>0.1 and abs(FindPos.temp[t-1])<0.1:
        FindPos.Pos[t]=1
    elif FindPos.temp[t]<-0.1 and abs(FindPos.temp[t-1])<0.1:
        FindPos.Pos[t]=-1
    elif abs(FindPos.temp[t])<0.1:
        FindPos.Pos[t]=0
    else:
        FindPos.Pos[t]=FindPos.Pos[t-1]
        
    if (FindPos.maxCumProfit-FindPos.total[t-1] > p_label):
        FindPos.Pos[t] = 0

    FindPos.Prof[t]=FindPos.Pos[t-1]*(y[t-1]-y[t-2])-0.035*abs(FindPos.Pos[t]-FindPos.Pos[t-1])   ##instantaneous profit

    FindPos.total[t]=FindPos.total[t-1]+FindPos.Prof[t] #Cumulative Profit

    profit=FindPos.total[t]


    return FindPos.Pos[t]


