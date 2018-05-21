#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import struct
import crcmod
import logging

logger = logging.getLogger('pyOTDR')

divider = "--------------------------------------------------------------------------------"

# speed of light
sol = 299792.458/1.0e6 # = 0.299792458 km/usec

# -----------------------------------------------------
def sorfile(filename):
    """
    return the file handle; need to close later;
    
    we assume that file content is 
     - all read (not skipped)
     - only read once (except for the version 1 vs. 2 header; rewind at most once)
     - read sequentially
    these are needed for the CRC checksum calculation to work
    """
    try:
        fh0 = open(filename,"rb")
    except IOError:
        logger.error("Failed to read {}".format(filename))
        return None
    
    # wrapper around file handler to also process CRC checksum along the way
    class FH:
        def __init__(self):
            self.bufsize = 2048 # adjust as needed
            self.buffer = b""
            self.spaceleft = self.bufsize
            """
            Calculate the CRC16 CCITT checksum of *data*.
            
            (CRC16 CCITT: start 0xFFFF, poly 0x1021)
            same as:
            
            crcmod.mkCrcFun( 0x11021, initCrc=0xFFFF, xorOut=0x0000, rev=False)
            """
            self.crc16 = crcmod.predefined.Crc('crc-ccitt-false')
            return
        
        def read(self,*args,**kargs):
            buf = fh0.read(*args,**kargs)
            xlen = len(buf)
            if xlen > self.spaceleft:
                # process then clear buffer
                self.crc16.update( self.buffer )
                self.buffer = b""
                self.spaceleft = self.bufsize
            
            self.buffer += buf
            self.spaceleft -= xlen
            return buf
        
        def digest(self):
            # last part of the file
            self.crc16.update( self.buffer )
            return self.crc16.crcValue

        def seek(self,*args,**kargs):
            # assume a rewind, and reset buffer
            if args[0] == 0:
                self.buffer = b""
                self.spaceleft = self.bufsize
                self.crc16 = crcmod.predefined.Crc('crc-ccitt-false')
            
            return fh0.seek(*args,**kargs)

        def tell(self,*args,**kargs):
            return fh0.tell(*args,**kargs)
        
        def close(self,*args,**kargs):
            return fh0.close(*args,**kargs)
    
    fh = FH()
    
    return fh

# -----------------------------------------------------
def get_string(fh):
    """fh is the file handle """
    mystr = b''
    byte = fh.read(1)
    while byte != '':
        tt = struct.unpack("c",byte)[0]
        if tt == b"\x00":
            break
        mystr += tt
        byte = fh.read(1)
        
    return mystr.decode('utf-8')

# -----------------------------------------------------
def get_float(fh, nbytes):
    """get floating point; fh is the file handle """
    tmp = fh.read(nbytes)
    if nbytes == 4:
        val = struct.unpack("<f", tmp)[0]
    elif nbytes == 8:
        val = struct.unpack("<d", tmp)[0]
    else:
        logger.error("parts.get_float(): Invalid number of bytes {}".format(nbytes))
        # TODO this should raise
        val = None
    
    return val

# -----------------------------------------------------
def get_uint(fh, nbytes=2):
    """
    get unsigned int (little endian), 2 bytes by default
    (assume nbytes is positive)
    """
    
    word = fh.read(nbytes)
    if nbytes == 2:
        # unsigned short
        val = struct.unpack("<H",word)[0]
    elif nbytes == 4:
        # unsigned int
        val = struct.unpack("<I",word)[0]
    elif nbytes == 8:
        # unsigned long long
        val = struct.unpack("<Q",word)[0]
    else:
        val = None
        # TODO this should raise
        logger.error("parts.get_uint(): Invalid number of bytes {}".format(nbytes))
    
    return val

# -----------------------------------------------------
def get_signed(fh, nbytes=2):
    """
    get signed int (little endian), 2 bytes by default
    (assume nbytes is positive)
    """
    
    word = fh.read(nbytes)
    if nbytes == 2:
        # unsigned short
        val = struct.unpack("<h",word)[0]
    elif nbytes == 4:
        # unsigned int
        val = struct.unpack("<i",word)[0]
    elif nbytes == 8:
        # unsigned long long
        val = struct.unpack("<q",word)[0]
    else:
        val = None
        # TODO this should raise
        logger.error("parts.get_signed(): Invalid number of bytes {}".format(nbytes))
    
    return val

# -----------------------------------------------------
def get_hex(fh, nbytes=1):
    """
    get nbyte bytes (1 by default)
    and display as hexidecimal
    """
    hstr = ""
    for i in range(nbytes):
        b = "%02X " % ord(fh.read(1))
        hstr += b
    
    return hstr

# -----------------------------------------------------
def slurp(fh, bname, results):
    """
    fh: file handle;
    results: dict for results;
    
    just read this block without processing
    """
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        # TODO this should raise
        logger.error('{} block starting position unknown'.format(bname))
        return status
    
    nn = ref['size']
    
    fh.read(nn)
    
    status = 'ok'
    return status
