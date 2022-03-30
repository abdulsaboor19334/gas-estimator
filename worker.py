import typing
from web3 import Web3
import numpy as np
from PyQt5.QtCore import ( QObject, pyqtSlot,pyqtSignal)
import pyqtgraph as pg
import time
import web3
import math

class Worker(QObject):
    soc = web3.WebsocketProvider('wss://eth-mainnet.alchemyapi.io/v2/022kSRhpRYdO_v49hxgVWE-Jv-nRHBS5')
    datReady = pyqtSignal(float,float)
    def __init__(self):
        self.x = Web3(self.soc)
        super().__init__()
    @pyqtSlot()    
    def plot(self):
        print('plotting started')
        self.old = 0
        while True:            
            self.new = self.x.eth.gas_price
            if self.new != self.old:
                # print('orignal gas price : ' , self.new * (10**-9))
                # print(math.log2(time.time()))
                self.datReady.emit(self.new * (10**-9),math.log10(time.time()))
            self.old = self.new
            