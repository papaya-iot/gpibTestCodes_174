# -*- coding: utf-8 -*-
"""
Instrument connection
"""
import visa
import read_IO
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

ERatio = 0
Linearity = 0
TDECq = 0

"""set DCA-X scope"""
DCA.write('ACQuire:CDISplay') # Clear display
DCA.write(':TRIGger:MODE CLOCK') # Set trigger mode
DCA.write(':TIMebase:SRATe 5.3125000E+10') # Set data rate
DCA.write(':TRIGger:PLENgth 32768') # Set pattern length
DCA.write(':TRIGger:DCDRatio SUB8') # Set clock rate
DCA.write(':TRIGger:PLOCK On; *OPC?') # Turn on pattern lock
DCA.write(':PTIMebase1:STATe On; *OPC?') # Turn on Precision Timebase
DCA.write('CHAN4A:DISPlay ON') # Turn on channel 4

"""perform FFE"""
DCA.write('FUNCtion1:FOPerator FFEQualizer') # Enable FFE
DCA.write('FUNCtion1:OPERand1 CHAN4A') # Choose Channel 4 as input
DCA.write('FUNCtion1:DISPlay ON; *OPC?') # Assign a function display port
DCA.write('SPRocess1:FFEQualizer:TAPS:COUNt 3; *OPC?') # Set FFE number of taps
DCA.write('SPRocess1:FFEQualizer:NPRecursors 1; *OPC?') # Set FFE number of precursors
DCA.write('CHAN4A:SIRC ON; :CHAN4A:SIRC:FRATe 5.312500E+10') #Set rate to 53.125GBaud
DCA.write(':DISPlay:WINDow:Time1:DMODe STILed') # Adjust display window
DCA.write(':MEASure:EYE:PAM:LINearity') # Get linearity
DCA.write(':MEASure:EYE:OER') # Get outer ER

"""perform TDECQ"""
DCA.write('FUNCtion1:FOPerator TEQualizer; *OPC?') # Enable TDECQ 
DCA.write('SPRocess1:TEQualizer:TSPacing:TPUI 1; *OPC?') # Set taps per UI
DCA.write('SPRocess1:TEQualizer:TAPS:COUNt 5; *OPC?') # Set number of taps
DCA.write('SPRocess1:TEQualizer:NPRecursors 2; *OPC?') # Set number of precursors
DCA.write(':MEASure:Eye:TDEQ:SOURce1 FUNCtion1') # Perform TDECQ on function 1
DCA.write('CHAN4A:SIRC ON; :CHAN4A:SIRC:FBANdwidth 2.656E+10') # Change BW to 26.5625 GHz
DCA.write(':MEASure:EYE:TDEQ') # Take TDEQ measurement

#DCA.write(':DISK:DWIZard:FNAMe "%USER_DATA_DIR%\Screen Images\08-02-2017\TDECQ_25C_EA_Bias_2.6V_test.zip"')
#DCA.write(':DISK:DWIzard:SAVe; *OPC?')

DCA.write(':MEASure:EYE:OER:SOURce1 CHAN4A') # Specify which eye to measure
ERatio = read_IO(':MEASure:EYE:OER?') # Wait till value appears, and then read values
Linearity = read_IO(':MEASure:EYE:PAM:LINearity?') # Wait till value appears, and then read values
DCA.write(':MEASure:EYE:TDEQ:SOURce1 FUNCtion1') # Specify which eye to measure
TDECq = read_IO(':MEASure:EYE:TDEQ?')# Wait till value appears, and then read values
