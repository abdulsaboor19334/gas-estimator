import sys
import time
from copy import deepcopy
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout
from PyQt5.QtCore import QThread
import pyqtgraph as pg
from datetime import datetime
from worker import Worker
from math import log10
class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.plotWidget = pg.plot(title='eth gas',axisItems={'bottom': pg.DateAxisItem()})
        self.plotWidget.showGrid(x=True,y=True)
        self.refrenceDat = []
        self.refTime = []
        self.dat = []
        self.timee = []
        self.forcastdat_MA =[]
        self.newtime_MA = []
        self.forcastdat_WMA =[]
        self.newtime_WMA = []
        self.alpha = 0.3
        self.graph = pg.PlotWidget()
        self.label = QLabel("live gas")
        self.obj = Worker()  # no parent!
        self.thread = QThread()  # no parent!
        self.obj.datReady.connect(self.ongasReady)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.plot)
        self.thread.start()
        self.initialize = True
        self.start = 0

    def ongasReady(self, gas,tim):
        self.latest = gas
        if self.initialize == True:
            self.refrenceDat.append(gas)
            self.refTime.append(log10(time.time()))
        if len(self.refrenceDat) >= 3:
            if self.initialize == True:
                self.dat.extend(self.refrenceDat)
                self.timee.extend(self.refTime)
                # MA
                average = self.average(self.dat)
                self.forcastdat_MA.append(average)
                self.newtime_MA.append(log10(time.time()))
                # WMA
                w_average = self.weighted_average(self.dat,[1,2,3])
                self.forcastdat_WMA.append(w_average)
                self.newtime_WMA.append(log10(time.time()))
                self.initialize = False
            self.dat.append(gas)
            self.timee.append(tim)
            self.plotWidget.plot(self.timee,self.dat,pen='r',symbol ='t2',symbolSize = 14, name ="GAS (Gwei)")
            # print(f'{self.dat} \n {self.timee}')
            self.forcastMA()
            self.forcastWMA()
            self.trend_line()
       
    def forcastMA(self):
        lastIndex = self.dat.index(self.dat[-1])
        els = self.dat[lastIndex-2:]
        sum = self.average(els)
        self.forcastdat_MA.append(sum)
        self.newtime_MA.append(self.timee[-1]+0.0000000046)
        self.plotWidget.plot(self.newtime_MA,self.forcastdat_MA,pen='b',symbol ='o',name ="Moving Average")
        # print('MA gas price : ',self.forcastdat_MA[-2],self.forcastdat_MA[-2]-self.latest)

    def forcastWMA(self):
        lastIndex = self.dat.index(self.dat[-1])
        els = self.dat[lastIndex-2:]
        sum = self.weighted_average(els,[1,2,3])
        self.forcastdat_WMA.append(sum)
        self.newtime_WMA.append(self.timee[-1]+0.0000000046)
        self.plotWidget.plot(self.newtime_WMA,self.forcastdat_WMA,pen='g',symbol ='o',name="Weighted Moving Average")
        # print('WMA gas price : ',self.forcastdat_WMA[-2],self.forcastdat_WMA[-2]-self.latest)
    
    def trend_line(self):
        dat_sum = 0
        sq_sum = 0
        x = self.timee.copy()
        y = self.dat.copy()
        # a = 0(sum(dat_sum))
        # print(x,y)
        for index in range(len(self.dat)):
            dat_sum += x[index] * y[index]
            sq_sum += x[index] ** 2
        a = dat_sum*len(y)
        b = sum(y)*sum(x)
        c = sq_sum*len(y)
        d = sum(x)**2
        # print(a,b,c,d)
        e = sum(y)
        try:
            m = (a-b)/(c-d)
        except ZeroDivisionError:
            m = a-b
        f = m*sum(x)
        y_intercept = (e-f)/len(x)

        end =  m*self.newtime_WMA[-1] + y_intercept
        if self.start == 0:
            self.start = m*self.timee[0] + y_intercept
        datx = [self.newtime_WMA[-1],self.timee[0]]
        daty = [end,self.start]
        print(datx,daty)
        try:
            self.plotWidget.removeItem(self.trend)
            self.trend = self.plotWidget.plot(datx,daty,pen='y',symbol ='o',name="trend")
        except:
            self.trend = self.plotWidget.plot(datx,daty,pen='y',symbol ='o',name="trend")
    
    def average(self,data:list) -> float:
        sum_ = sum(data)
        return sum_/len(data)
    
    def weighted_average(self,data:list,weigts:list) -> float:
        sum_ = 0
        for x in range(data.index(data[-1])+1):
            sum_ += data[x]*weigts[x]
        return sum_/sum(weigts)
       
app = QApplication(sys.argv)
form = Form()
sys.exit(app.exec_())
