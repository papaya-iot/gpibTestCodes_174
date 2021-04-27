import requests
import urllib.parse
import sys, traceback


class Instrument:
    def __init__(self, ip, address):
        self.url = 'http://' + ip + '/'
        self.adr = address
        self.__outpuOnOff = 0
        self._output = ''

    def _get_status(self):
        try:
            resp = requests.get(url=f'{self.url}status').json()
            return resp

        except ValueError as e:
            print(e)
            # resp = {'error': True, 'data': e}

    def query(self, cmd):
        try:
            cmd = urllib.parse.quote(cmd)  # escape special chars
            # req_url = f'{self.url}query?adr={self.adr}&cmd={cmd}'
            req_url = f'{self.url}query/{self.adr}/{cmd}'
            # resp = requests.get(url=req_url).json()
            resp = requests.get(url=req_url)
            return resp.content.decode('utf-8')
            # return resp.json()['data']

        except ValueError as e:
            print(e)
            # resp = {'error': True, 'data': e}

        # if only_data or resp['error']:
        #     # return string output
        #     return resp['data']
        # else:  # return json obj with ibsta, iberr, ibcntl
        #     return resp

    def write(self, cmd):
        try:
            cmd = urllib.parse.quote(cmd)  # escape special chars
            # req_url = f'{self.url}write?adr={self.adr}&cmd={cmd}'  # falcon
            req_url = f'{self.url}write/{self.adr}/{cmd}'   # flask
            requests.get(url=req_url)

        except Exception as e:
            print(e)

    def read(self, only_data=True):
        try:
            # req_url = f'{self.url}read?adr={self.adr}'    # falcon
            # resp = requests.get(url=req_url).json(strict=False)     # use strict=false to allow \n
            # return resp['data']
            req_url = f'{self.url}read/{self.adr}'    # flask
            resp = requests.get(url=req_url)
            return resp.content.decode('utf-8')
            # return resp.json()['data']

        except ValueError as e:
            print(e)
            # resp = {'error': True, 'data': e}

        # if only_data or resp['error']:
        #     # return string output
        #     return resp['data']
        # else:  # return json obj with ibsta, iberr, ibcntl
        #     return resp

    def queryIDN(self):
        try:
            data = self.query("*IDN?")
            return data
        except Exception as e:
            print('*IDN query fails')
            return e

    def queryESR(self):
        try:
            resp = self.query('*ESR?')
            self._output = float(resp)
        except ValueError:
            print('*ESR query fails')
        return self._output

    def querySTB(self):
        try:
            resp = self.query('*STB?')
            self._output = float(resp)
        except ValueError:
            print('*STB query fails')
        return self._output

    def query_err(self):
        try:
            resp = self.query('SYST:ERR?')
            self._output = resp
        except ValueError:
            print('*STB query fails')
        return self._output

    def cls(self):
        try:
            self.write('*CLS')
        except Exception as e:
            print('fails to clear')
            print(e)

    def _set_ESE(self, x):
        try:
            cmd = '*ESE ' + str(x)
            self.write(cmd)
        # except ValueError:
        except Exception as e:
            print('ESE write fails')
            print(e)

    def _get_ESE(self):
        try:
            resp = self.query('*ESE?')
            self._output = float(resp)
        except ValueError:
            print('*ESE query fails')
        return self._output

    ESE = property(_get_ESE, _set_ESE, "ESE property")

    def _set_OPC(self, x):
        try:
            cmd = '*OPC ' + str(x)
            self.write(cmd)
        except Exception as e:
            print('OPC write fails')
            print(e)

    def _get_OPC(self):
        try:
            resp = self.query('*OPC?')
            self._output = float(resp)
        except ValueError:
            print('*OPC query fails')
        return self._output

    OPC = property(_get_OPC, _set_OPC, "OPC property")

    def _set_PSC(self, x):
        try:
            cmd = '*PSC ' + str(x)
            self.write(cmd)
        except Exception as e:
            print('PSC write fails')
            print(e)

    def _get_PSC(self):
        try:
            resp = self.query('*PSC?')
            self._output = float(resp)
        except ValueError:
            print('*PSC query fails')
        return self._output

    PSC = property(_get_PSC, _set_PSC, "PSC property")

    def _set_SRE(self, x):
        try:
            cmd = '*SRE ' + str(x)
            self.write(cmd)
        except Exception as e:
            print('SRE write fails')
            print(e)

    def _get_SRE(self):
        try:
            resp = self.query('*SRE?')
            self._output = float(resp)
        except ValueError:
            print('*SRE query fails')
        return self._output

    SRE = property(_get_SRE, _set_SRE, "SRE property")

    def wait(self):
        try:
            self.write('*WAI')
        except ValueError:
            print('*WAI write fails')

