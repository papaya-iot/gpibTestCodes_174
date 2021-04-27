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

rm = visa.ResourceManager('@py')
DCA = rm.open_resource('TCPIP0::10.75.115.164::inst7::INSTR')
EA_Bias = rm.open_resource('GPIB0::2::INSTR')
PM = rm.open_resource('GPIB0::4::INSTR')
LD_Bias = rm.open_resource('GPIB0::26::INSTR')
TEC = rm.open_resource('GPIB0::5::INSTR')
#AWG = rm.open_resource('TCPIP0::10.75.61.51::inst0::INSTR')
print(DCA.query('*IDN?'))
print(EA_Bias.query('*IDN?'))
print(PM.query('*IDN?'))
print(LD_Bias.query('*IDN?'))
print(TEC.query('*IDN?'))

#EA_Bias.write(':SOUR:FUNC VOLT') # Voltage source
#EA_Bias.write(':SENS:FUNC "CURR:DC"') # Measure Current
#EA_Bias.write(':SENS:CURR:PROT 0.1') #Compliance Current 100 mA
#
#LD_Bias.write(':SOUR:FUNC CURR') # Current source
#LD_Bias.write(':SENS:FUNC "VOLT:DC"') # Measure Voltage
#LD_Bias.write(':SENS:VOLT:PROT 2') #Compliance Voltage 2 V

"""
Parameters initialaziation
"""
VbArray = np.arange(0, -4.05, -0.05) #from -0.5 to -4
I_LD = np.arange(70E-3, 120E-3, 10E-3)
VbArray_T = VbArray.reshape(len(VbArray), 1) #reshape from (N,) to (N,1)
I_LD_T = I_LD.reshape(len(I_LD), 1)
i = 0 # Vbias
j = 0 # I_LD
Pow = np.zeros([len(VbArray), len(I_LD)])
I = np.zeros([len(VbArray), len(I_LD)])

"""
Taking measurement
"""
#TEC.write(':SOUR:TEMP 40')
#TEC.query(':MEAS:TEMP?')
for I_ld in I_LD:
    i = 0
    LD_Bias.write(':SOUR:FUNC CURR') # Current source
    LD_Bias.write(':SENS:FUNC "VOLT"') # Sensing voltage
    LD_Bias.write(':SENS:VOLT:PROT 1.7') # Set compliance voltage to 1.7 V
    LD_Bias.write(':SOUR:CURR:LEV %s'%I_ld)
    time.sleep(1)
    for Vbias in VbArray:
        EA_Bias.write(':SOUR:FUNC VOLT') # Votlage source
        EA_Bias.write(':SENS:FUNC "CURR"') # Sensing current
        EA_Bias.write(':SENS:CURR:PROT 50e-3') # Set compliance current to 40 mA
        EA_Bias.write(':SOUR:VOLT:LEV %s'%Vbias) # Varing bias voltage
        time.sleep(0.4)
        I[i, j] = EA_Bias.query(':FORM:ELEM CURR')
        Pow[i, j] = PM.query('READ:POW?') #read PM power values
#        AWG.write(':VOLT1:LEV %s'%swing)
#        DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
#        time.sleep(15)
#        Eratio[i, j] = DCA.query(':MEASure:EYE:ERATio?') #save ER data
#        DCA.write(':DISK:SIMage:FNAMe "%USER_DATA_DIR%\\Screen Images\\08-15-2017\\Temp_77C_EA_Bias_' + str(Vbias) + '_Swing_' + str(swing) + 'V.jpg"')
#        DCA.write(':DISK:SIMage:SAVE; *OPC?')
        i+=1
    j+=1
    
"""
Saving data
"""   
Filename = 'C:/Users/lab6750/Desktop/Test Program/Results/Tosa_400G_test_v4_70C.csv'
np.savetxt(Filename, np.transpose(I_LD_T), delimiter=',', header = "I_LD (A)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f = open(Filename, 'ba')
np.savetxt(f, np.c_[VbArray_T, Pow], delimiter=',', header = "Vbias (V), Power (dBm)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f.write(b'\n')
np.savetxt(f, np.c_[VbArray_T, I], delimiter=',', header = "Vbias (V), Current (A)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f.write(b'\n')
f.close()
    
"""
1) dP/dV, finding optimum Vbias
2) Computing Vdd_dc for different ER
""" 
Vbias_infl = np.zeros([1, len(I_LD)])
Vpp_dc = np.zeros([1, len(I_LD)])
Err = 0.01 # Define error range for ER
ER_spec = 5 # Specify the desired ER value to calculate the Vpp_dc
X = np.arange(0.01, 0.8, 0.001) # Vpp +/- x
ER = np.zeros([1, len(X)])
j = 0
Pow_mW = 10**(Pow/10) # transform to linear unit
for i in range(len(I_LD)):
    fit = np.polyfit(VbArray, Pow_mW[:, i]/max(Pow_mW[:, i]), 8) # curve fitting Pow_Vbias
    fit_fn = np.poly1d(fit) # fit_fn is the fitted curve
    VbArray_interpolate = np.arange(0, -4.05, -0.01) # adding more points to increase accuracy
    p = np.polyder(fit_fn) # d_Pow/d_vbias
    ind = np.argmax(p(VbArray_interpolate)) # then find the index of the max value
    Vbias_infl[0, j] = VbArray_interpolate[ind]
    plt.plot(VbArray, Pow_mW[:, i]/max(Pow_mW[:, i]), 'r--', VbArray, fit_fn(VbArray), 'r')
    plt.show()
    plt.plot(VbArray, p(VbArray), 'r--', VbArray_interpolate, p(VbArray_interpolate), 'r')
    plt.show()   
###finding Vpp_DC for ER = 4, 5, 6 dB###   
    m = 0
    for x in X:
        ER[0, m] = 10*math.log10(fit_fn(Vbias_infl[0, j] + x)/fit_fn(Vbias_infl[0, j] - x)) # Calculate all ER values at various Vpp_dc
        m+=1
    ind_ER = [i for i in range(len(X)) if abs(ER[0, i] - ER_spec) < Err][0] # Find Vpp_dc at which the ER is closest to desired value
    Vpp_dc[0, j] = 2*X[ind_ER]
    j+=1

"""
Saving data
"""
f = open(Filename, 'ba')
f.write(b'\n')
np.savetxt(f, np.c_[np.transpose(Vbias_infl), np.transpose(Vpp_dc)], delimiter=',', header = "Inflection Point (V), Vpp_dc (V)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f.close()



