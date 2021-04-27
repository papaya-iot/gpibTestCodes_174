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
# 

class SpiInstrument:

    _csMode = 1
    _csVal = 0
    _clkDiv = 12
    _bits2shift = 8
    _msb_first = 1
    _pol = 0
    _pha = 0
    
    def __init__(self, ip):
        # gpib address 28 is hardcoded for SPI
        resource_name = "TCPIP0::%s::inst28::INSTR" % ip
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource_name)
        self.instr.timeout = 10000

    def close(self):
        self.instr.close()

            
    def writeBytes(self, be_hexstring):
        '''
        write big endian hex string to spi device
        :param be_hexstring: (string) hex encoded, ex: '3ffff0'
        :param dataWordSize, word len of the be_hexstring, not len(be_hexstring) as
        individual word can be represented by 2 to 8 hexadecimal digits
        :return: None
        '''
        # byte[0]: 0x01 for write ops
        # byte[1:2]: length of write data
        # byte[3:]: bytes of command string

        cmd = bytes.fromhex(be_hexstring)
        len_cmd = len(cmd) 
        data_bytes = cmd    
        bytes_to_write = bytes([0x01]) + len_cmd.to_bytes(2, 'little') + data_bytes    
        
        try:
            self.instr.write_raw(bytes_to_write)
        except ValueError:
            print("spi failed writeBytes")
            
    def writeCS(self,val=0-1):
        ''' 
        write chip select GPIO value when csMode of SPI device is None (or zero)
        :param val is the value of GPIO, can be either 0 or 1
        '''
        # byte[0]: 0x05 for writecs ops
        # byte[1:2]: length of write data
        # byte[3:]: bytes of command string
        
        len_cmd = 1
        hex_string = '{0:02x}'.format(val)
        #print('hexstring is %s'%hex_string)
        bytes_to_write = bytes([0x05]) + len_cmd.to_bytes(2, 'little') + bytes.fromhex(hex_string)
        try:
            self.instr.write_raw(bytes_to_write)
        except ValueError:
            print('spi fail write cs')
            
    def readCS(self):
        ''' 
        read chip select GPIO value when csMode of SPI is None (or zero)
        '''
        # byte[0]: 0x06 for writecs ops
        # byte[1:2]: length of write data
        # byte[3:]: bytes of command string
        
        len_cmd = 0
        bytes_to_write = bytes([0x06]) + len_cmd.to_bytes(2, 'little')
        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw()
            #le_hexstring = (''.join(format(x,'02x') for x in data))
        except ValueError:
            print('spi fail write cs')
        return data[0]

    def queryBytes(self, be_hexstring):
        '''
        'be_hexsting: big endian hex string, ie '0a0102' where 0a is the MSB
        Note that the be_hexstring contains both the register address and 
        the dummy write data. The dummy write
        data is used to provide SPI clock cycles such that
        the correct number of data bits are read back from the MISO signal. 
        As a result, the actual values of the dummy write data is not important
        but must have the same as the number of bits as the actual data to be
        read back.
        
        It is very important that the user calls set_config() to setup the spi
        interface before calling the this routine since _bits2shift is used.
        
        
        '''
        # byte[0]: 0x02 for query ops
        # byte[1:2]: length of query data
        # byte[3:]: bytes of command string

        cmd = bytes.fromhex(be_hexstring)
        len_cmd = len(cmd)
        data_bytes = cmd    
        bytes_to_write = bytes([0x02]) + len_cmd.to_bytes(2, 'little') + data_bytes
        #print(bytes_to_write, len(bytes_to_write))

        try:
            self.instr.write_raw(bytes_to_write)
            data = self.instr.read_raw()
            #debug only
            #data = data[0:3]
            sz = 8
            if (self._bits2shift == 8):
                sz = 1 
                fmt = '{0:02x}'
            if (self._bits2shift == 16):
                sz = 2
                fmt = '{0:04x}'
            if (self._bits2shift == 24):
                sz = 3
                fmt = '{0:06x}'
            if (self._bits2shift == 32):
                sz = 4
                fmt = '{0:08x}'
            
            
            #print('fmt is %s, sz is %d'%(fmt, sz))
            
            be_hexout = ''
            for i in range(0,len(data),sz):
                be_hexout += fmt.format(int.from_bytes(data[i:i+sz],'little'))
                
            return be_hexout
        
        except ValueError:
            print("spi device failed query bytes")
            
    def get_config(self):
        '''
        read SPI interface configuration
        Please read the set_config() for parameters definitions
        
        It is very important that the user calls set_config() to setup the spi
        interface before calling any methods.
        '''
        cmd_byte = bytes([0x04])
        len_data = 0
        len_data_bytes = len_data.to_bytes(2, 'little')
        bytes_to_write = cmd_byte + len_data_bytes
        try:
            self.instr.write_raw(bytes_to_write)
            config = self.instr.read_raw()
        except ValueError:
            print("spi failed read config")
        # unpack the config
        csMode = int(config[0])
        csVal = int(config[1])
        clkDiv = int.from_bytes(config[2:4],'little') # read back data is little endian
        bits2shift = int(config[4])
        msb_first = int(config[5])
        pol = int(config[6])
        pha = int(config[7])
        # update class val
        
        self._csMode = csMode
        self._csVal = csVal
        self._clkDiv = clkDiv
        self._bit2shift = bits2shift
        self._msb_first = msb_first
        self._pol = pol
        self._pha = pha
        
        config = {
                "csMode": csMode,
                "csVal": csVal,
                "clkDiv": clkDiv,
                "bits2shift": bits2shift,
                "msb_first": msb_first,
                "pol": pol,
                "pha":pha
            }
        #return (csMode, csVal, clkDiv,bits2shift,msb_first,pol, pha)
        return config
            
    def set_config(self, csMode, csVal, clkDiv, bits2shift=24, msb_first=1, pol=0, pha=0):
        '''
        set SPI configuration
        
        byte[0]: 0x03 for config
        byte[1:2]: data length
        byte[3:]: csMode(1 byte)csVal(1 byte), clkDiv(2 bytes), bit2shift(1 byte)
        msb_first(1 byte), pol(1 byte), pha(1 byte)
        
        csMode: manual -> 0 , active_low -> 1, active_high ->2
        csVal: value of chip select
        clkDiv: 0-4096, actual clkspeed = 125.0/(clkDiv  + 1.0) MHz
        bits2shift: number of bits to shift per word. Word length can be 
        8, 16, 24 or 32 bits long
        msb_first: shift out the most significant bit first when equals to 1. 
        This corresponds to the left most hex digit in the 
        be_hexstring argument in queryBytes() and writeBytes() 
        pol: clock polarity
        pha: clock phase polarity
        
        It is very important that the user calls set_config() to setup the spi
        interface before calling any methods.
        
        '''
        cmd_byte = bytes([0x03])
        len_data = 11
        len_data_bytes = len_data.to_bytes(2, 'little')
        
        csMode_byte = csMode.to_bytes(1,'little')
        csVal_byte = csVal.to_bytes(1,'little')
        clkDiv_bytes = clkDiv.to_bytes(2,'little')
        bit2shift_bytes = bits2shift.to_bytes(1,'little')
        msb_first_byte = msb_first.to_bytes(1,'little')
        pol_byte = pol.to_bytes(1,'little')
        pha_byte = pha.to_bytes(1,'little')
        trailing_bytes = bytes([0x00,0x00,0x00])
        
        
        bytes_to_write = cmd_byte + len_data_bytes + csMode_byte  + csVal_byte + \
                         clkDiv_bytes + bit2shift_bytes + msb_first_byte + \
                         pol_byte + pha_byte + trailing_bytes
                         
        #print('bytes_to_write %d'%len(bytes_to_write))

        try:
            #print(list(bytes_to_write))
            self.instr.write_raw(bytes_to_write)
            # update local class properties
            self._csMode = csMode
            self._csVal = csVal
            self._clkDiv = clkDiv
            self._bits2shift = bits2shift
            self._msb_first = msb_first
            self._pol = pol
            self._pha = pha
            
        except ValueError:
            print("spi failed write config")
        #return len(bytes_to_write)
    
    def calc_clkdiv(self, speedHz=35000-125000000):
        '''
        function to calculate clkdiv with a desired speed
        '''
        clkdiv = (125000000/speedHz) -1
        return clkdiv


