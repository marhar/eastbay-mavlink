#!/usr/bin/python

import socket
import struct

ADDR='239.239.250.1'
PORT=8001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('',PORT))
mreq = struct.pack("4sl", socket.inet_aton(ADDR), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

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



while True:
    (buf, sender) = sock.recvfrom(300)
    xdump(buf)
