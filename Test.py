# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\11FL942.LI\.spyder2\.temp.py
"""

import visa
import numpy as np
import matplotlib.pyplot as plt
import time

import pyvisa as py

rm = py.visa.resource_manager()
py.visa.get_instruments_list()
DCA=py.visa.instrument('GPIB1::7::INSTR')
#rm.list_resources()

print(DCA.ask('*IDN?'))