class MCP3008(SpiInstrument):
    '''
    Microchip MCP3008
    please refer to Figure 6-1
    https://www.mouser.com/datasheet/2/268/21295b-72710.pdf
    '''
    def __init__(self,ip):
        SpiInstrument.__init__(self,ip)
        SpiInstrument.set_config(self,1,0,120,24,1,0,0)
        
    
    def readSingleEndedADC(self,channel=0-7):
        ''' reading channel in single ended 0-7
        '''
        be_hexstring = '01%1x000'%(channel+8) #'01' + hex(channel) + '000'
        #print('be_hexstring %s'%be_hexstring)
        be_outhex = self.queryBytes(be_hexstring)
        return int(be_outhex,16)
    
class MCP4812(SpiInstrument):
    '''
    https://www.mouser.com/datasheet/2/268/20002249B-1149996.pdf
    '''
    def __init__(self,ip):
        SpiInstrument.__init__(self,ip)
        SpiInstrument.set_config(self,1,0,120,16,1,0,0)
        
    def writeDAC(self,channel='A', value=0-1023):
        ''' 10 bits DAC, only 
        '''
        if (channel == 'A'):
            val = value*4 # shifted 2 bits
            val += pow(2,13) + pow(2,12) # bit 13 is 1 and bit 12 is 1 always
            
        if (channel == 'B'):
            val = value*4 # shifted 2 bits
            val += pow(2,15) + pow(2,13) + pow(2,12) # bit 15 is high
        
        #write to the dac
        be_hexstring = '{0:04x}'.format(val)
        #print('be_hexstring is %s'%be_hexstring)
        self.writeBytes(be_hexstring)
        
