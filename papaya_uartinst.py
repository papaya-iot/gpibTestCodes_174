"""
Copyright (C) 2020 Piek Solutions LLC

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import visa
import time


class UartInstrument:

    def __init__(self, ip):
        # gpib address 29 is hardcoded for UART
        resource_name = "TCPIP0::%s::inst29::INSTR" % ip
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource_name)
        self.instr.timeout = 10000

    def close(self):
        self.instr.close()

    def read(self):
        '''
        read from uart device
        :return: response string from device
        '''
        # byte[0]: 0x01 for query cmd
        # byte[1]: length of query cmd
        # byte[2:]: bytes of command string
        
        len_cmd = 0
        bytes_to_write = bytes([0x01]) + len_cmd.to_bytes(2, 'little') 
        #print(bytes_to_write, len(bytes_to_write))
        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw()
            return data
        except ValueError:
            print("uart failed read")


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
            data = self.instr.read_raw()
            # print(data)
            return data
        except ValueError:
            print("uart failed query")

    def queryBytes(self, command):
        '''
        query uart device with hex coded command string, adding newline to the end
        :param command: (string) hex encoded command string, ex: '02c9'
        :return: response string from device
        '''
        # byte[0]: 0x01 for query cmd
        # byte[1]: length of query cmd
        # byte[2:]: bytes of command string

        cmd = bytes.fromhex(command)
        len_cmd = len(cmd) + 1
        data_bytes = cmd + bytes([0x0a])    # cmd bytes and newline
        bytes_to_write = bytes([0x01]) + len_cmd.to_bytes(2, 'little') + data_bytes
        print(bytes_to_write, len(bytes_to_write))

        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw()
            # print(data)
            return data
        except ValueError:
            print("uart failed queryBytes")
            
    def queryBytesRaw(self, command):
        '''
        query uart device with hex coded command string
        :param command: (string) hex encoded command string, ex: '02c9'
        :return: response string from device
        '''
        # byte[0]: 0x01 for query cmd
        # byte[1]: length of query cmd
        # byte[2:]: bytes of command string

        cmd = bytes.fromhex(command)
        len_cmd = len(cmd) 
        data_bytes = cmd     # cmd bytes wo newline
        bytes_to_write = bytes([0x01]) + len_cmd.to_bytes(2, 'little') + data_bytes
        #print(bytes_to_write, len(bytes_to_write))

        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw()
            # print(data)
            return data
        except ValueError:
            print("uart failed queryBytesRaw")

    def write(self, command):
        '''
        write command string to uart instrument adding newline to the end
        :param command: (str)
        :return: None
        '''
        # byte[0]: 0x02 for write cmd
        # byte[1]: length of write cmd
        # byte[2:]: bytes of command string

        len_cmd = len(command) + 1
        data_bytes = command.encode('utf-8') + bytes([0x0a])
        bytes_to_write = bytes([2]) + len_cmd.to_bytes(2, 'little') + data_bytes
        # print(f"write {hex(self.addr)} reg {hex(int_reg_addr)}: {bytes_to_write}")
        #print(bytes_to_write)

        try:
            self.instr.write_raw(bytes_to_write)
        except ValueError:
            print("uart failed write")

    def writeBytes(self, command):
        '''
        write hex coded command string to uart instrument, append a newline by default
        :param command: (string) hex encoded command string, ex: '02c9'
        :return: None
        '''
        # byte[0]: 0x02 for write cmd
        # byte[1]: length of write cmd
        # byte[2:]: bytes of command string

        cmd = bytes.fromhex(command)
        len_cmd = len(cmd) + 1
        data_bytes = cmd + bytes([0x0a])
        bytes_to_write = bytes([2]) + len_cmd.to_bytes(2, 'little') + data_bytes
        #print(bytes_to_write)

        try:
            self.instr.write_raw(bytes_to_write)
        except ValueError:
            print("uart failed writeBytes")
            
    def writeBytesRaw(self, command):
        '''
        write hex coded command string to uart instrument
        :param command: (string) hex encoded command string, ex: '02c9'
        :return: None
        '''
        # byte[0]: 0x02 for write cmd
        # byte[1]: length of write cmd
        # byte[2:]: bytes of command string

        cmd = bytes.fromhex(command)
        len_cmd = len(cmd) 
        data_bytes = cmd     # cmd bytes wo newline
        bytes_to_write = bytes([2]) + len_cmd.to_bytes(2, 'little') + data_bytes
        print(bytes_to_write)

        try:
            self.instr.write_raw(bytes_to_write)
        except ValueError:
            print("uart failed writeBytesRaw")
            
# =============================================================================
# Both Byte Timeout(us) and Msg Timeout (ms) are related to reading from the RS232 interface. 
# The users will need to change the default values when they are reading a large amount of data 
# or an instrument that is slow to respond (ie slow measurement etc.). The default Msg Timeout(ms) 
# is set to 5000ms or 5s: any read operation on the RS232 will wait for 5s for data to be 
# available on the RxD line before it timeout and finishes. 
# 
# Byte Timeout(us) is related to the read duration to read data on the RxD line. When it is set 
# to 100000us or 0.1s, the RxD line is read for 0.1s, even if all the data that has been transmitted
# has been read before the 0.1s interval is complete. For example, 
# if the data to be read in is not small, then the Byte Timeout(us) should be set to a small value to 
# improve the response time. On the other hand, when reading in a large amount of data, 
# the users will need to increase the Byte Timeout (us) to a few seconds in order to completely read 
# in the data. Note that the Byte Timeout value also depends on the baud rate.
# 
# =============================================================================

    def set_config(self, data_rate, num_bits, parity, stop_bits, msg_timeout, byte_timeout):
        '''
        set uart configuration
        :param data_rate: (int) baud rate
        :param num_bits: (int) number of bits in a message (7 or 8)
        :param parity: (int) 0=None, 1=Odd, 2=Even
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
            #print(list(bytes_to_write))
            return self.instr.write_raw(bytes_to_write)
        except ValueError:
            print("uart device failed write")

    def get_config(self):
        '''
        read config from uart device
        :return: dictionary of config values
        '''
        len_data = 0
        len_data_bytes = len_data.to_bytes(2, 'little')
        bytes_to_write = bytes([0x04]) + len_data_bytes

        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw()
            # print(data)

            # print(int.from_bytes(data[0:1], 'little'))  # read uart config byte
            # print(int.from_bytes(data[1:3], 'big'))     # length of data

            # bit7, bit6, bit5, bit4 | bit3, bit2, bit1 | bit0
            # RS_CHAR_8              | RS_PARITY_NONE   | RS_STOP_1
            config_byte = data[3]
            numbits = ((config_byte & 0xf0) >> 4) + 5
            parity = (config_byte & 0x06) >> 1
            stopbits = (config_byte & 0x01)

            baud = int.from_bytes(data[4:8], 'little')
            m_timo = int.from_bytes(data[8:12], 'little')
            b_timo = int.from_bytes(data[12:16], 'little')

            config = {
                "baud": baud,
                "numbits": numbits,
                "parity": parity,
                "stopbits": stopbits,
                "m_timo": m_timo,
                "b_timo": b_timo
            }

            return config
        except ValueError:
            print("uart failed read")


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

    def selectPowerSupply(self,x):
        try:
            #select instrument
            # 1 is P6V, 2 is P25V and 3 is N25V
            cmd = 'INST:NSEL ' + str(x)
            self.write(cmd)
        except ValueError:
            print('Agilent E3631 selct PS fails')
            
    def setP6VSupply(self,x):
        try:
            # P6V is 1
            self.write('INST:NSEL 1')
            cmd = 'volt ' + str(x)
            self.write(cmd)
        except ValueError:
            print('Agilent E3631 selct PS fails')
    
    def queryP6VSetVoltage(self):
        try:
            # P6V is 1
            self.write('INST:NSEL 1')
            time.sleep(0.3) # consecutive is too fast for uart
            val = self.query('volt?')
        except ValueError:
            print('Agilent E3631 selct PS fails')
        return float(val)
    
    def setP25VSupply(self,x):
        try:
            # P25V is 2
            self.write('INST:NSEL 2')
            cmd = 'volt ' + str(x)
            self.write(cmd)
        except ValueError:
            print('Agilent E3631 selct PS fails')
    
    def queryP25VSetVoltage(self):
        try:
            # P6V is 1
            self.write('INST:NSEL 2')
            time.sleep(0.3) # consecutive is too fast for uart
            val = self.query('volt?')
        except ValueError:
            print('Agilent E3631 selct PS fails')
        return float(val)
    
    def setN25VSupply(self,x):
        try:
            # P6V is 1
            self.write('INST:NSEL 3')
            cmd = 'volt ' + str(x)
            self.write(cmd)
        except ValueError:
            print('Agilent E3631 selct PS fails')
    
    def queryN25VSetVoltage(self):
        try:
            # P6V is 1
            self.write('INST:NSEL 3')
            time.sleep(0.3) # consecutive is too fast for uart
            val = self.query('volt?')
        except ValueError:
            print('Agilent E3631 selct PS fails')
        return float(val)
    
  