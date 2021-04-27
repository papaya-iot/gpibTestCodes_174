# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 11:53:30 2017

@author: MILDTHSBGLM1
"""
def read_IO(x):
    while 1:
        if float(DCA.query(x)) != 9.91E+37:
            break
    return DCA.query(x)