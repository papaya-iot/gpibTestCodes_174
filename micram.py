# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 09:18:14 2017

@author: CMPLR22
"""

import uspatools
import numpy as np
import pandas as pd


USPA7201 = uspatools.USPA7201('10.75.61.202', 5017, 'C:/Users/lab6750/Desktop/Test Program/uspatools-0.3.3/uspatools-0.3.3', cd3_installed=True)

USPA7201.dac_set_swing(1, 500)
USPA7201.dac_set_samplerate(1, 53.125e9) 
USPA7201.dac_adj_dutycycle(1)
USPA7201.dac_sync(1)

path='C:/Users/lab6750/Desktop/Test Program/uspatools-0.3.3/uspatools-0.3.3/'
pattern = np.loadtxt(path+"32768sym_PRBS16.txt")
pattern = np.repeat(pattern, 2) # Reduce data rate from 53.125G to 26.5625G
#pattern=[-1,-0.33,0.33,1]

pattern = np.loadtxt(path+"prbs13_2sps.txt")
pattern= np.array(pattern)
USPA7201.dac_pattern_load(1, pattern)
USPA7201.dac_pattern_start()



USPA7201.dac_set_swing(1, 400)
USPA7201.dac_pattern_stop()
USPA7201.dac_pattern_start()
fir=[0,1,0]
#fir=[-0.069597, 1.170860, -0.101263]
fir=[-0.166071, 1.397520, -0.231449]
fir=fir/np.sum(np.abs(fir))
USPA7201.dac_pattern_load(1, pattern,fir)
USPA7201.dac_pattern_start()