class Keithley_2400(Instrument):
    def __init__(self, ip, address=1):
        super().__init__(ip, address)

    def sourcetype(self, type):
        if type == 'voltage':
            super().write(':SOUR:FUNC VOLT')
            super().write(':SENS:FUNC "CURR"')  # Sensing current
        elif type == 'current':
            super().write(':SOUR:FUNC CURR')
            super().write(':SENS:FUNC "VOLT"')  # Sensing current

    def setvoltage(self, vb, curlimit=0.05):
        super().write(':SENS:CURR:PROT %f' % curlimit)  # Set compliance current to 40 mA
        super().write(':SOUR:VOLT:LEV %f' % vb)

    def querycurrent(self):
        try:
            super().write(':FORM:ELEM CURR')
            cur = super().query('READ?')
            c = float(cur)
        except ValueError:
            print('warning: current reading error...')
            print(cur)
            c = -1000
        return float(c)

    def setcurrent(self, cur, vlimit=2):
        super().write(':SENS:VOLT:PROT %f' % vlimit)
        super().write(':SOUR:CURR:LEV %s' % cur)

    def _get_output(self):
        try:
            resp = super().query(':OUTPUT?')
            self._output = float(resp)
        except ValueError:
            print('Keithley 2400 query fails')
        return self._output

    def _set_output(self, x):
        try:
            cmd = ':OUTPUT  ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Keithley 2400 write fails')
        self._output = x

    output = property(_get_output, _set_output, "output property")


class Agilent_E3631(Instrument):
    def __init__(self, ip, address=1):
        super().__init__(ip, address)

    def _get_outputOnOff(self):
        try:
            # req_adr = self.url + 'query/{}/:outp%3f'.format(self.adr)
            resp = super().query(':outp?')
            self.__outpuOnOff = int(resp)  # update outpuOnOff var
        except Exception as e:
            resp = {'error': True, 'data': e}
        return self.__outpuOnOff

    def _set_outputOnOff(self, x):
        try:
            # cmd = urllib.parse.quote('outp ' + str(x))
            # req_adr = '{}write/{}/{}'.format(self.url, self.adr, cmd)
            super().write('outp {}'.format(x))
            self.__outpuOnOff = x
        except Exception as e:
            print(e)

    outputOnOff = property(_get_outputOnOff, _set_outputOnOff, "outputOnOff property")

    def queryCurrent(self):
        try:
            resp = float(super().query(':meas:curr:dc?'))
        except ValueError:
            print('Agilent E3631 query failure')
        return resp

    def queryVoltage(self):
        try:
            resp = float(super().query(':meas:volt:dc?'))
        except ValueError:
            print('Agilent E3631 query failure')
        return resp


class Agilent_33401(Instrument):
    def __init__(self, ip, address=1):
        super().__init__(ip, address)

    def queryIDN(self):
        try:
            resp = super().query('*IDN?')
        except ValueError:
            print('Agilent 33401 fails query')
        return resp

    def cls(self):
        try:
            super().write('*CLS')
        except ValueError:
            print('Agilent 33401 fails to clear')

    def _set_ESE(self, x):
        try:
            cmd = '*ESE ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Agilent 33401 ESE write fails')

    def _get_ESE(self):
        try:
            resp = super().query('*ESE?')
            self._output = float(resp)
        except ValueError:
            print('Agilent 33401 *ESE query fails')
        return self._output

    ESE = property(_get_ESE, _set_ESE, "ESE property")

    def _set_SRE(self, x):
        try:
            cmd = '*SRE ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Agilent 33401 SRE write fails')

    def _get_SRE(self):
        try:
            resp = super().query('*SRE?')
            self._output = float(resp)
        except ValueError:
            print('Agilent 33401 *SRE query fails')
        return self._output

    SRE = property(_get_SRE, _set_SRE, "SRE property")

    def acVoltage(self):
        try:
            super().write(':meas:volt:ac?')
            resp = float(super().read())
        except ValueError:
            print('Agilent 33401 fails query')
        return resp

    def acCurrent(self):
        try:
            super().write(':meas:curr:ac?')
            resp = float(super().read())
        except ValueError:
            print('Agilent 33401 fails query')
        return resp

    def dcVoltage(self):
        try:
            super().write(':meas:volt:dc?')
            resp = float(super().read())
        except ValueError:
            print('Agilent 33401 fails query')
        return resp

    def dcCurrent(self):
        try:
            super().write(':meas:curr:dc?')
            resp = float(super().read())
        except ValueError:
            print('Agilent 33401 fails query')
        return resp


