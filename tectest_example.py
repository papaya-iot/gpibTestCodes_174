## Varying Vbias, measuring Power, ER ##

# written in python 3.7

"""
Instrument connections
"""
#import visa    # already imported in visainst, i2cinst, uartinst
import papaya_visainst as visainst
import papaya_i2cinst as i2cinst
import papaya_uartinst as uartinst
import time
from importlib import reload # reload the module, ie visainst when it has change when using console

papaya_ip = "192.168.2.197"

## GPIB Instrument Setup
# use VISAInstrument class from visainst.py
tec = visainst.Keithley_2510(papaya_ip, 5)
tec.cls()
# setting up for error trigger
tec.ESE = 36
tec.SRE = 32

eabias = visainst.Keithley_2400(papaya_ip, 15)
eabias.cls()
eabias.ESE = 36
eabias.SRE = 32
eabias.sourcetype('voltage')

osa = visainst.Agilent_86142(papaya_ip, 11)
osa.cls()
osa.ESE = 32
osa.SRE = 32

dmm = visainst.Agilent_33401(papaya_ip, 27)
dmm.cls()
dmm.ESE = 36
dmm.SRE = 32

att = visainst.JDSU_HA9(papaya_ip, 21)

## I2C Instrument Setup
# use I2cConnection class from papaya_i2cinst.py
# initiate new connection, default address 30
conn = i2cinst.I2cConnection(papaya_ip)
devices = conn.scan()
print('devices present: ', devices)
# example class BME280 uses I2cInstrument class
# connect to device at i2c address 0x77
bme280 = i2cinst.BME280(conn, 0x77, 1)

## UART Instrument Setup
# example class Agilent_E3631 uses UartInstrument class
# connect to new uart device, default address 29

pwr = uartinst.Agilent_E3631(papaya_ip)
# set default config: baud rate 9600, 8 numbits, no parity, 1 stopbits,
#             msg timo 5s, byte timo 200000 us
pwr.set_config(9600, 7, 2, 1, 5000, 100000)
time.sleep(2) # allow time for config to process
pwr.write("syst:rem") # needed for inst control using 


## Test Loop
start_time = time.perf_counter()

cnt = 0.    # to change the bias

for ind in range(1, 100):

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
    print('', pwr.queryCurrent())
    print('', pwr.queryVoltage())
    
    print('att is %f' % att.attenuation)
    print('beam status is %d' % att.beamIsBlocked)

    print("elapsed time: {}".format(time.perf_counter() - start_time))
    

print("total elapsed time: {}".format(time.perf_counter() - start_time))

tec.close()
dmm.close()
eabias.close()
att.close()
osa.close()
pwr.close()
conn.close()
