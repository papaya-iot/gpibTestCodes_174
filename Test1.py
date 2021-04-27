# -*- coding: utf-8 -*-
"""
Instrument connection
"""
import visa
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
import xlsxwriter

rm = visa.ResourceManager()
DCA = rm.open_resource('GPIB4::7::INSTR')
EA_Bias = rm.open_resource('GPIB4::10::INSTR')
PM = rm.open_resource('GPIB4::21::INSTR')
LD_Bias = rm.open_resource('GPIB4::28::INSTR')
TEC = rm.open_resource('GPIB4::30::INSTR')
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
Initialaziation
"""
VbArray = np.arange(-1, -3, -1) #from -0.5 to -4
VbArray_T = VbArray.reshape(len(VbArray), 1) #reshape from (N,) to (N,1)
ii = 0
Pow=np.zeros([len(VbArray),1])
Result = np.zeros([len(VbArray),1])

DCA.write('ACQuire:CDISplay') # Clear display
DCA.write(':TRIGger:MODE CLOCK') # Set trigger mode
DCA.write(':TIMebase:SRATe 5.3125000E+10') # Set data rate
DCA.write(':TRIGger:PLENgth 32768') # Set pattern length
DCA.write(':TRIGger:DCDRatio SUB8') # Set clock rate
DCA.write(':TRIGger:PLOCK On; *OPC?') # Turn on pattern lock
DCA.write(':PTIMebase1:STATe On; *OPC?') # Turn on Precision Timebase

DCA.write('FUNCtion1:FOPerator FFEQualizer') # Enable FFE
DCA.write('FUNCtion1:OPERand1 CHAN4A') # Choose Channel 4 as input
DCA.write('FUNCtion1:DISPlay ON; *OPC?') # Assign a function display port
DCA.write('SPRocess1:FFEQualizer:TAPS:COUNt 3; *OPC?') # Set FFE number of taps
DCA.write('SPRocess1:FFEQualizer:NPRecursors 1; *OPC?') # Set FFE number of precursors

DCA.write('FUNCtion1:FOPerator TEQualizer; *OPC?') # Enable TDECQ 
DCA.write('SPRocess1:TEQualizer:TSPacing:TPUI 1; *OPC?') # Set taps per UI
DCA.write('SPRocess1:TEQualizer:TAPS:COUNt 5; *OPC?') # Set number of taps
DCA.write('SPRocess1:TEQualizer:NPRecursors 2; *OPC?') # Set number of precursors


"""
Taking measurement
"""
for Vbias in VbArray:
    EA_Bias.write(':SOUR:VOLT:LEV %s'%Vbias)
    time.sleep(1)
    Pow[ii] = PM.query('READ:POW?') #read PM power values
    #DCA.write(':MEASure:EYE:ERATio') #perform ER measurement
    DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
    time.sleep(1)
    Result[ii] = DCA.query(':MEASure:EYE:ERATio?') #save ER data
    ii+=1
    
"""
Saving data
"""    
#np.savetxt('C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/E02_EA_Bias_P_25.csv',np.c_[VbArray_T, Pow],delimiter=',') #np.c_ is to convert from (M,N) to (N,M)
data = {'VBias': VbArray_T[:,0], 'Power': Pow[:,0], 'ER': Result[:,0]}
df = pd.DataFrame(data, columns=['VBias', 'Power', 'ER'])
writer = pd.ExcelWriter('C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/test.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.save()
