#!/usr/bin/python

#-----------------------------------------------------------------------
# python mavlink testing
# t2 -- dumping of a mavlink message
#
# notes:
#
# requires serial package:
#    https://pypi.python.org/pypi/pyserial
#
# http://www.qgroundcontrol.org/mavlink/pymavlink
#
# mac serial detection:
#
# > ls /dev/*usb*
# ls: /dev/*usb*: No such file or directory
# ***now plug in radio***
# > ls /dev/*usb*
# /dev/cu.usbserial-A4015B9Q	/dev/tty.usbserial-A4015B9Q
#-----------------------------------------------------------------------

import sys
import serial

#PORT='COM10'
PORT='/dev/tty.usbserial-A4015B9Q'
PORT='/dev/tty.usbmodem411'
BAUD=57600
BAUD=115200

#-----------------------------------------------------------------------
# adapted from http://code.activestate.com/recipes/142812-hex-dumper
#-----------------------------------------------------------------------
xdumpf=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def xdump(src, length=16):
    """dump a string in classic hexdump format"""
    N=0;
    while src:
        s,src = src[:length],src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(xdumpf)
        print "%04X   %-*s   %s" % (N, length*3, hexa, s)
        N+=length

#-----------------------------------------------------------------------
# fe 09 e5 01 01 00 00 00 00 00 02 03 51 04 03 20 30
def process(ser):
    """process the mavlink input stream"""

    buf=''
    while True:
        x = ser.read(1)
        if len(x) == 0:
            print "TIMEOUT"
        else:
            buf+=x
            sys.stdout.write('%02x '%(ord(x)))
            sys.stdout.flush()

#-----------------------------------------------------------------------
def main():
    """the main thing!"""

    ser = serial.Serial()
    ser.port=PORT
    ser.baudrate=BAUD
    ser.parity=serial.PARITY_NONE
    ser.stopbits=serial.STOPBITS_ONE
    ser.bytesize=serial.EIGHTBITS
    ser.timeout=2
    print ser
    ser.open()

    process(ser)

#-----------------------------------------------------------------------
if __name__=="__main__":
    main()
