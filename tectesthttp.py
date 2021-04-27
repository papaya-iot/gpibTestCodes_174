## Varying Vbias, measuring Power, ER ##

# written in python 3.7

"""
Instrument connections
"""
#import visa
import numpy as np
import matplotlib.pyplot as plt
import time
import math
import pandas as pd
#from scipy.optimize import curve_fit
#from sympy import *
import csv
## import sweep
#import visainst
import httpinst as hi

## import uspatools


# tec = hi.Keithley_2510('TCPIP0::192.168.2.115::inst5::INSTR')
tec = hi.Keithley_2510('192.168.2.136:8080', 5)
tec.cls
## setting up for error trigger
tec.ESE = 36
tec.SRE = 32
## tec1 = visainst.Newport_3150('TCPIP0::10.75.114.183::inst6::INSTR')
## laserbias = visainst.Keithley2400('TCPIP0::10.75.114.18::inst26::INSTR')
## laserbias.sourcetype('current')
eabias = hi.Keithley_2400('192.168.2.136:8080', 15)
eabias.cls
eabias.ESE = 36
eabias.SRE = 32
eabias.sourcetype('voltage')
## opm = visainst.powermeter('TCPIP0::10.75.114.18::inst4::INSTR')
## dca = visainst.dca('TCPIP0::10.75.114.18::inst7::INSTR')
## micramDAC = uspatools.USPA7201('10.75.61.202', 5017, 'C:/Users/lab6750/Desktop/Test Program/uspatools-0.3.3/uspatools-0.3.3', cd3_installed=True)
## micramDAC.dac_pattern_stop()

## ps = visainst.Agilent_E3631('TCPIP0::192.168.2.95::inst1::INSTR')
#osa = visainst.Agilent_86142('TCPIP0::192.168.2.115::inst11::INSTR')
osa = hi.Agilent_86142('192.168.2.136:8080', 11)
osa.cls
osa.ESE = 36
osa.SRE = 32
# dmm = hi.Agilent_33401('TCPIP0::192.168.2.115::inst28::INSTR')
dmm = hi.Agilent_33401('192.168.2.136:8080', 28)
dmm.cls
dmm.ESE = 36
dmm.SRE = 32
att = hi.JDSU_HA9('192.168.2.136:8080', 21)
# att = hi.JDSU_HA9('TCPIP0::192.168.2.115::inst21::INSTR')

fname = 'input_dc2.xlsx'
datain = pd.read_excel(fname, sheet_name='Sheet1')
datain = datain.astype(np.float64)
## datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']] = datain[['read_temperature','read_EAcurrent','read_Pave','read_ER']].astype(np.float64)

starttime = time.perf_counter()
cnt = 0.
for ind in range(1,50000):            ##

    # eabias.setvoltage(datain['set_EAvoltage'][ind])
    eabias.setvoltage(-cnt * 50e-3)
    eabias.output = 1
    cnt += 1
    cnt %= 100
     ## te4c.settemp(datain['set_temperature'][ind])
    tec.settemp(25.00)
    if ind % 2 == 0:
        tec.output = 1
    else:
        tec.output = 0
    ## laserbias.setcurrent(datain['set_laserCurrent'][ind])

    ## psCurrent = ps.queryCurrent()
    ## print('ps current is ' + str(psCurrent))
    ## osa.startWavelength = 1555e-9
    startwav = osa.startWavelength
    ## osa.stopWavelength
    ## print('start wavelength is %e stop wavelength is %e' % (osa.startWavelength, osa.stopWavelength) )
    ## jkm     time.sleep(0.1)s

    trace = osa.getTrace1(51)
    ary = trace.split(',')
    print(len(ary))
    # tec.settemp(25.00)
    stopwav = osa.stopWavelength

    ## lastChar = ary(len(ary)-1)

    ####print('power supply current is %f' % ps.queryCurrent())
    print('att is %f' % att.attenuation)
    print('beam status is %d' % att.beamIsBlocked)
    ## print('dmm voltage is %e' % dmm.dcCurrent())
    ## print('dmm voltage is %e' % dmm.dcVoltage())

    ## dt = abs(tec.querytemp()-datain['set_temperature'][ind] )
    ##    while (dt>3 ): ##and dt<15
    ##        temp_c = tec.querytemp()
    ##        ##time.sleep(.1)
    ##        dt = abs(temp_c-datain['set_temperature'][ind] )
    ##        print('temp delta ' + str(dt))

    ##    if dt>5 and dt<15:
    ##        print('dt is %f, tec working...'%dt)
    ##        time.sleep(120)
    ##    elif dt >15:
    ##        print('dt is %f, tec working...'%dt)
    ##        time.sleep(300)
    ##    else:
    ##        pass

    ## datain.at[ind,'read_temperature'] = tec1.querytemp()
    datain.at[ind, 'read_temperature'] = tec.querytemp()
    datain.at[ind, 'read_EAcurrent'] = eabias.querycurrent()
    ## datain.at[ind,'read_Pave'] = opm.querypower()
    print('run step %d, total step %d, at temp %.3f' % (ind, max(datain.index), datain.at[ind, 'read_temperature']))
    print('run step %d, total step %d, at current %.6f' % (ind, max(datain.index), datain.at[ind, 'read_EAcurrent']))

print()
print("elapsed time: {}".format(time.perf_counter() - starttime))
writer = pd.ExcelWriter('output_dc.xlsx')
datain.to_excel(writer, 'Sheet1')

## writer = pd.ExcelWriter('output_dc.xlsx')
## datain.to_excel(writer,'Sheet1')

