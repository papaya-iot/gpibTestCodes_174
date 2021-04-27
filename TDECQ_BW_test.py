# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 14:46:14 2017

@author: MILDTHSBGLM1
"""

BW = [20E9, 22E9, 24E9, 26.56E9, 38.7E9, 39.84E9]
i = 0
TDECq = np.zeros([len(BW), 1])
for bw in BW:
    DCA.write('CHAN4A:SIRC ON; :CHAN4A:SIRC:FBANdwidth %s'%bw) # Change BW to 26.5625 GHz
    time.sleep(3)
    DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
    time.sleep(10)
    TDECq[i] = read_IO(':MEASure:EYE:TDEQ?')# Wait till value appears, and then read values
    DCA.write(':DISK:SIMage:FNAMe "%USER_DATA_DIR%\\Screen Images\\08-15-2017\\TDECQ_25C_EA_Bias_2.6V_BW_' + str(bw) + '.jpg"')
    DCA.write(':DISK:SIMage:SAVe; *OPC?')
    i+=1
    