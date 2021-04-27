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
micramDAC.dac_pattern_stop()


fname='input_dc.xlsx'
datain = pd.read_excel(fname,sheetname='Sheet1')
datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']] = datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']].astype(np.float64)

for ind in datain.index:
    
    tec.settemp(datain['set_temperature'][ind])
    laserbias.setcurrent(datain['set_laserCurrent'][ind])
    eabias.setvoltage(datain['set_EAvoltage'][ind])
    time.sleep(0.2)
    
    datain.at[ind,'read_temperature'] = tec.querytemp()
    datain.at[ind,'read_EAcurrent'] = eabias.querycurrent()
    datain.at[ind,'read_Pave'] = opm.querypower()
    print('run step %d, total step %d'% (ind,max(datain.index)))
    
    
writer = pd.ExcelWriter('output_dc.xlsx')    
datain.to_excel(writer,'Sheet1')
    



