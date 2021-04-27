import visa
import papaya_uartinst as uartinst
import time

# initiate new uart device
pwr = uartinst.Agilent_E3631("192.168.2.105")

# set default config: baud rate 9600, 8 numbits, no parity, 1 stopbits,
#             byte timo 100000 us, msg timo 5s
pwr.set_config(9600, 8, 0, 1, 100000, 5000)
time.sleep(2)   # allow time for config to process

# instrument must be set to remote mode
pwr.write("syst:rem")
time.sleep(1)
# print(pwr.query("syst:err?"))

for i in range(100):
    print('step %d' % i)
    print('\t', pwr.queryCurrent())
    print('\t', pwr.queryVoltage())

pwr.close()
