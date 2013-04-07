#!/usr/bin/python
#-----------------------------------------------------------------------
# python mavlink testing
# demo 1: basic reading
# connect to a mavlink unit and read the data stream
#-----------------------------------------------------------------------

import sys
import serial   # https://pypi.python.org/pypi/pyserial

# set these as necessary
#PORT="COM9"
#BAUD=57600
PORT='/dev/tty.usbmodem411'
BAUD=115200

#-----------------------------------------------------------------------
def main():
    """the main thing!"""

    ser = serial.Serial()
    ser.port=PORT
    ser.baudrate=BAUD
    ser.open()

    while True:
        while ser.inWaiting() > 0:
            x = ser.read(1)
            sys.stdout.write('%02x '%(ord(x)))
            sys.stdout.flush()

#-----------------------------------------------------------------------
if __name__=="__main__":
    main()
