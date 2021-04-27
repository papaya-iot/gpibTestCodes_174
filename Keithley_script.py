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
Parameters initialaziation
"""
VbArray = np.arange(-0, -5, -0.2) #from -0.5 to -4
VbArray_T = VbArray.reshape(len(VbArray), 1) #reshape from (N,) to (N,1)
ii = 0
Pow=np.zeros([len(VbArray),1])
Result = np.zeros([len(VbArray),1])

"""
Taking measurement
"""
for Vbias in VbArray:
    EA_Bias.write(':SOUR:VOLT:LEV %s'%Vbias)
    time.sleep(1)
    Pow[ii] = PM.query('READ:POW?') #read PM power values
    ##DCA.write(':MEASure:EYE:ERATio') #perform ER measurement
#    DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
#    time.sleep(15)
#    Result[ii] = DCA.query(':MEASure:EYE:ERATio?') #save ER data
#    DCA.write(':DISK:SIMage:FNAMe "%USER_DATA_DIR%\\Screen Images\\08-10-2017\\Temp_77C_EA_Bias_' + str(Vbias) + '.jpg"')
#    DCA.write(':DISK:SIMage:SAVE; *OPC?')
    ii+=1
    
"""
Saving data
"""    
#np.savetxt('C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/E02_EA_Bias_P_25.csv',np.c_[VbArray_T, Pow],delimiter=',') #np.c_ is to convert from (M,N) to (N,M)
data = {'VBias': VbArray_T[:,0], 'Power': Pow[:,0], 'ER': Result[:,0]}
df = pd.DataFrame(data, columns=['VBias', 'Power', 'ER'])
writer = pd.ExcelWriter('C:/Users/MILDTHSBGLM1.LI/Desktop/Test Program/Results/E02_EA_Bias_25C_w_RF_08_11_2017_2.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')
writer.save()