class Keithley_2510(Instrument):
    # Keithley 2510
    # def __init__(self, resourceName='GPIB0::15::INSTR', defaultmode='temp'):
    def __init__(self, ip, adr=1):
        super().__init__(ip, adr)
        super().write(':SOUR:FUNC TEMP')

    def querytemp(self):
        try:
            # super().write(':MEAS:TEMP?')
            # temp = super().read()
            temp = super().query(':MEAS:TEMP?')
            t = float(temp)
        except ValueError:
            print('warning: temp read error...')
            print(temp)
            t = -1000
        return float(t)

    def settemp(self, setT='25'):
        super().write(':SOUR:TEMP %f' % setT)

    def _get_output(self):
        try:
            resp = super().query(':OUTPUT?')
            self._output = float(resp)
        except ValueError:
            print('Keithley 2510 query fails')
        return self._output

    def _set_output(self, x):
        try:
            cmd = ':OUTPUT  ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Keithley 2510 write fails')
        self._output = x

    output = property(_get_output, _set_output, "output property")


class Newport_3150(Instrument):
    # this is Newport
    # def __init__(self, resourceName='GPIB0::15::INSTR', defaultmode='temp'):
    def __init__(self, ip, adr=1):
        super().__init__(ip, adr)
        super().write(':SOUR:FUNC TEMP"')

    def queryIDN(self):
        try:
            resp = super().query('*IDN?')
        except ValueError:
            print('Newport 3150 fails query')
        return resp

    def querytemp(self):
        temp = super().query(':TEC:T?')
        try:
            t = float(temp['data'])
        except ValueError:
            print('warning: temp read error...')
            print(temp)
            t = -1000
        return float(t)

    def settemp(self, setT='25'):
        super().write(':TEC:T %f' % setT)


class powermeter(Instrument):

    # def __init__(self, resourceName='GPIB0::4::INSTR'):
    def __init__(self, ip, adr=1):
        super().__init__(ip, adr)

    def queryIDN(self):
        try:
            resp = super().query('*IDN?')
        except ValueError:
            print('Agilent 86163 fails query')
        return resp

    def querypower(self):
        opt = super().query('READ:POW?')
        return float(opt)


class dca(Instrument):

    # def __init__(self, resourceName='GPIB0::7::INSTR'):
    def __init__(self, ip, adr=1):
        super().__init__(ip, adr)

    def initialize(self):  # initiallize for PAM4 measurement
        pass

    def getER(self, source='1', ch='2A'):
        cmd = ':MEASure:EYE:OER:SOURce' + source + ' CHAN' + ch
        super().write(cmd)
        er = super().query(':MEASure:EYE:OER?')
        return float(er)

    def getOMA(self, source='1', ch='2A'):
        cmd = ':MEASure:EYE:OOMA:SOURce' + source + ' CHAN' + ch
        super().write(cmd)
        oma = super().query(':MEASure:EYE:OOMA?')
        return float(oma)

    def getRLM(self, source='1', ch='2A'):
        cmd = ':MEASure:EYE:PAM:LINearity:SOURce' + source + ' CHAN' + ch
        super().write(cmd)
        RLM = super().query(':MEASure:EYE:PAM:LINearity?')
        return float(RLM)

    #    def getTDEDQ(self):
    #        return super().query()

    def autoscale(self):
        super().write(':SYSTem:AUToscale')
        super().ask('*OPC?')

    def clear(self):
        super().write(':ACQuire:CDISplay')
        super().ask('*OPC?')

    def run(self):
        super().write(':ACQuire:RUN')
    #    def savejpg(self,ch='2A',fname='',path='')


#        cmd = ':DISPlay:WINDow:TIME1:ZSIGnal CHAN'+ch
#        super().write(cmd)
#        self.

