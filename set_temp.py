# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 18:51:27 2017

@author: lab6750
"""
def set_temp(x):
    Err = 0.005
    TEC.write(':SOUR:TEMP ' + str(x))
    time.sleep(60)
    while 1:
        if float(TEC.query(':MEAS:TEMP?')) - x < Err:
            break
    return TEC.query(':MEAS:TEMP?')