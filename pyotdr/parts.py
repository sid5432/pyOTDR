import struct
from typing import BinaryIO

import crcmod
import logging

logger = logging.getLogger(__name__)

divider = (
    "--------------------------------------------------------------------------------"
)

# speed of light
sol = 299792.458 / 1.0e6  # = 0.299792458 km/usec


class FH:
    """
    wrapper around file handler to also process CRC checksum along the way
    """

    def __init__(self, filehandle: BinaryIO):
        self.filehandle = filehandle
        self.bufsize = 2048  # adjust as needed
        self.buffer = b""
        self.spaceleft = self.bufsize
        """
        Calculate the CRC16 CCITT checksum of *data*.
        
        (CRC16 CCITT: start 0xFFFF, poly 0x1021)
        same as:
        
        crcmod.mkCrcFun( 0x11021, initCrc=0xFFFF, xorOut=0x0000, rev=False)
        """
        self.crc16 = crcmod.predefined.Crc("crc-ccitt-false")

    def read(self, *args, **kargs):
        buf = self.filehandle.read(*args, **kargs)
        xlen = len(buf)
        if xlen > self.spaceleft:
            # process then clear buffer
            self.crc16.update(self.buffer)
            self.buffer = b""
            self.spaceleft = self.bufsize

        self.buffer += buf
        self.spaceleft -= xlen
        return buf

    def digest(self):
        # last part of the file
        self.crc16.update(self.buffer)
        return self.crc16.crcValue

    def seek(self, *args, **kargs):
        # assume a rewind, and reset buffer
        if args[0] == 0:
            self.buffer = b""
            self.spaceleft = self.bufsize
            self.crc16 = crcmod.predefined.Crc("crc-ccitt-false")

        return self.filehandle.seek(*args, **kargs)

    def tell(self) -> int:
        return self.filehandle.tell()

    def close(self) -> None:
        return self.filehandle.close()


def sorfile(filename: str) -> "FH":
    """
    return the file handle; need to close later;

    we assume that file content is
     - all read (not skipped)
     - only read once (except for the version 1 vs. 2 header; rewind at most once)
     - read sequentially
    these are needed for the CRC checksum calculation to work
    """
    try:
        fh = open(filename, "rb")
        return FH(fh)
    except IOError as e:
        logger.error("Failed to read {}".format(filename))
        raise e


# -----------------------------------------------------
def get_string(fh: BinaryIO) -> str:
    """
    Get string from the file handle. decode as utf-8
    """
    mystr = b""
    byte = fh.read(1)
    while byte != "":
        tt = struct.unpack("c", byte)[0]
        if tt == b"\x00":
            break
        mystr += tt
        byte = fh.read(1)

    return mystr.decode("utf-8")


def get_float(fh: "FH", nbytes: int) -> float:
    """get floating point; fh is the file handle"""
    tmp = fh.read(nbytes)
    if nbytes == 4:
        return struct.unpack("<f", tmp)[0]
    elif nbytes == 8:
        return struct.unpack("<d", tmp)[0]
    else:
        logger.error("parts.get_float(): Invalid number of bytes {}".format(nbytes))
        raise ValueError("Trying to get float of size > 8bytes")


def get_uint(fh: "FH", nbytes: int = 2) -> int:
    """
    get unsigned int (little endian), 2 bytes by default
    (assume nbytes is positive)
    """

    word = fh.read(nbytes)
    if nbytes == 2:
        # unsigned short
        return struct.unpack("<H", word)[0]
    elif nbytes == 4:
        # unsigned int
        return struct.unpack("<I", word)[0]
    elif nbytes == 8:
        # unsigned long long
        return struct.unpack("<Q", word)[0]
    else:
        logger.error("parts.get_uint(): Invalid number of bytes {}".format(nbytes))
        raise ValueError("Trying to get uint of size > 8bytes")


def get_signed(fh: "FH", nbytes: int = 2) -> int:
    """
    get signed int (little endian), 2 bytes by default
    (assume nbytes is positive)
    """

    word = fh.read(nbytes)
    if nbytes == 2:
        # unsigned short
        val = struct.unpack("<h", word)[0]
    elif nbytes == 4:
        # unsigned int
        val = struct.unpack("<i", word)[0]
    elif nbytes == 8:
        # unsigned long long
        val = struct.unpack("<q", word)[0]
    else:
        logger.error("parts.get_signed(): Invalid number of bytes {}".format(nbytes))
        raise ValueError("Trying to get int of size > 8bytes")

    return val


def get_hex(fh: "FH", nbytes: int = 1) -> str:
    """
    get nbyte bytes (1 by default)
    and display as hexidecimal
    """
    hstr = ""
    for i in range(nbytes):
        b = "%02X " % ord(fh.read(1))
        hstr += b
    return hstr


def slurp(fh: "FH", bname: str, results: dict) -> str:
    """
    fh: file handle;
    results: dict for results;

    just read this block without processing
    """
    status = "nok"

    try:
        ref = results["blocks"][bname]
        startpos = ref["pos"]
        fh.seek(startpos)
    except:
        # TODO this should raise
        logger.error("{} block starting position unknown".format(bname))
        return status

    nn = ref["size"]

    fh.read(nn)

    status = "ok"
    return status
