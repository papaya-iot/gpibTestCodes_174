import requests
import urllib.parse


class UartHttpInstrument:

    def __init__(self, ip):
        # gpib address 29 is hardcoded for UART
        self.url = 'http://' + ip + '/uart/'

    def query(self, command):
        """
        query uart device with command string, adding newline to the end
        :param command: (str)
        :return: response string from device
        """
        try:
            cmd = urllib.parse.quote(command)  # escape special chars
            req_url = self.url + 'query/' + cmd
            resp = requests.get(url=req_url)
            return resp.content.decode('utf-8')
        except ValueError:
            print("uart failed query")

    def write(self, command):
        '''
        write command string to uart instrument
        :param command: (str)
        :return: success
        '''
        try:
            cmd = urllib.parse.quote(command)  # escape special chars
            req_url = self.url + 'write/' + cmd
            requests.get(url=req_url)
        except ValueError:
            print("uart failed write")

    def set_config(self, data_rate, num_bits, parity, stop_bits, msg_timeout, byte_timeout):
        """
        set uart configuration
        :param data_rate: (int) baud rate
        :param num_bits: (int) number of bits in a message (7 or 8)
        :param parity: (int) 0=None, 1=Odd, 2=Even
        :param stop_bits: (int) stopbit value
        :param msg_timeout: (int) message timeout in ms
        :param byte_timeout: (int) byte read timeout in us
        :return:
        """

        params = 'baud=%d&numbits=%d&parity=%d&stopbits=%d&m_timo=%d&b_timo=%d' \
                 % (data_rate, num_bits, parity, stop_bits, msg_timeout, byte_timeout)

        try:
            req_url = self.url + 'config/?' + params
            requests.get(req_url)
        except ValueError:
            print('uart device failed set config')

    def get_config(self):
        try:
            req_url = self.url + 'getconfig/'
            resp = requests.get(req_url).json(strict=False)
            return resp
        except ValueError:
            print('uart device failed get config')


class Agilent_E3631(UartHttpInstrument):
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

