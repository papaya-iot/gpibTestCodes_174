## Varying Vbias, measuring Power, ER ##

# written in python 3.7

"""
Instrument connections
"""
#import visa    # already imported in visainst, i2cinst, uartinst
import time
import papaya_httpinst as hi
import papaya_i2chttpinst as i2cinst
import papaya_uarthttpinst as uartinst

## import uspatools

papaya_ip = '192.168.2.105'

tec = hi.Keithley_2510(papaya_ip, 5)
tec.cls()
## setting up for error trigger
tec.ESE = 36
tec.SRE = 32

eabias = hi.Keithley_2400(papaya_ip, 15)
eabias.cls()
eabias.ESE = 36
eabias.SRE = 32
eabias.sourcetype('voltage')

osa = hi.Agilent_86142(papaya_ip, 11)
osa.cls()
osa.ESE = 36
osa.SRE = 32

dmm = hi.Agilent_33401(papaya_ip, 28)
dmm.cls()
dmm.ESE = 36
dmm.SRE = 32

att = hi.JDSU_HA9(papaya_ip, 21)

## I2C HTTP Setup
print(i2cinst.scanI2c('192.168.2.105'))
bme280 = i2cinst.BME280('192.168.2.105', 0x77, 1)
# bme280 = I2cHttpDevice('192.168.2.105', '77')  # this way works too

## UART HTTP Setup
pwr = uartinst.Agilent_E3631('192.168.2.105')
pwr.set_config(9600, 7, 2, 1, 100000, 5000)
print(pwr.get_config())

# start measurement loop
start_time = time.perf_counter()
cnt = 0.
for ind in range(1, 500):

    eabias.setvoltage(-cnt*50e-3)
    eabias.output = 1
    cnt += 1
    cnt %= 100
    # tec.settemp(25.00)
    # if ind % 2 == 0 :
    #     tec.output = 1
    # else:
    #     tec.output = 0

    startwav = osa.startWavelength
    trace = osa.getTrace()
    ary = trace.split(',')
    print(len(ary))
    y = [float(c) for c in ary]
    stopwav = osa.stopWavelength

    # I2C read data
    t, p, h = bme280.read_data()
    print('h=%.2f p=%.1f t=%.2f' % (h, p, t))

    # UART read data
    print('', pwr.queryCurrent())
    print('', pwr.queryVoltage())

    print('att is %f' % att.attenuation)
    print('dmm voltage is %e' % dmm.dcVoltage())

    # print('run step %d, at temp %.3f' % (ind, tec.querytemp()))
    print('run step %d, at current %.6f' % (ind, eabias.querycurrent()))

    print("elapsed time: {}".format(time.perf_counter() - start_time))

print("total elapsed time: {}".format(time.perf_counter() - start_time))
