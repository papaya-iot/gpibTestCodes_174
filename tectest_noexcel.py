## Varying Vbias, measuring Power, ER ##

# written in python 3.7

"""
Instrument connections
"""
#import visa    # already imported in visainst and i2cinst
import visainst
import i2cinst
import time
# from sympy import *
from importlib import reload # reload the module, ie visainst when it has change when using console

## GPIB Instrument Setup
# use VISAInstrument class from visainst.py
ip = "192.168.2.253"
tec=visainst.Keithley_2510(ip, 5)
tec.cls()
# setting up for error trigger
tec.ESE=36
tec.SRE=32

eabias = visainst.Keithley_2400(ip, 15)
eabias.cls()
eabias.ESE = 36
eabias.SRE = 32
eabias.sourcetype('voltage')

osa = visainst.Agilent_86142(ip, 11)
osa.cls()
osa.ESE=32
osa.SRE=32

dmm = visainst.Agilent_33401(ip, 28)
dmm.cls()
dmm.ESE = 36
dmm.SRE = 32

att = visainst.JDSU_HA9(ip, 21)

## I2C Instrument Setup
# use I2CInstrument class from i2cinst.py
# initiate new connection, default address 30
conn = i2cinst.I2cConnection(ip, 30)
devices = conn.scan()
print('devices present: ', devices)
# create device at i2c address 0x77
bme280 = i2cinst.BME280(conn, 0x77, 1)

## UART Instrument Setup


## Test Loop
starttime = time.perf_counter()

cnt = 0. # to change the bias

for ind in range(1, 2000):

    # GPIB Instruments
    eabias.setvoltage(-cnt*50e-3)
    eabias.output = 1
    cnt +=1
    cnt %= 100
    tec.settemp(25.00)
    if ind % 2 == 0 :
        tec.output = 1
    else:
        tec.output = 0
     
    startwav = float(osa.startWavelength)
    trace = osa.getTrace()
    ary = trace.split(',')
    print(len(ary))
    
    y = [float(c) for c in ary]
    stopwav = float(osa.stopWavelength)

    print('dmm voltage is %e' % dmm.dcVoltage())
    
    print('run step %d, at temp %.3f' % (ind, tec.querytemp()))
    print('run step %d, at current %.6f' % (ind, eabias.querycurrent()))

    # I2C Instrument
    t, p, h = bme280.read_data()
    print('%d  h=%.2f p=%.1f t=%.2f' % (ind, h, p, t))

    # UART Instrument


    print("elapsed time: {}".format(time.perf_counter() - starttime))
    

print("total elapsed time: {}".format(time.perf_counter() - starttime))

tec.close()
dmm.close()
eabias.close()
att.close()
osa.close()