class Agilent_86142(Instrument):
    def __init__(self, ip, adr=1):
        super().__init__(ip, adr)
        self._startWavelength = 1529e-9
        self._stopWavelength = 1560e-9
        self._traceLength = 0

    def queryIDN(self):
        try:
            resp = super().query('*IDN?')
        except ValueError:
            print('Agilent 86142 fails query')
        return resp

    def cls(self):
        try:
            super().write('*CLS')
        except ValueError:
            print('Keithley 86142 fails to clear')

    def _set_ESE(self, x):
        try:
            cmd = '*ESE ' + str(x)
            super().write(cmd)
        except ValueError:
            print('86142 ESE write fails')

    def _get_ESE(self):
        try:
            resp = super().query('*ESE?')
            self._output = float(resp)
        except ValueError:
            print('86142 *ESE query fails')
        return self._output

    ESE = property(_get_ESE, _set_ESE, "ESE property")

    def _set_SRE(self, x):
        try:
            cmd = '*SRE ' + str(x)
            super().write(cmd)
        except ValueError:
            print('86142 SRE write fails')

    def _get_SRE(self):
        try:
            resp = super().query('*SRE?')
            self._output = float(resp)
        except ValueError:
            print('86142 *SRE query fails')
        return self._output

    SRE = property(_get_SRE, _set_SRE, "SRE property")

    def _get_startWavelength(self):
        try:
            resp = super().query(':sens:wav:star?')
            self._startWavelength = float(resp)
        except ValueError:
            print('Agilent 86142 query get startwav fails')
        return self._startWavelength

    def _set_startWavelength(self, x):
        try:
            cmd = ':sens:wav:star ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Agilent 86142 write fails')
        self._startWavelength = x

    startWavelength = property(_get_startWavelength, _set_startWavelength, "startWavelength property")

    def _get_stopWavelength(self):
        try:
            resp = super().query(':sens:wav:stop?')
            self._stopWavelength = float(resp)
        except ValueError:
            print('Agilent 86142 query get stopwav fails')
        return self._stopWavelength

    def _set_stopWavelength(self, x):
        try:
            cmd = ':sens:wav:stop ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Agilent 86142 write fails')
        self._stopWavelength = x

    stopWavelength = property(_get_stopWavelength, _set_stopWavelength, "stopWavelength property")

    def _get_traceLength(self):
        try:
            resp = super().query(':SENS:SWE:POIN?')
            self._traceLength = float(resp)
        except ValueError:
            print('Agilent 86142 query get traclen fails')
        return self._traceLength

    def _set_traceLength(self, x):
        try:
            cmd = ':SENS:SWE:POIN ' + str(x)
            super().write(cmd)
        except ValueError:
            print('Agilent 86142 write fails')
        self._traceLength = x

    traceLength = property(_get_traceLength, _set_traceLength, "traceLength property")

    def getTrace(self):
        tmp = ''
        elmcount = []
        try:
            super().write('form ascii')
            super().write('trac? tra')
            resp = super().read()
            flag = '\n' in resp
            count = 0
            while (not (flag)):
                # time.sleep(0.1)
                tmp = super().read()
                #elmcount.append(len(tmp.split(',')))
                # print('length %i and count %i'% (len(tmp),count))
                resp += (tmp)
                flag = '\n' in tmp
                count += 1
                #print(elmcount)
            # print (count)
        except Exception:
            print('error')
            print(tmp)
            resp = tmp
            traceback.print_exc()
        ###COMMENTED OUT BC ERRORS
        # except visa.VisaIOError:
        #     print('error')
        #     print(tmp)
        #     resp = tmp
        #     traceback.print_exc()
        #     sys.exit(3)
        return resp

    def getTrace1(self, pts):
        tmp = ''
        elmcount = []
        count = 0
        itr = 0
        try:
            super().write('form ascii')
            super().write('trac? tra')
            resp = super().read()
            # print('resp', len(resp), resp)
            flag = '\n' in resp
            print (flag)
            count += len(resp.split(','))
            while count < pts:  # (not(flag)):
                # time.sleep(0.1)
                tmp = super().read()
                count += len(tmp.split(','))
                elmcount.append(count)
                # print('length %i and count %i'% (len(tmp),count))
                resp += (tmp)
                flag = '\n' in tmp
                print(flag)
                # if itr < 2:
                # print (' ' + str(count))
                # print('tmp', len(tmp))
                # print(str(itr), tmp)
                # else:
                # print(str(itr), tmp)
                itr += 1
            #print (itr)
        except Exception:
            print('error')
            print(tmp)
            resp = tmp
            traceback.print_exc()
            sys.exit(3)
        return resp

    def getTraceBin(self):
        try:
            super().write('form real32')
            super().write('trac? tra')
            resp = super().read()
        except ValueError:
            print('Agilent 86142 write fails')
        return resp


