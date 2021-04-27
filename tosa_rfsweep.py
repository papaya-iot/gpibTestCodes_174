# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 21:42:10 2017

@author: lab6750
"""

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



tec=visainst.tec('TCPIP0::10.75.115.164::inst5::INSTR')
laserbias = visainst.smu('TCPIP0::10.75.115.164::inst26::INSTR')
laserbias.sourcetype('current')
eabias = visainst.smu('TCPIP0::10.75.115.164::inst2::INSTR')
eabias.sourcetype('voltage')
opm = visainst.powermeter()
dca = visainst.dca()
micramDAC = uspatools.USPA7201('10.75.61.202', 5017, 'C:/Users/lab6750/Desktop/Test Program/uspatools-0.3.3/uspatools-0.3.3', cd3_installed=True)
#micramDAC.dac_pattern_stop()
micramDAC.dac_pattern_start()

fname='input_RF.xlsx'
datain = pd.read_excel(fname,sheetname='Sheet1')
datain = datain.astype(np.float64)
#datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']] = datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']].astype(np.float64)

for ind in datain.index:
    
    tec.settemp(datain['set_temperature'][ind])
    
    if abs(tec.querytemp()-datain['set_temperature'][ind] ) >5:
        time.sleep(300)
        
    laserbias.setcurrent(datain['set_laserCurrent'][ind])
    eabias.setvoltage(datain['set_EAvoltage'][ind])
    micramDAC.dac_set_swing(1,datain['set_RFVpp'][ind])     # set RF vpp
    dca.autoscale()
    time.sleep(8)
    
    datain.at[ind,'read_temperature'] = tec.querytemp()
    datain.at[ind,'read_EAcurrent'] = eabias.querycurrent()
    datain.at[ind,'read_Pave'] = opm.querypower()
    
    datain.at[ind,'read_ER'] = dca.getER(ch='2A')
    datain.at[ind,'read_RLM'] = dca.getRLM(ch='2A')
    datain.at[ind,'read_DACVpp'] = dca.getOMA(ch='3A')
    
    print('run step %d, total step %d'% (ind,max(datain.index)))
    
    
writer = pd.ExcelWriter('output_RF.xlsx')    
datain.to_excel(writer,'Sheet1')
    
micramDAC.dac_pattern_stop()


