#!/usr/bin/python
import sys
import os
cdir = os.path.dirname( os.path.realpath(__file__) )
import crcmod

sys.path.insert(0, cdir+"/../..")


from pyOTDR import cksum
from pyOTDR import read

def crc16_ccitt(data):
    """
    Calculate the CRC16 CCITT checksum of *data*.
    
    (CRC16 CCITT: start 0xFFFF, poly 0x1021)
    same as:
    
    crcmod.mkCrcFun( 0x11021, initCrc=0xFFFF, xorOut=0x0000, rev=False)
    """
    crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
    digest = crc16(data)
    # print hex(crc16(data))
    # return hex(crc16(data))[2:].upper().zfill(4)
    return digest

def test_cksum():
    # sanity check algorithm
    digest = crc16_ccitt("123456789")
    # print  "* check crc-ccitt-false: ",digest
    
    assert digest == 0x29B1
    
    filename = cdir+"/../data/demo_ab.sor"
    with open(filename, mode='rb') as fh:
        data = fh.read()
    
    assert len(data) == 25708
    
    file_chk = ord(data[-1])*256 + ord(data[-2])
    assert file_chk == 38827

    newdata = data[0:-2]
    
    # print "* trunc size is ",len(newdata)
    
    digest = crc16_ccitt(newdata)
    
    assert digest == file_chk
    
    devnull = open( os.devnull, "w")
    # test against module (SOR version 1)
    status, results, tracedata = read.sorparse(filename, debug=True, logfile=devnull)
    
    # print "* Our calcuated check sum: ",digest
    assert results['Cksum']['checksum_ours'] == digest
    
    # SOR version 2
    filename = cdir+"/../data/sample1310_lowDR.sor"
    status, results, tracedata = read.sorparse(filename, debug=True, logfile=devnull)
    
    assert results['Cksum']['checksum_ours'] == 62998
    assert results['Cksum']['checksum'] == 59892
    
    return
        
# ==========================================
if __name__ == '__main__':
    test_cksum()
    
