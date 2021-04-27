import visa


class UartInstrument:

    def __init__(self, ip, gpib_address=29):
        resource_name = "TCPIP0::%s::inst%s::INSTR" % (ip, gpib_address)
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource_name)
        self.instr.timeout = 10000

    def close(self):
        self.instr.close()

    def query(self, command):
        '''
        query uart device with command string, adding newline to the end
        :param command: (str)
        :return: response string from device
        '''
        # byte[0]: 0x01 for query cmd
        # byte[1]: length of query cmd
        # byte[2:]: bytes of command string

        len_cmd = len(command) + 1
        data_bytes = command.encode('utf-8') + bytes([0x0a])    # cmd bytes and newline
        bytes_to_write = bytes([0x01]) + len_cmd.to_bytes(2, 'little') + data_bytes
        # print(bytes_to_write, len(bytes_to_write))

        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read()
            # print(data)
            return data
        except ValueError:
            print("uart failed query")

    def write(self, command):
        '''
        write command string to uart instrument
        :param command: (str)
        :return: success
        '''
        # byte[0]: 0x02 for write cmd
        # byte[1]: length of write cmd
        # byte[2:]: bytes of command string

        len_cmd = len(command) + 1
        data_bytes = command.encode('utf-8') + bytes([0x0a])
        bytes_to_write = bytes([2]) + len_cmd.to_bytes(2, 'little') + data_bytes
        # print(f"write {hex(self.addr)} reg {hex(int_reg_addr)}: {bytes_to_write}")
        print(bytes_to_write)

        try:
            return self.instr.write_raw(bytes_to_write)
        except ValueError:
            print(f"uart failed write")

    def set_config(self, data_rate, num_bits, parity, stop_bits, msg_timeout, byte_timeout):
        '''
        set uart configuration
        :param data_rate: (int) baud rate
        :param num_bits: (int) number of bits in a message (7 or 8)
        :param parity: (int) 0=None, 1=odd, 2=even
        :param stop_bits: (int) stopbit value
        :param msg_timeout: (int) message timeout in ms
        :param byte_timeout: (int) byte read timeout in us
        :return:
        '''
        # byte[0]: 0x03 for config
        # byte[1]: data length
        # byte[2:]: configUart(byteConfig - bitnums, parity, stop,
        #          (int) baudrate, (int) msgtimeout, (int) bytetimeout)

        cmd_byte = bytes([0x03])
        len_data = 13
        len_data_bytes = len_data.to_bytes(2, 'little')
        config_byte = bytes([(0x02 if num_bits == 7 else 0x03) << 0x04 | parity << 0x01 | stop_bits-1])
        # bit7, bit6, bit5, bit4 | bit3, bit2, bit1 | bit0
        # RS_CHAR_8              | RS_PARITY_NONE   | RS_STOP_1
        data_rate_bytes = data_rate.to_bytes(4, 'little')
        msg_timo_bytes = msg_timeout.to_bytes(4, 'little')
        byt_timo_bytes = byte_timeout.to_bytes(4, 'little')

        bytes_to_write = cmd_byte + len_data_bytes + config_byte + data_rate_bytes + \
                         msg_timo_bytes + byt_timo_bytes

        try:
            print(list(bytes_to_write))
            return self.instr.write_raw(bytes_to_write)
        except ValueError:
            print(f"i2c device {hex(self.addr)} failed write")


class Agilent_E3631(UartInstrument):
    def _get_outPutOnOff(self):
        try:
            resp = self.query(':outp?')
            self._startWavelength = int(resp)
        except ValueError:
            print('Agilent E3631 query fails')
        return self._outpuOnOff

    def _set_outPutOnOff(self, x):
        try:
            cmd = 'outp ' + str(x)
            self.write(cmd)
        except ValueError:
            print('Agilent E3631 write fails')
        self._outpuOnOff = x

    outputOnOff = property(_get_outPutOnOff, _set_outPutOnOff, "outputOnOff property")

    def queryCurrent(self):
        try:
            resp = self.query(':meas:curr:dc?')
        except ValueError:
            print('Agilent E3631 query failure')
        return float(resp)

    def queryVoltage(self):
        try:
            resp = self.query(':meas:volt:dc?')
        except ValueError:
            print('Agilent E3631 query failure')
        return float(resp)
