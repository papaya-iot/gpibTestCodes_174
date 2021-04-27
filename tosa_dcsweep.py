# Varying Vbias, measuring Power, ER #

"""
Instrument connection
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
import uspatools


tec=visainst.tec('TCPIP0::10.75.114.18::inst5::INSTR')
laserbias = visainst.smu('TCPIP0::10.75.114.18::inst26::INSTR')
laserbias.sourcetype('current')
eabias = visainst.smu('TCPIP0::10.75.114.18::inst2::INSTR')
eabias.sourcetype('voltage')
opm = visainst.powermeter('TCPIP0::10.75.114.18::inst4::INSTR')
dca = visainst.dca('TCPIP0::10.75.114.18::inst7::INSTR')
micramDAC = uspatools.USPA7201('10.75.61.202', 5017, 'C:/Users/lab6750/Desktop/Test Program/uspatools-0.3.3/uspatools-0.3.3', cd3_installed=True)
micramDAC.dac_pattern_stop()


fname='input_dc2.xlsx'
datain = pd.read_excel(fname,sheetname='Sheet1')
datain = datain.astype(np.float64)
#datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']] = datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']].astype(np.float64)

for ind in datain.index:
    
    tec.settemp(datain['set_temperature'][ind])
    tec.settemp(25.00)
    laserbias.setcurrent(datain['set_laserCurrent'][ind])
    eabias.setvoltage(datain['set_EAvoltage'][ind])
    time.sleep(0.05)
    
    dt = abs(tec.querytemp()-datain['set_temperature'][ind] )
#    while (dt>3 ): #and dt<15
#        temp_c = tec.querytemp()
#        #time.sleep(.1)
#        dt = abs(temp_c-datain['set_temperature'][ind] )
#        print('temp delta ' + str(dt))
        
#    if dt>5 and dt<15:
#        print('dt is %f, tec working...'%dt)
#        time.sleep(120)
#    elif dt >15:
#        print('dt is %f, tec working...'%dt)
#        time.sleep(300)
#    else:
#        pass
    
   
    datain.at[ind,'read_temperature'] = tec.querytemp()
    datain.at[ind,'read_EAcurrent'] = eabias.querycurrent()
    datain.at[ind,'read_Pave'] = opm.querypower()
    print('run step %d, total step %d, at temp %.3f'% (ind,max(datain.index),datain.at[ind,'read_temperature']))
    
    
writer = pd.ExcelWriter('output_dc.xlsx')    
datain.to_excel(writer,'Sheet1')
    
#writer = pd.ExcelWriter('output_dc.xlsx')    
#datain.to_excel(writer,'Sheet1')


