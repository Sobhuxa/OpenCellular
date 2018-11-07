#!/usr/bin/env python
"""Enhanced Serial Port class
part of pyserial (http://pyserial.sf.net)  (C)2002 cliechti@gmx.net

another implementation of the readline and readlines method.
this one should be more efficient because a bunch of characters are read
on each access, but the drawback is that a timeout must be specified to
make it work (enforced by the class __init__).

this class could be enhanced with a read_until() method and more
like found in the telnetlib.
"""

from serial import Serial
from time import sleep

class EnhancedSerial(Serial):
    def __init__(self, *args, **kwargs):
        #ensure that a reasonable timeout is set
        timeout = kwargs.get('timeout',0.01)
        if timeout < 0.01: timeout = 0.01
        kwargs['timeout'] = timeout
        Serial.__init__(self, *args, **kwargs)
        self.buf = ''
        self.last = ''
        
    def read(self, *args, **kwargs):
        ret = Serial.read(self, *args, **kwargs)
        #TODO: only store when there's someone called wait_until?
        self.last += ret
        return ret

    def wait_until(self, *args, **kwargs):
        timeout = kwargs.get('timeout',10)
        tries=0
        while 1:
            if (timeout > 0) and (tries*self.timeout > timeout):
                return -1
            i = 0
            for s in args:
                if isinstance(s, str):
                    pos = self.last.find(s)
                    if pos >= 0:
                        self.last = self.last[pos+1:]
                        #print("matched"+ str(len(self.last)))
                        return i
                else: break
                i+=1
            #if pattern not found, remove the found part in lines
            pos = self.last.rfind('\n')
            if pos >= 0 :
                self.last = self.last[pos+1:]
            sleep(self.timeout)
            tries += 1



    def readline(self, maxsize=None, timeout=1):
        """maxsize is ignored, timeout in seconds is the max time that is way for a complete line"""
        tries = 0
        while 1:
            self.buf += self.read(512)
            pos = self.buf.find('\n')
            if pos >= 0:
                line, self.buf = self.buf[:pos+1], self.buf[pos+1:]
                return line
            tries += 1
            if tries * self.timeout > timeout:
                break
        line, self.buf = self.buf, ''
        return line

    def readlines(self, sizehint=None, timeout=1):
        """read all lines that are available. abort after timout when no more data arrives."""
        lines = []
        while 1:
            line = self.readline(timeout=timeout)
            if line:
                lines.append(line)
            if not line or line[-1:] != '\n':
                break
        return lines

if __name__=='__main__':
    #do some simple tests with a Loopback HW (see test.py for details)
    
    PORT = 0
    #test, only with Loopback HW (shortcut RX/TX pins (3+4 on DSUB 9 and 25) )
    s = EnhancedSerial(PORT)
    #write out some test data lines
    s.write('\n'.join("hello how are you".split()))
    #and read them back
    print s.readlines()
    #this one should print an empty list
    print s.readlines(timeout=0.4)
