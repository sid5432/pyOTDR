import os
import crcmod

from pyotdr.read import sorparse

cdir = os.path.dirname(os.path.realpath(__file__))


def crc16_ccitt(data):
    """
    Calculate the CRC16 CCITT checksum of *data*.

    (CRC16 CCITT: start 0xFFFF, poly 0x1021)
    same as:

    crcmod.mkCrcFun( 0x11021, initCrc=0xFFFF, xorOut=0x0000, rev=False)
    """
    crc16 = crcmod.predefined.mkCrcFun("crc-ccitt-false")
    digest = crc16(data)
    return digest


def test_cksum():
    # sanity check algorithm
    digest = crc16_ccitt(b"123456789")

    assert digest == 0x29B1

    filename = cdir + "/../data/demo_ab.sor"
    with open(filename, mode="rb") as fh:
        data = fh.read()

    assert len(data) == 25708

    file_chk = data[-1] * 256 + data[-2]

    assert file_chk == 38827

    newdata = data[0:-2]

    # print "* trunc size is ",len(newdata)

    digest = crc16_ccitt(newdata)

    assert digest == file_chk

    devnull = open(os.devnull, "w")
    # test against module (SOR version 1)
    status, results, tracedata = sorparse(filename)
    # print(results)
    # print "* Our calcuated check sum: ",digest
    assert results["Cksum"]["checksum_ours"] == digest

    # print("--------------- ok version 1 -----------------------")

    # SOR version 2
    filename = cdir + "/../data/sample1310_lowDR.sor"
    status, results, tracedata = sorparse(filename)

    assert results["Cksum"]["checksum_ours"] == 62998
    assert results["Cksum"]["checksum"] == 59892

    # print("--------------- ok version 2 -----------------------")

    return


# ==========================================
if __name__ == "__main__":
    test_cksum()
