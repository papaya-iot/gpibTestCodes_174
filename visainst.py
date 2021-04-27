# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 14:56:08 2017

@author: lab6750
"""


import pyvisa as visa
import time
import sys,traceback
import re as regex
import numpy as np


class VisaInstrument():

    def __init__(self, ip, gpib_address):      
        resource_name = "TCPIP0::%s::inst%s::INSTR" % (ip, gpib_address)
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(resource_name)
        self.instr.timeout = 10000
			
    def close(self):
        self.instr.close()

    def cls(self):
        try:
            self.instr.write('*CLS')
        except ValueError:
            print('*CLS fails to clear')
            
    def _set_ESE(self, x):
        try:
            cmd = '*ESE ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print ('*ESE write fails')
            
    def _get_ESE(self,x):
        try:
            resp = self.instr.query('*ESE?')
            self._output = float(resp)
        except ValueError:
            print('*ESE query fails')
        return self._output
            
    ESE = property(_get_ESE, _set_ESE, "ESE property")
    
    def _set_SRE(self, x):
        try:
            cmd = '*SRE ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print ('*SRE write fails')
            
    def _get_SRE(self,x):
        try:
            resp = self.instr.query('*SRE?')
            self._output = float(resp)
        except ValueError:
            print('*SRE query fails')
        return self._output
            
    SRE = property(_get_SRE, _set_SRE, "SRE property")
    
    def queryIDN(self):
        try:
            data = self.instr.query('*IDN?')
            return data
        except ValueError:
            print('*IDN query fails')
             
class Keysight_N9030B(VisaInstrument): 
        
    def getTrace(self,tra='TRACE1'):
        flag = False
        count = 0
        try:
            self.instr.write('trac:data? %s' %tra)
            resp = self.instr.read()
            flag = '\n' in resp
            while (not(flag)):
                tmp = self.instr.read()
                #print('length %i and count %i'% (len(tmp),count))
                resp += (tmp)
                flag = '\n' in tmp                
                count += 1
        except visa.VisaIOError:
            print('error')
            print(tmp)
            resp = tmp
            traceback.print_exc()
            sys.exit(3)
            
        ary = resp.split(',')
        dd =np.array([float(c) for c in ary])
        return dd   

class Anritsu_M4647A(VisaInstrument): 
        
    def sweepOnce(self):
        self.instr.write('TRS;WFS;HLD')
        time.sleep(11)
    
    def readSXX(self,fmt='OS11C'):
        #fmt: OS11C, OS11R,OS12C, OS12R, OS21C, OS21R, OS22C, OS22R
        
        #self.instr.write(':calc1:form:s1p:port port1')
        #set to real imag
        #self.instr.write(':calc1:form %s'%fmt)
        #self.instr.write('OFD')
        #:sens1:freq:data?
        try:
            self.instr.write(fmt) # C here refers to calibrated
            resp = self.instr.read()
            s = regex.findall(r'^#\d+',resp)[0] # get the first elment in string instead of list
            pos = int(s[1]) + 3
            _num =int(s[2:len(s)])  # total number of bytes to read
            resp = resp[pos:len(resp)] # remove the header
            cnt = len(resp)
            while (cnt < _num):
                tmp = self.instr.read()
                cnt += len(tmp)
                resp += tmp
                #print (cnt)
        except visa.VisaIOError:
            traceback.print_exc()
            sys.exit(3)
            
        # make them into real numbers
        y = resp.split('\n')
        y = y[0:len(y)-1] # last element is \n
        real =np.zeros(len(y),dtype=float)
        imag = np.zeros(len(y),dtype=float)
        for i_ in range(0,len(y)):
            valstr = y[i_].split(',') # split into real and imag
            real[i_] = float(valstr[0])
            imag[i_] = float(valstr[1])
            
        c = real + 1.j*imag
        
        return c
    
    def freq(self):
        try:
            self.instr.write(':sens1:freq:data?')
            resp = self.instr.read()
            s = regex.findall(r'^#\d+',resp)[0] # get the first elment in string instead of list
            pos = int(s[1]) + 3
            _num =int(s[2:len(s)])  # total number of bytes to read
            resp = resp[pos:len(resp)] # remove the header
            cnt = len(resp)
            while (cnt < _num):
                tmp = self.instr.read()
                cnt += len(tmp)
                resp += tmp
        except visa.VisaIOError:
            traceback.print_exc()
            sys.exit(3)
            
        y = resp.split('\n')
        y = y[0:len(y)-1] # last element is \n
        val = np.array([float(c) for c in y])
        return val
        
class Keithley_2400(VisaInstrument):
           
    def sourcetype(self,type):
        if type == 'voltage':            
            self.instr.write(':SOUR:FUNC VOLT')
            self.instr.write(':SENS:FUNC "CURR"') # Sensing current
        elif type == 'current':
            self.instr.write(':SOUR:FUNC CURR')
            self.instr.write(':SENS:FUNC "VOLT"') # Sensing current                 
        
    def setvoltage(self,vb,curlimit=0.05):
        self.instr.write(':SENS:CURR:PROT %f'%curlimit) # Set compliance current to 40 mA
        self.instr.write(':SOUR:VOLT:LEV %f'%vb)        
    
    def querycurrent(self):
        try:
            self.instr.write(':FORM:ELEM CURR')
            cur = self.instr.query('READ?')
            c = float(cur)
        except ValueError:
            print('warning: current reading error...')
            print(cur)
            c = -1000        
        return float(c)
    
    def setcurrent(self,cur,vlimit=2):
        self.instr.write(':SENS:VOLT:PROT %f'%vlimit)
        self.instr.write(':SOUR:CURR:LEV %s'%cur)
        
    def _get_output(self):
        try:
            resp = self.instr.query(':OUTPUT?')
            self._output = float(resp)
        except ValueError:
            print('Keithley 2400 query fails')
        return self._output
        
    def _set_output(self, x):
        try:
            cmd = ':OUTPUT  ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('Keithley 2400 write fails')
        self._output = x
        
    output = property(_get_output, _set_output, "output property")
        
class Agilent_E3631(VisaInstrument):
   
    def _get_outPutOnOff(self):
        try:
            resp = self.instr.query(':outp?')
            self._startWavelength = int(resp)
        except ValueError:
            print('Agilent E3631 query fails')
        return self._outpuOnOff
  
    def _set_outPutOnOff(self, x):
        try:
            cmd = 'outp ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('Agilent E3631 write fails')
        self._outpuOnOff = x
      
    outputOnOff = property(_get_outPutOnOff, _set_outPutOnOff, "outputOnOff property")
        
    def queryCurrent(self):
        try:
            resp=self.instr.query(':meas:curr:dc?')
        except ValueError:
            print('Agilent E3631 query failure')
        return float(resp)
    
    def queryVoltage(self):
        try:
            resp=self.instr.query(':meas:volt:dc?')
        except ValueError:
            print('Agilent E3631 query failure')
        return float(resp)


class Agilent_33401(VisaInstrument):

    def acVoltage(self):
        try:
            self.instr.write(':meas:volt:ac?')
            resp = self.instr.read()
        except ValueError:
            print('Agilent 33401 fails query')
        return float(resp)   
    
    def acCurrent(self):
        try:
            self.instr.write(':meas:curr:ac?')
            resp = self.instr.read()
        except ValueError:
            print('Agilent 33401 fails query')
        return float(resp)
    
    def dcVoltage(self):
        try:
            self.instr.write(':meas:volt:dc?')
            resp = self.instr.read()
        except ValueError:
            print('Agilent 33401 fails query')
        return float(resp)   
    
    def dcCurrent(self):
        try:
            self.instr.write(':meas:curr:dc?')
            resp = self.instr.read()
        except ValueError:
            print('Agilent 33401 fails query')
        return float(resp)
    
    
class Keithley_2510(VisaInstrument):

    def querytemp(self):
        try:
            self.instr.write(':MEAS:TEMP?')
            temp = self.instr.read()
            t = float(temp)
        except ValueError:
            print('warning: temp read error...')
            print(temp)
            t = -1000
        return float(t)    
    
    def settemp(self,setT='25'):
        self.instr.write(':SOUR:TEMP %f'%setT)
        
    def _get_output(self):
        try:
            
            resp = self.instr.query(':OUTPUT?')
            self._output = float(resp)
        except ValueError:
            print('Keithley 2510 query fails')
        return self._output
        
    def _set_output(self, x):
        try:
            cmd = ':OUTPUT  ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('Keithley 2510 write fails')
        self._output = x
        
    output = property(_get_output, _set_output, "output property")
    

class Newport_3150(VisaInstrument):
        
    def querytemp(self):
        temp = self.instr.query(':TEC:T?')
        try:
            t = float(temp)
        except ValueError:
            print('warning: temp read error...')
            print(temp)
            t = -1000
        return float(t)    
    
    def settemp(self,setT='25'):
        self.instr.write(':TEC:T %f'%setT)
    

class powermeter(VisaInstrument):
    
    def queryIDN(self):
        try:
            resp = self.instr.query('*IDN?')
        except ValueError:
            print('Agilent 86163 fails query')
        return resp
    
    def querypower(self):
        opt = self.instr.query('READ:POW?')        
        return float(opt)
    
class dca(VisaInstrument):

    def initialize(self): # initiallize for PAM4 measurement
        pass
    
    def getER(self,source='1',ch='2A'):
        cmd = ':MEASure:EYE:OER:SOURce'+source+' CHAN'+ch
        self.instr.write(cmd)
        er = self.instr.query(':MEASure:EYE:OER?')
        return float(er)
    
    def getOMA(self,source='1',ch='2A'):
        cmd = ':MEASure:EYE:OOMA:SOURce'+source+' CHAN'+ch
        self.instr.write(cmd)
        oma = self.instr.query(':MEASure:EYE:OOMA?')
        return float(oma)
    
    def getRLM(self,source='1',ch='2A'):
        cmd = ':MEASure:EYE:PAM:LINearity:SOURce'+source+' CHAN'+ch
        self.instr.write(cmd)
        RLM = self.instr.query(':MEASure:EYE:PAM:LINearity?')
        return float(RLM)
    
#    def getTDEDQ(self):
#        return self.instr.query()
    
    def autoscale(self):
        self.instr.write(':SYSTem:AUToscale')
        self.instr.ask('*OPC?')
    
    def clear(self):
        self.instr.write(':ACQuire:CDISplay')
        self.instr.ask('*OPC?')
    
    def run(self):
        self.instr.write(':ACQuire:RUN')    
#    def savejpg(self,ch='2A',fname='',path='')
#        cmd = ':DISPlay:WINDow:TIME1:ZSIGnal CHAN'+ch
#        self.instr.write(cmd)
#        self.

class Agilent_86142(VisaInstrument):

    def _get_startWavelength(self):
        try:
            resp = self.instr.query(':sens:wav:star?')
            self._startWavelength = float(resp)
        except ValueError:
            print('Agilent 86142 query fails')
        return self._startWavelength
  
    def _set_startWavelength(self, x):
        try:
            cmd = ':sens:wav:star ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('Agilent 86142 write fails')
        self._startWavelength = x
      
    startWavelength = property(_get_startWavelength, _set_startWavelength, "startWavelength property")
    
    def _get_stopWavelength(self):
        try:
            resp = self.instr.query(':sens:wav:stop?')
            self._startWavelength = float(resp)
        except ValueError:
            print('Agilent 86142 query fails')
        return self._startWavelength
  
    def _set_stopWavelength(self, x):
        try:
            cmd = ':sens:wav:stop ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('Agilent 86142 write fails')
        self._stopWavelength = x
      
    stopWavelength = property(_get_stopWavelength, _set_stopWavelength, "stopWavelength property")
  
    def _get_traceLength(self):
        try:
            resp = self.instr.query(':SENS:SWE:POIN?')
            self._traceLength = float(resp)
        except ValueError:
            print('Agilent 86142 query fails')
        return self._traceLength
  
    def _set_traceLength(self, x):
        try:
            cmd = ':SENS:SWE:POIN  ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('Agilent 86142 write fails')
        self._traceLength = x
      
    traceLength = property(_get_traceLength, _set_traceLength, "traceLength property")
    
 
    def getTrace(self):
        tmp = ''
        elmcount = []
        try:
            self.instr.write('form ascii')
            self.instr.write('trac? tra')
            resp = self.instr.read()
            flag = '\n' in resp
            count = 0
            while (not(flag)):
                #time.sleep(0.1)
                tmp = self.instr.read()
                #elmcount.append(len(tmp.split(',')))
                #print('length %i and count %i'% (len(tmp),count))
                resp += (tmp)
                flag = '\n' in tmp
                count += 1
                #print (elmcount)
            #print (count)
        except visa.VisaIOError:
            print('error')
            print(tmp)
            resp = tmp
            traceback.print_exc()
            sys.exit(3)
        return resp
    
    def getTrace1(self,pts):
        tmp = ''
        elmcount = []
        count = 0
        itr=0
        try:
            self.instr.write('form ascii')
            self.instr.write('trac? tra')
            resp = self.instr.read()
            #print('resp', len(resp), resp)
            flag = '\n' in resp
            count += len(resp.split(','))
            while (count < pts): #(not(flag)):
                #time.sleep(0.1)
                tmp = self.instr.read()
                count += len(tmp.split(','))
                elmcount.append(count)
                #print('length %i and count %i'% (len(tmp),count))
                resp += (tmp)
                flag = '\n' in tmp
                print(flag)
                itr +=1
            #print (count)
        except visa.VisaIOError:
            print('error')
            print(tmp)
            resp = tmp
            traceback.print_exc()
            sys.exit(3)
        return resp
    
    def getTraceBin(self):
        try:
            self.instr.write('form real32')
            self.instr.write('trac? tra')
            resp = self.instr.read()
        except ValueError:
            print('Agilent 86142 write fails')
        return resp
        
class JDSU_HA9(VisaInstrument):
    _attenuation = 0
    _beamIsBlocked = 0
    
    def _get_attenuation(self):
        try:
            resp = self.instr.query('att?')
            self._attenuation = float(resp)
        except ValueError:
            print('JDSU HA9 query fails')
        return self._attenuation
  
    def _set_attenuation(self, x):
        try:
            cmd = 'att ' + str(x)
            self.instr.write(cmd)
        except ValueError:
            print('JDSU HA9 write fails')
        self._attenuation = x
      
    attenuation = property(_get_attenuation, _set_attenuation, "attenuation property")
    
    def _get_beamIsBlocked(self):
        try:
            resp = self.instr.query('D?')
            self._beamIsBlocked = int(resp)
        except ValueError:
            print('JDSU HA9 query fails')
        return self._beamIsBlocked
  
    def _set_beamIsBlocked(self, x):
        try:
            cmd = 'D ' + str(int(x))
            self.instr.write(cmd)
        except ValueError:
            print('JDSU HA9 write fails')
        self._beamIsBlocked = int(x)
      
    beamIsBlocked = property(_get_beamIsBlocked, _set_beamIsBlocked, "beamIsBlock property")
    