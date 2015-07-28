#!/usr/bin/python

#-----------------------------------------------------------------------
# python mavlink testing
# t3 -- decoding mavlink package
#
#-----------------------------------------------------------------------

import sys
import serial    # https://pypi.python.org/pypi/pyserial
import array
import struct

#PORT='COM10'
PORT='/dev/tty.usbmodem621'

BAUD=57600
BAUD=115200

#=======================================================================
# UTILITY STUFF
#=======================================================================

#-----------------------------------------------------------------------
xdumpf=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def xdump(src, length=16):
    """dump a string in classic hexdump format
       adapted from http://code.activestate.com/recipes/142812-hex-dumper
    """
    N=0;
    while src:
        s,src = src[:length],src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(xdumpf)
        print "%04X   %-*s   %s" % (N, length*3, hexa, s)
        N+=length

#-----------------------------------------------------------------------
MAVLINK_MESSAGE_CRCS=[
  50,124,137,0,237,217,104,119,0,0,0,89,0,0,0,0,0,0,0,0,214,159,220,168,
  24,23,170,144,67,115,39,246,185,104,237,244,222,212,9,254,230,28,28,
  132,221,232,11,153,41,39,214,223,141,33,15,3,100,24,239,238,30,240,183,
  130,130,0,148,21,0,243,124,0,0,0,20,0,152,143,0,0,127,106,0,0,0,0,0,0,
  0,231,183,63,54,0,0,0,0,0,0,0,175,102,158,208,56,93,0,0,0,0,235,93,124,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,42,
  241,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,204,49,
  170,44,83,46,0]

class x25crc(object):
    """x25 CRC - based on checksum.h from mavlink library"""
    def __init__(self, buf=''):
        self.crc = 0xffff
        self.accumulate(buf)

    def accumulate(self, buf):
        '''add in some more bytes'''
        bytes = array.array('B')
        if isinstance(buf, array.array):
            bytes.extend(buf)
        else:
            bytes.fromstring(buf)
        accum = self.crc
        for b in bytes:
            tmp = b ^ (accum & 0xff)
            tmp = (tmp ^ (tmp<<4)) & 0xFF
            accum = (accum>>8) ^ (tmp<<8) ^ (tmp<<3) ^ (tmp>>4)
            accum = accum & 0xFFFF
        self.crc = accum

#-----------------------------------------------------------------------
def decode(buf):
    """decode a mavlink message"""
    print '--'
    print 'len:',len(buf)
    crc=x25crc()
    xdump(buf)
    magic, mlen, seq, srcSystem, srcComponent, msgId = struct.unpack('cBBBBB', buf[:6])
    print magic, mlen, seq, srcSystem, srcComponent, msgId

    crc.accumulate(buf[1:len(buf)-2]) # skip magic and cksum
    crc.accumulate(chr(MAVLINK_MESSAGE_CRCS[msgId]))
    print '\nwrong crc=%0x'%(crc.crc)

#-----------------------------------------------------------------------
def process(ser):
    """process the mavlink input stream"""

    buf=''
    while True:
        x = ser.read(1)
        if len(x) == 0:
            print "TIMEOUT"
        else:
            if ord(x) == 0xfe:
                if len(buf)>0:
                    decode(buf)
                    buf=''
            buf+=x
            #sys.stdout.write('%02x '%(ord(x)))
            sys.stdout.flush()

#-----------------------------------------------------------------------
def connect():
    """connect to the mavlink device"""

    # try and figure out the port on a mac.
    autoselect=1
    if autoselect and sys.platform == 'darwin':
        import glob
        candidates=glob.glob('/dev/tty*usb*')
        print 'candidate ports (%d):'%(len(candidates))
        for c in candidates:
            print '   ',c
        myport=candidates[0]
        mybaud=57600
        mybaud=115200
    else:
        myport=PORT
        mybaud=BAUD

    print 'connecting to:', myport
    ser = serial.Serial()
    ser.port=myport
    ser.baudrate=mybaud
    ser.parity=serial.PARITY_NONE
    ser.stopbits=serial.STOPBITS_ONE
    ser.bytesize=serial.EIGHTBITS
    ser.timeout=2
    ser.open()
    return ser

#-----------------------------------------------------------------------
def main():
    """the main thing!"""

    ser=connect()
    process(ser)

#-----------------------------------------------------------------------
if __name__=="__main__":
    main()
