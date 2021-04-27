# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 15:38:05 2017

@author: lab6750
"""
#DCA.write(':LTESt:ACQuire:CTYPe:PATTerns 1; :LTESt:ACQuire:STATe ON; *OPC?') # Acquisiation limit to 1
#for v in range(400, 1000, 100):
#    DCA.write(':ACQuire:CDISplay') # Clear screen
#    USPA7201.dac_set_swing(1, v) # v from 350 to 900
#    DCA.write(':ACQuire:RUN; *OPC?') # Click run
#    time.sleep(15)
#    DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
#    time.sleep(15)
#    DCA.write(':DISK:DWIZard:FNAMe "D:/User Files/Screen Images/dca-' + str(v) + '.zip"')
#    DCA.write(':DISK:DWIZard:SAVE; *OPC?')

for v in range(400, 1000, 100):
    DCA.write(':ACQuire:CDISplay') # Clear screen
    USPA7201.dac_set_swing(1, v) # v from 350 to 900
    time.sleep(1)
    DCA.write(':SYSTem:AUToscale;*OPC?') #perform autoscale
    time.sleep(15)
    DCA.write(':DISK:DWIZard:FNAMe "D:/User Files/Screen Images/dca-' + str(v) + '.zip"')
    DCA.write(':DISK:DWIZard:SAVE; *OPC?')