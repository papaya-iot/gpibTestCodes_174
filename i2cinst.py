import visa
import time


def enforce_int(addr):
    'given hex string or int address, return integer'
    if type(addr) == int:
        return addr
    elif type(addr) == str and '0x' in addr:
        return int(addr, 16)
    else:
        raise ValueError('device address must be int or hex string')


class I2cConnection:

    def __init__(self, ip, gpib_address=30):
        resource_name = "TCPIP0::%s::inst%s::INSTR" % (ip, gpib_address)
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource_name)
        self.instr.timeout = 10000

    def scan(self):
        '''
        scans devices on i2c bus
        :return: list of hex string addresses present on i2c bus
        '''
        # byte[0]: 0x00 for scan cmd
        bytes_to_write = bytes([0])
        try:
            self.instr.write_raw(bytes_to_write)
            bytes_data = self.instr.read_raw(128)
            # bytes_data = self.instr.read_bytes(128)     # can use in pyvisa 1.9.0 and up
            data = list(bytes_data)
            result = [hex(i) for i in range(128) if data[i] == 1]
            return result
        except ValueError:
            print("i2c failed scan")


class I2cDevice:

    def __init__(self, connection, device_address):
        self.instr = connection.instr
        self.addr = enforce_int(device_address)

    def close(self):
        self.instr.close()

    def read(self, reg_addr, len_read):
        '''
        read len_read bytes starting from register reg_addr
        :param reg_addr: (int) register address to read
        :param len_read: (int) number of bytes to read
        :return: bytestring of data
        '''
        # byte[0]: 0x01 for read cmd
        # byte[1]: device address
        # byte[2]: register address
        # byte[3]: length of read data
        assert len_read < 256, "num of bytes to read cannot exceed 255"

        int_reg_addr = enforce_int(reg_addr)
        # ensure address is hex string or int

        bytes_to_write = bytes([0x01, self.addr, int_reg_addr, len_read])
        # print(f"write {hex(self.addr)} reg {hex(int_reg_addr)}: {bytes_to_write}")

        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw(len_read)
            # data = self.instr.read_bytes(len_read)
            # print(f"read  {hex(self.addr)} reg {hex(int_reg_addr)}: {data}")
            return data
        except ValueError:
            print("i2c failed read")

    def write(self, reg_addr, data, len_data=0):
        '''

        :param reg_addr: (int) register address to write to
        :param data: (bytes) data in bytestring
        :param len_data: (optional int) num of bytes in data, can be computed
        :return: success
        '''
        # byte[0]: 0x02 for write cmd
        # byte[1]: device address
        # byte[2]: register address
        # byte[3]: length of write data
        # byte[4:]: bytes of data
        assert len_data < 256, "max 255 bytes exceeded"

        if len_data == 0:   # if default, compute length
            len_data = len(data)

        int_reg_addr = enforce_int(reg_addr)
        # ensure address is hex string or int

        bytes_to_write = bytes([2, self.addr, int_reg_addr, len_data]) + data[:len_data]
        # print(f"write {hex(self.addr)} reg {hex(int_reg_addr)}: {bytes_to_write}")

        try:
            return self.instr.write_raw(bytes_to_write)
        except ValueError:
            print(f"i2c device {hex(self.addr)} failed write")


