# Varying Vbias, measuring Power, ER #

"""
Instrument connection
"""
import visa
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
import xlsxwriter
from scipy.optimize import curve_fit
from sympy import *

rm = visa.ResourceManager()
DCA = rm.open_resource('TCPIP0::10.75.115.19::inst7::INSTR')
EA_Bias = rm.open_resource('TCPIP0::10.75.115.19::inst2::INSTR')
PM = rm.open_resource('TCPIP0::10.75.115.19::inst4::INSTR')
LD_Bias = rm.open_resource('TCPIP0::10.75.115.19::inst26::INSTR')
TEC = rm.open_resource('TCPIP0::10.75.115.19::inst5::INSTR')
#AWG = rm.open_resource('TCPIP0::10.75.61.51::inst0::INSTR')
print(DCA.query('*IDN?'))
print(EA_Bias.query('*IDN?'))
print(PM.query('*IDN?'))
print(LD_Bias.query('*IDN?'))
print(TEC.query('*IDN?'))
#print(AWG.query('*IDN?'))

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
VbArray = np.arange(-0, -5, -0.2) #from -0.5 to -4
Swing = np.arange(0.15, 0.3, 0.3)
VbArray_T = VbArray.reshape(len(VbArray), 1) #reshape from (N,) to (N,1)
Swing_T = Swing.reshape(len(Swing), 1)
i = 0 # Vbias
j = 0 # Swing
Pow = np.zeros([len(VbArray), len(Swing)])
Eratio = np.zeros([len(VbArray), len(Swing)])
I = np.zeros([len(VbArray), len(Swing)])

"""
Taking measurement
"""
for Vbias in VbArray:
    j = 0
    for swing in Swing:
        
        EA_Bias.write(':SOUR:FUNC VOLT')
        EA_Bias.write(':SENS:FUNC CURR:DC')
        EA_Bias.write('CurrentCompliance = 40e-3')
        EA_Bias.write(':SOUR:VOLT:LEV %s'%Vbias)

inst.write(':SOUR:FUNC CURR')
inst.write(':SENS:FUNC VOLT:DC')      
        
        time.sleep(1)
        I[i, j] = EA_Bias.query(':FORM:ELEM CURR')
        Pow[i, j] = PM.query('READ:POW?') #read PM power values
        AWG.write(':VOLT1:LEV %s'%swing)
        DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
        time.sleep(15)
        Eratio[i, j] = DCA.query(':MEASure:EYE:ERATio?') #save ER data
#        DCA.write(':DISK:SIMage:FNAMe "%USER_DATA_DIR%\\Screen Images\\08-15-2017\\Temp_77C_EA_Bias_' + str(Vbias) + '_Swing_' + str(swing) + 'V.jpg"')
#        DCA.write(':DISK:SIMage:SAVE; *OPC?')
        j+=1
    i+=1
    
"""
dP/dV, finding optimum Vbias
""" 
Pow_mW = 10**(Pow/10) # transform to linear unit
param = curve_fit(func, VbArray[:], Pow_mW[:]) # curve fitting Pow_Vbias
[c1, c2, c3, c4, c5, c6, c7, c8] = param[0] # calculate params
VbArray_interpolate = np.arange(0, -5, -0.01) # adding more points to increase accuracy
ind = np.argmax(func_diff(VbArray_interpolate)) # d_Pow/d_vbias, then find the index of the max value
Vbias = VbArray_interpolate[ind]
plt.plot(VbArray, Pow_mW, 'r--', VbArray, func(VbArray,c1,c2,c3,c4,c5,c6,c7,c8), 'r')
plt.show()
plt.plot(VbArray, func_diff(VbArray), 'r--', VbArray_interpolate, func_diff(VbArray_interpolate), 'r')
plt.show()

"""
Saving data
"""   
Filename = 'C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/Power_vbias_swing_77C_5.csv'
np.savetxt(Filename, np.c_[VbArray_T, Pow], delimiter=',', header = "Vbias (V), Power (dBm)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f = open(Filename, 'a')
f.write('\n')
np.savetxt(f, np.c_[VbArray_T, Eratio], delimiter=',', header = "Vbias (V), ER (dB)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f.write('\n')
np.savetxt(f, np.c_[VbArray_T, I], delimiter=',', header = "Vbias (V), Current (mA)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f.write('\n')
np.savetxt(f, Swing_T, delimiter=',', header = "Swing (mV)", comments = "") #np.c_ is to convert from (M,N) to (N,M)
f.close()
#data = {'VBias': VbArray_T[:,0], 'Power': Pow[:,:]}
#df = pd.DataFrame(data, columns=['VBias', 'Power'])
#writer = pd.ExcelWriter('C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/E02_EA_Bias_25C_w_RF_08_14_2017.xlsx', engine='xlsxwriter')
#df.to_excel(writer, sheet_name='Sheet1')
#
#data = {'VBias': VbArray_T[:,0], 'ER': ER[:,:]}
#df = pd.DataFrame(data, columns=['VBias', 'ER'])
#writer = pd.ExcelWriter('C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/E02_EA_Bias_25C_w_RF_08_14_2017.xlsx', engine='xlsxwriter')
#df.to_excel(writer, sheet_name='Sheet2')
#writer.save()