class JDSU_HA9(Instrument):
    # def __init__(self, resourceName):
    #     rm = visa.ResourceManager()
    #     super() = rm.open_resource(resourceName)
    #     super().timeout = 10000
    def __init__(self, ip, adr=1):
        super().__init__(ip, adr)
        self._attenuation = 0
        self._beamIsBlocked = 0

    def _get_attenuation(self):
        try:
            resp = super().query('att?')
            self._attenuation = float(resp)
        except ValueError:
            print('JDSU HA9 query fails')
        return self._attenuation

    def _set_attenuation(self, x):
        try:
            cmd = 'att ' + str(x)
            super().write(cmd)
        except ValueError:
            print('JDSU HA9 write fails')
        self._attenuation = x

    attenuation = property(_get_attenuation, _set_attenuation, "attenuation property")

    def _get_beamIsBlocked(self):
        try:
            resp = super().query('D?')
            self._beamIsBlocked = int(resp)
        except ValueError:
            print('JDSU HA9 query fails')
        return self._beamIsBlocked

    def _set_beamIsBlocked(self, x):
        try:
            cmd = 'D ' + str(int(x))
            super().write(cmd)
        except ValueError:
            print('JDSU HA9 write fails')
        self._beamIsBlocked = int(x)

    beamIsBlocked = property(_get_beamIsBlocked, _set_beamIsBlocked, "beamIsBlock property")


class thermoStreamTP04100(Instrument):
    _flowOnOff = 0

    def __init__(self, ip, address=1):
        super().__init__(ip, address)

    def _set_SRE(self, x):
        try:
            cmd = '*SRE ' + str(x)
            super().write(cmd)
        except ValueError:
            print('thermoStreamTP04100 SRE write fails')

    def _get_SRE(self):
        try:
            resp = super().query('*SRE?')
            self._output = float(resp['data'])
        except ValueError:
            print('thermoStreamTP04100 *SRE query fails')
        return self._output

    SRE = property(_get_SRE, _set_SRE, "SRE property")

    def _set_flow(self, x):
        try:
            cmd = 'FLOW ' + str(x)
            super().write(cmd)
        except ValueError:
            print('thermoStreamTP04100 FLOW write fails')

    def _get_flow(self):
        return self._flowOnOff

    flow = property(_get_flow, _set_flow, "Flow property")

    def _set_tempSetPoint(self, x):
        try:
            cmd = 'SETP ' + str(x)
            super().write(cmd)
        except ValueError:
            print('thermoStreamTP04100 SETP write fails')

    def _get_tempSetPoint(self):
        try:
            resp = super().query('SETP?')
            self._output = float(resp['data'])
        except ValueError:
            print('thermoStreamTP04100 SETP query fails')
        return self._output

    setpoint = property(_get_tempSetPoint, _set_tempSetPoint, "setpoint property")

    def readDutTemp(self):
        try:
            resp = super().query('TMPD?')
            self._output = float(resp['data'])
        except ValueError:
            print('thermoStreamTP04100 read dut temperature fails')
        return self._output

    def readAirTemp(self):
        try:
            resp = super().query('TMPA?')
            self._output = float(resp['data'])
        except ValueError:
            print('thermoStreamTP04100 read air temperature fails')
        return self._output

# without
# class tekDSA8300(Instrument):
#     def __init__(self, ip, address=1):
#         super().__init__(ip, address)
#
# class ANR_MP1800A(Instrument):
#     def __init__(self, ip, address=1):
#         super().__init__(ip, address)
#
# class Keysight86100D(Instrument):
#     def __init__(self, ip, address=1):
#         super().__init__(ip, address)
#
# class GP_MPC101(Instrument):
#     def __init__(self, ip, address=1):
#         super().__init__(ip, address)

# a = Agilent_86142('192.168.2.209:8080', '11')
# print(a.queryIDN()['data'])
# print(a._get_status())
# print(a._get_outputOnOff())
# a._set_outputOnOff(1)
# print(a._get_status())
# print(a._get_outputOnOff())
# print(a.queryCurrent())
# print(a.queryVoltage())

# k = Keithley_2400('192.168.2.209:8080', '15')
# print(k.query('*IDN?'))
# k.cls()

# att = JDSU_HA9('192.168.209', 21)
# print('att is %f' % att.attenuation)

#
# tec = Keithley_2510('192.168.2.209:8080', 5)
# tec.cls
# ## setting up for error trigger
# tec.ESE = 36
# tec.SRE = 32
# tec.settemp(25.00)
# tec.querytemp()
