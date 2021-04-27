## Varying Vbias, measuring Power, ER ##

# written in python 3.7

"""
Instrument connections
"""
import visa
import numpy as np
import matplotlib.pyplot as plt
import time
import math
import pandas as pd
from scipy.optimize import curve_fit
from sympy import *
import csv
#import sweep
import visainst
#import uspatools


tec=visainst.Keithley_2510('TCPIP0::192.168.2.54::inst5::INSTR')
tec.cls

tec.ESE=36
tec.SRE=32

eabias = visainst.Keithley_2400('TCPIP0::192.168.2.54::inst15::INSTR')
eabias.cls
eabias.ESE = 36
eabias.SRE = 32
eabias.sourcetype('voltage')



osa = visainst.Agilent_86142('TCPIP0::192.168.2.54::inst11::INSTR')
osa.cls
osa.ESE=32
osa.SRE=32
dmm = visainst.Agilent_33401('TCPIP0::192.168.2.54::inst28::INSTR')
dmm.cls
dmm.ESE = 36
dmm.SRE = 32
att = visainst.JDSU_HA9('TCPIP0::192.168.2.54::inst21::INSTR')

fname='input_dc2.xlsx'
datain = pd.read_excel(fname, sheet_name='Sheet1')
datain = datain.astype(np.float64)

starttime = time.perf_counter()

cnt = 0. # to change the bias

for ind in range(1, 2000): ##
    
    
    eabias.setvoltage(-cnt*50e-3)
    eabias.output = 1
    cnt +=1
    cnt %= 100
     
    tec.settemp(25.00)
    if ind % 2 == 0 :
        tec.output = 1
    else:
        tec.output = 0
     
     
     
    startwav = float(osa.startWavelength)
     
    trace = osa.getTrace()
    ary = trace.split(',')
    print(len(ary))
     
    stopwav = float(osa.stopWavelength)
     
    print('dmm voltage is %e' % dmm.dcVoltage())
    
    
    
    
    datain.at[ind,'read_temperature'] = tec.querytemp()
    datain.at[ind,'read_EAcurrent'] = eabias.querycurrent()
     
    print('run step %d, total step %d, at temp %.3f'% (ind,max(datain.index),datain.at[ind,'read_temperature']))
    print('run step %d, total step %d, at current %.6f'% (ind,max(datain.index),datain.at[ind,'read_EAcurrent']))
    
print()
print("elapsed time: {}".format(time.perf_counter() - starttime))
writer = pd.ExcelWriter('output_dc.xlsx')    
datain.to_excel(writer,'Sheet1')
    


tec.instr.close()
dmm.instr.close()
eabias.instr.close()
att.instr.close()
osa.instr.close()


