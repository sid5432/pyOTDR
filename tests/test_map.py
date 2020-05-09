import os

cdir = os.path.dirname(os.path.realpath(__file__))

from pyotdr.read import sorparse
from pyotdr import parts


def test_map():
    filename = cdir + "/../data/demo_ab.sor"
    fh = parts.sorfile(filename)
    assert fh != None
    fh.close()

    status, results, trace = sorparse(filename)

    assert status == "ok"

    # map block
    ref = results["blocks"]
    assert ref["Cksum"]["pos"] == 25706
    assert ref["Cksum"]["version"] == "1.00"

    assert ref["DataPts"]["pos"] == 328
    assert ref["DataPts"]["size"] == 23564

    return


# ==================================
if __name__ == "__main__":
    test_map()
