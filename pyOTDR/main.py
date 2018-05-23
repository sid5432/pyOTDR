#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import re
import json
import logging
if __name__ == '__main__':
    cdir = os.path.dirname( os.path.realpath(__file__) )
    sys.path.insert(0, cdir+"/..")


import pyOTDR

logger = logging.getLogger('pyOTDR')
logger.setLevel(logging.DEBUG)

def main():
    if len(sys.argv) < 2:
        print("USAGE: %s SOR_file [format]" % sys.argv[0])
        print("     : format: JSON (default) or XML")
        sys.exit()
    
    logging.basicConfig(format='%(message)s')
    # logging.basicConfig()
    
    filename = sys.argv[1]
    opformat = "JSON"
    if len(sys.argv) >= 3:
        opformat = "XML" if sys.argv[2] == "XML" else "JSON"
    
    status, results, tracedata = pyOTDR.sorparse(filename) 
    
    # construct data file name to dump results
    fn_strip, ext = os.path.splitext( os.path.basename(filename) )
    if opformat == "JSON":
        datafile = fn_strip+"-dump.json"
    else:
        datafile = fn_strip+"-dump.xml"
    
    with open(datafile,"w") as output:
        pyOTDR.tofile(results, output, format=opformat)
    
    # construct data file name
    fn_strip, ext = os.path.splitext( os.path.basename(filename) )
    opfile = fn_strip+"-trace.dat"
    
    with open(opfile,"w") as output:
        for xy in tracedata:
            output.write(xy)

# ==============================================
if __name__ == '__main__':
    main()
