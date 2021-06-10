import sys
import os

cdir = os.path.dirname(os.path.realpath(__file__))

from pyotdr import parts


def file1():
    """SOR version 1 file"""
    filename = cdir + "/../data/demo_ab.sor"
    return filename


def file2():
    """SOR version 2 file"""
    filename = cdir + "/../data/sample1310_lowDR.sor"
    return filename


# -------------------------------------------------------
def test_get_string():
    """test get_string"""
    filename = file2()
    fh = parts.sorfile(filename)
    assert fh != None

    mystr = parts.get_string(fh)
    assert mystr == "Map"

    assert fh.tell() == 4
    fh.close()

    return


# -------------------------------------------------------
def test_get_uint():
    """test get_unsigned int (2 or 4)"""
    filename = file1()
    fh = parts.sorfile(filename)
    assert fh != None

    val = parts.get_uint(fh, nbytes=2)
    assert val == 100
    assert fh.tell() == 2

    val = parts.get_uint(fh, nbytes=4)
    assert val == 148
    assert fh.tell() == 6

    fh.close()

    return


# -------------------------------------------------------
def test_get_hex():
    """test hex conversion"""
    filename = file1()
    fh = parts.sorfile(filename)
    assert fh != None

    hstr = parts.get_hex(fh, 8)
    assert hstr == "64 00 94 00 00 00 0A 00 "
    fh.close()

    return


# -------------------------------------------------------
def test_get_signed():
    """test signed integer conversion"""
    filename = file2()
    fh = parts.sorfile(filename)
    assert fh != None

    fh.seek(461)
    fstr = parts.get_signed(fh, 2)
    assert fstr == 343

    fstr = parts.get_signed(fh, 2)
    assert fstr == 22820

    fstr = parts.get_signed(fh, 4)
    assert fstr == -38395

    fstr = parts.get_signed(fh, 8)
    assert fstr == 6002235321314002225

    fh.close()

    return


# ==================================
if __name__ == "__main__":
    test_get_string()
    test_get_uint()
    test_get_hex()
    test_get_signed()
