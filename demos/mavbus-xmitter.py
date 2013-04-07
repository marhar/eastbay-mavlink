#!/usr/bin/python
#-----------------------------------------------------------------------
# mavbus-xmitter.py -- put mavlink messages onto the mavlink bus
#
# This is a demo program.
# Once I like how this is working, I will package appropriately.
#-----------------------------------------------------------------------

import sys
import array
import struct
import serial    # install from https://pypi.python.org/pypi/pyserial
import socket

#-----------------------------------------------------------------------
# set your port and baud rates here
#-----------------------------------------------------------------------

PORT='COM10'                       # typical windows port
PORT='/dev/tty.usbmodem621'        # typical mac port
BAUD=57600                         # baud rate for radio connection
BAUD=115200                        # baud rate for direct usb connection

#-----------------------------------------------------------------------
# transmitter socket
#-----------------------------------------------------------------------

MCADDR='239.239.250.1'
MCPORT=8001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)


#-----------------------------------------------------------------------
# manifest constants
#-----------------------------------------------------------------------

MAV_STARTB=0xfe      # this byte indicates start of mavlink packet

#-----------------------------------------------------------------------
# utility stuff
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
# checksum special note:
#
# each message type (0,1,2,...) has an extra one-byte magic number.
# heartbeat (message 0) has magic number of 50, so you can index this
# table with the message number to get the magic number.  After
# accumulating the bytes of the message, accumulate the magic number.
# this table is copied from the mavlink source.
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

#-----------------------------------------------------------------------
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
def decode2(buf):
    """decode and process a command"""
    # we don't do anything here
    pass

#-----------------------------------------------------------------------
lastseq=255
def decode(buf):
    """decode a mavlink message"""

    global lastseq
    print '-----------'
    xdump(buf)
    magic, mlen, seq, srcSystem, srcComponent, msgId = struct.unpack('<6B', buf[:6])
    b0,b1=struct.unpack('2B',buf[6+mlen:])
    givenCk=b0+b1*256
    crc=x25crc()
    crc.accumulate(buf[1:len(buf)-2]) # skip magic and cksum
    crc.accumulate(chr(MAVLINK_MESSAGE_CRCS[msgId]))

    print 'mlen=%d, seq=%d, sys=(%d,%d), msgId=%d, sums=(%04x,%04x)'%\
        (mlen,seq,srcSystem,srcComponent,msgId,givenCk,crc.crc)

    if crc.crc == givenCk:
        # good message, process it
        if seq != (lastseq+1)%256:
            print 'WARNING, lost message? seq=%d,lastseq=%d'%(seq,lastseq)
        lastseq=seq
        decode2(buf)
        sock.sendto(buf,(MCADDR,MCPORT))
    else:
        # complain!
        print 'BAD CRC on message'

#-----------------------------------------------------------------------
def timedread(ser,n):
    """read octets, complain upon timeout"""

    while True:
        x = ser.read(n)
        if len(x) == 0:
            print "TIMEOUT"
        else:
            return x

#-----------------------------------------------------------------------
def process(ser):
    """process the mavlink input stream"""

    while True:
        # scan stream until we see sync byte
        x = timedread(ser,1)
        if ord(x) == MAV_STARTB:
            #  read the length and rest of message, and process
            len=timedread(ser,1)
            rest=timedread(ser,4+ord(len)+2)
            buf=x
            buf+=len
            buf+=rest
            decode(buf)

#-----------------------------------------------------------------------
def connect():
    """connect to the mavlink device"""

    autoselect=1

    # here's some autoselect logic for mac
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
    print 'STARTING'
    process(ser)

#-----------------------------------------------------------------------
if __name__=="__main__":
    main()
