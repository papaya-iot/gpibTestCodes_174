# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 14:06:02 2017

@author: lab6750
"""







import numpy as np
import time
import visainst


vbcontrol=visainst.smu()
pm = visainst.powermeter()

def sweepvb(VbArray):
    I = []
    Pow = []
        
    VbArray=np.array(VbArray)
    for ii in range(len(VbArray)):        
        Vbias = VbArray[ii]
        time.sleep(0.4)
        vbcontrol.setvol(Vbias,curlimit=50e-3)
        I.append( float(vbcontrol.querycur()) )#read PM power values
        Pow.append(float(pm.querypower()))
#        Pow=Pow.append(tep)
#        AWG.write(':VOLT1:LEV %s'%swing)
#        DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
#        time.sleep(15)
#        Eratio[i, j] = DCA.query(':MEASure:EYE:ERATio?') #save ER data
#        DCA.write(':DISK:SIMage:FNAMe "%USER_DATA_DIR%\\Screen Images\\08-15-2017\\Temp_77C_EA_Bias_' + str(Vbias) + '_Swing_' + str(swing) + 'V.jpg"')
#        DCA.write(':DISK:SIMage:SAVE; *OPC?')
#        i+=1
    return I,Pow

def sweepld(curarray):
    