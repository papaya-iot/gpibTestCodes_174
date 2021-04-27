import visa
import papaya_i2cinst as i2cinst
import papaya_i2chttpinst as i2chttp
import time

### USING VXI11
# initiate new connection, default address 30
conn = i2cinst.I2cConnection("192.168.2.105")
devices = conn.scan()
print('devices present: ', devices)

# create device at i2c address 0x77
bme280 = i2cinst.BME280(conn, 0x77, 1)

# read 4 bytes from _ctrl_hum register
# print(bme280.read(0xf2, 4))
# print(bme280.read(0xfa, 3))

start_time = time.perf_counter()
for i in range(100):
    t, p, h = bme280.read_data()
    print('%d  h=%.2f p=%.1f t=%.2f' % (i, h, p, t))
print('vxi11 elapsed time: ', time.perf_counter() - start_time)
conn.close()


#### USING HTTP
print(i2chttp.scanI2c('192.168.2.105'))
bme280_http = i2chttp.BME280('192.168.2.105', 0x77, 1)
# bme280_http = i2chttp.I2cHttpDevice('192.168.2.105', '77', 1)  # this way works to inherit only r/w methods

print(bme280_http.read('0xf2', 4))

start_time = time.perf_counter()
for i in range(100):
    t, p, h = bme280_http.read_data()
    print('%d  h=%.2f p=%.1f t=%.2f' % (i, h, p, t))
print('http elapsed time: ', time.perf_counter() - start_time)