# example i2c instrument class
# adapted from BME280.py, http://abyz.me.uk/rpi/pigpio/examples.html (2016-08-05)
class BME280(I2cDevice):

    _calib00 = 0x88

    _T1 = 0x88 - _calib00
    _T2 = 0x8A - _calib00
    _T3 = 0x8C - _calib00

    _P1 = 0x8E - _calib00
    _P2 = 0x90 - _calib00
    _P3 = 0x92 - _calib00
    _P4 = 0x94 - _calib00
    _P5 = 0x96 - _calib00
    _P6 = 0x98 - _calib00
    _P7 = 0x9A - _calib00
    _P8 = 0x9C - _calib00
    _P9 = 0x9E - _calib00

    _H1 = 0xA1 - _calib00

    _chip_id = 0xD0
    _reset = 0xE0

    _calib26 = 0xE1

    _H2 = 0xE1 - _calib26
    _H3 = 0xE3 - _calib26
    _xE4 = 0xE4 - _calib26
    _xE5 = 0xE5 - _calib26
    _xE6 = 0xE6 - _calib26
    _H6 = 0xE7 - _calib26

    _ctrl_hum = 0xF2
    _status = 0xF3
    _ctrl_meas = 0xF4
    _config = 0xF5

    _rawdata = 0xF7
    _press = 0xF7
    _temp = 0xFA
    _humid = 0xFD

    _p_msb = 0xF7 - _rawdata
    _p_lsb = 0xF8 - _rawdata
    _p_xlsb = 0xF9 - _rawdata
    _t_msb = 0xFA - _rawdata
    _t_lsb = 0xFB - _rawdata
    _t_xlsb = 0xFC - _rawdata
    _h_msb = 0xFD - _rawdata
    _h_lsb = 0xFE - _rawdata

    _os_ms = [0, 1, 2, 4, 8, 16]

    def __init__(self, i2c_conn, gpib_addr, sampling):
        super().__init__(i2c_conn, gpib_addr)

        # additional initialization procedure
        self.sampling = sampling
        self._load_calibration()
        self.measure_delay = self._measurement_time(sampling, sampling, sampling)
        self.t_fine = 0.0

    def _s16(self, _calib, off):
        v = self._u16(_calib, off)
        if v > 32767:
            v -= 65536
        return v

    def _u16(self, _calib, off):
        return (_calib[off] | (_calib[off + 1] << 8))

    def _u8(self, _calib, off):
        return _calib[off]

    def _s8(self, _calib, off):
        v = self._u8(_calib, off)
        if v > 127:
            v -= 256
        return v

    def _measurement_time(self, os_temp, os_press, os_hum):
        ms = ((1.25 + 2.3 * self._os_ms[os_temp]) +
              (0.575 + 2.3 * self._os_ms[os_press]) +
              (0.575 + 2.3 * self._os_ms[os_hum]))
        return (ms / 1000.0)

    def _load_calibration(self):

        d1 = self.read(self._calib00, 26)

        self.T1 = self._u16(d1, self._T1)
        self.T2 = self._s16(d1, self._T2)
        self.T3 = self._s16(d1, self._T3)
        # print format(self._u8(d1,self._T1),'02x')

        # for index in range(len(d1)):
        #     print(index, format(d1[index], '02x'))

        self.P1 = self._u16(d1, self._P1)
        self.P2 = self._s16(d1, self._P2)
        self.P3 = self._s16(d1, self._P3)
        self.P4 = self._s16(d1, self._P4)
        self.P5 = self._s16(d1, self._P5)
        self.P6 = self._s16(d1, self._P6)
        self.P7 = self._s16(d1, self._P7)
        self.P8 = self._s16(d1, self._P8)
        self.P9 = self._s16(d1, self._P9)

        self.H1 = self._u8(d1, self._H1)

        d2 = self.read(self._calib26, 7)

        self.H2 = self._s16(d2, self._H2)

        self.H3 = self._u8(d2, self._H3)

        t = self._u8(d2, self._xE5)

        t_l = t & 15
        t_h = (t >> 4) & 15

        self.H4 = (self._u8(d2, self._xE4) << 4) | t_l

        if self.H4 > 2047:
            self.H4 -= 4096

        self.H5 = (self._u8(d2, self._xE6) << 4) | t_h

        if self.H5 > 2047:
            self.H5 -= 4096

        self.H6 = self._s8(d2, self._H6)

    def _read_raw_data(self):
        # write control bytes for oversampling config
        self.write(self._ctrl_hum, bytes([self.sampling]), 1)
        self.write(self._ctrl_meas, bytes([self.sampling << 5 | self.sampling << 2 | 1]), 1)
        time.sleep(self.measure_delay)

        # read 8 bytes starting from register self._rawdata
        d = self.read(self._rawdata, 8)

        # print(''.join(format(x, '02x') for x in d))
        msb = d[self._t_msb]
        lsb = d[self._t_lsb]
        xlsb = d[self._t_xlsb]
        raw_t = ((msb << 16) | (lsb << 8) | xlsb) >> 4

        msb = d[self._p_msb]
        lsb = d[self._p_lsb]
        xlsb = d[self._p_xlsb]
        raw_p = ((msb << 16) | (lsb << 8) | xlsb) >> 4

        msb = d[self._h_msb]
        lsb = d[self._h_lsb]
        raw_h = (msb << 8) | lsb

        return raw_t, raw_p, raw_h

    def read_temp(self):
        # write measurement control byte
        self.write(self._ctrl_meas, bytes([self.sampling << 5 | self.sampling << 2 | 1]), 1)
        time.sleep(self.measure_delay)

        # read 3 bytes starting from register self._temp
        d = self.read(self._temp, 3)

        # print(''.join(format(x, '02x') for x in d))
        msb, lsb, xlsb = d
        raw_t = ((msb << 16) | (lsb << 8) | xlsb) >> 4

        var1 = (raw_t / 16384.0 - (self.T1) / 1024.0) * float(self.T2)
        var2 = (((raw_t) / 131072.0 - (self.T1) / 8192.0) *
                ((raw_t) / 131072.0 - (self.T1) / 8192.0)) * (self.T3)

        self.t_fine = var1 + var2

        t = (var1 + var2) / 5120.0
        return t

    def read_data(self):
        raw_t, raw_p, raw_h = self._read_raw_data()

        var1 = (raw_t / 16384.0 - (self.T1) / 1024.0) * float(self.T2)
        var2 = (((raw_t) / 131072.0 - (self.T1) / 8192.0) *
                ((raw_t) / 131072.0 - (self.T1) / 8192.0)) * (self.T3)

        self.t_fine = var1 + var2

        t = (var1 + var2) / 5120.0

        var1 = (self.t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * self.P6 / 32768.0
        var2 = var2 + (var1 * self.P5 * 2.0)
        var2 = (var2 / 4.0) + (self.P4 * 65536.0)
        var1 = ((self.P3 * var1 * var1 / 524288.0) + (self.P2 * var1)) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.P1
        if var1 != 0.0:
            p = 1048576.0 - raw_p
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = self.P9 * p * p / 2147483648.0
            var2 = p * self.P8 / 32768.0
            p = p + (var1 + var2 + self.P7) / 16.0
        else:
            p = 0

        h = self.t_fine - 76800.0

        h = ((raw_h - ((self.H4) * 64.0 + (self.H5) / 16384.0 * h)) *
             ((self.H2) / 65536.0 * (1.0 + (self.H6) / 67108864.0 * h *
                                     (1.0 + (self.H3) / 67108864.0 * h))))

        h = h * (1.0 - self.H1 * h / 524288.0)

        if h > 100.0:
            h = 100.0
        elif h < 0.0:
            h = 0.0

        return t, p, h