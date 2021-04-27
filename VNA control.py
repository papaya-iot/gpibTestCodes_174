# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 10:10:26 2015

@author: FPJGZ12
"""

import visa
import numpy as np
import matplotlib.pyplot as plt
import time

rm=visa.ResourceManager()
VNA=rm.open_resource('GPIB0::8::INSTR')
Keithly=rm.open_resource('GPIB0::6::INSTR')
PM=rm.open_resource('GPIB0::7::INSTR')
VNA.query('*IDN?')
Keithly.query('*IDN?')

Keithly.write(':SOUR:FUNC VOLT')
Keithly.write(':SOURce:VOLTage:MODE FIXed')
Keithly.write(':SOUR:VOLT:RANG 5')
Keithly.write(':SOUR:VOLT:LEV %d'%-1)

PM.ask('READ:POW?')

#VNA.write('BSP 1000000')   #stop freq
#VNA.write('BST 1000000000')   #start freq
#VNA.write('CNTR 1000000')   #cneter freq
#VNA.write('CWF 1000000')   #CW freq
#VNA.write('CWON 0/1')   #0 for off, 1 for on,
#VNA.ask('BSP?')
#VNA.ask('DAT?')
#VNA.write('OUTPDATA')

VNA.write("LANG NATIVE\n");
VNA.write(":SENSE:SWEEP:POINTS 2001\n");
VNA.write(":FORM:SNP:FREQ HZ\n");
VNA.write(":FORM:SNP:PAR REIM\n");

VNA.write(':CALC1:EXTR:SXPP:PORT12')

VNA.write("TRS;WFS;OS2P\n");
Response=VNA.read()
ResponseS=Response.split('\n')
fileHandle=open('C:\Dave.s4p','w')
fileHandle.write(Response)

Temp='15C'
VbArray=[-0.5,-0.75,-1,-1.25,-1.5,-2,-2.5,-3,-3.5,-4] # 15C
#VbArray=[-0.5,-0.75,-1,-1.25,-1.5,-1.75,-2,-2.5,-3] # 50C
#VbArray=[-0.5,-0.6,-0.7,-0.8,-0.9,-1,-1.1,-1.2,-1.3,-1.5,-1.75,-2,-2.5] # 82C

ii=0
Pow=np.zeros([len(VbArray),1])
for Vbias in VbArray:
    
    Keithly.write(':SOUR:VOLT:LEV %s'%Vbias)
    time.sleep(0.5)
    Pow[ii]=PM.ask('READ:POW?')
    
#    VNA.write("TRS;WFS;OS2P\n");
    VNA.write("TRS;WFS;OS4P\n")
    time.sleep(5)
#    Response=VNA.read()
#    VNA.write(":MMEM:STOR:MDATA 'C:/1111/test002.s4p'")  
    Fname="'C:/1111/"+Temp+str(Vbias)+".s4p'"
    tep=VNA.ask(':CALC:DATA:FDAT?')  # to query VNA data to memory
    VNA.write(":MMEM:STOR:MDATA %s"%Fname) # to save S file to local machine

    ii+=1
    
np.savetxt('C:/Chip2Pow15C.csv',Pow,delimiter=",")
    
    




#F_Start=70e3
#F_Stop=20e6
#NumPoint=2001
#F_axis=np.linspace(F_Start,F_Stop,NumPoint)
#
#VNA.write('CH3')  # S21
#a=VNA.ask(':CALC:DATA:FDAT?')
#a=a.encode('utf-8')
#a=a[11:-1]
#a=a.split('\n')
#
#
#for ii in range(len(a)):
#    a[ii]=a[ii].split(',')
#a=np.array(a)
##for ii in range(np.shape(a)[1]):
##    a[:,ii]=[float(x) for x in a[:,ii]]
#    
#data=np.zeros([NumPoint,3]);data[:,0]=F_axis;data[:,1:3]=a