class AD5683R(SpiInstrument):
    '''
    https://www.mouser.com/datasheet/2/609/AD5683R_5682R_5681R_5683-1501713.pdf
    '''
    def __init__(self,ip):
        SpiInstrument.__init__(self,ip)
        SpiInstrument.set_config(self,1,0,12,24,1,1,0) # col, pha is 1, 0
        
    def writeDAC(self, value=0-65535):
        '''
        16bits
        '''
        be_hexstring = '3%04x0'%value
        #print('hex_string is %s'%be_hexstring)
        k = be_hexstring #self.remap24to32b(be_hexstring)
        try:
            self.writeBytes(k)
        except ValueError:
            print('AD5683R writeDAC fails')
    
    def writeCSAndDAC(self,value=0-65535):
        '''
        use the manual CS to demonstrate
        the use of manual mode
        '''
        #set the config to use the 8 bits transfer and manual mode
        SpiInstrument.set_config(self,0,1,12,8,1,1,0) # col, pha is 1, 0     
        be_hexstring = '3%04x0'%value
        #print(be_hexstring)
        try:
            #self.writeCS(1)
            #time.sleep(0.01)
            self.writeCS(0)
            self.writeBytes(be_hexstring) # write the 3 bytes of data
            self.writeCS(1)
        except ValueError:
            print('AD5683R writeCSAndDAC fails')   
            
            
if __name__ == '__main__':
    print('papaya spi demo')
    papaya_ip = "192.168.2.253"
    ad5683 = AD5683R(papaya_ip)
    ad5683.set_config(1,0,120,24,1,1,0) # this is a must
    #ad5683.writeDAC(65535)
    ad5683.writeCSAndDAC(32768)
    