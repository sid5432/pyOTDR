import os
import json

cdir = os.path.dirname(os.path.realpath(__file__))


from pyotdr.read import sorparse
from pyotdr import parts


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in list(obj.items()))
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def _compare_(sor_filename):

    filename = cdir + "/../data/" + sor_filename
    fh = parts.sorfile(filename)
    assert fh != None
    fh.close()

    status, results, tracedata = sorparse(filename)

    assert status == "ok"

    # load and compare JSON file
    fn_strip, ext = os.path.splitext(os.path.basename(filename))
    datafile = fn_strip + "-dump.json"

    jsonfile = cdir + "/../data/" + datafile

    with open(jsonfile) as jsf:
        jold = dict(json.load(jsf))

    jnew = json.dumps(results, sort_keys=True)
    jnew = json.loads(jnew)

    jold = ordered(jold)
    jnew = ordered(jnew)

    assert jold == jnew

    # load and compare trace data
    tfile = fn_strip + "-trace.dat"
    tfile = cdir + "/../data/" + tfile

    with open(tfile) as jsf:
        count = 0
        for line in jsf:
            assert line.strip("\n") == tracedata[count].strip("\n")
            count += 1

    return


def test_read1():
    _compare_("demo_ab.sor")
    return


def test_read2():
    _compare_("sample1310_lowDR.sor")
    return


def test_read3():
    _compare_("M200_Sample_005_S13.sor")
    return
