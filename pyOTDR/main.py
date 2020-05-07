#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import logging
import argparse
if __name__ == '__main__':
    cdir = os.path.dirname( os.path.realpath(__file__) )
    sys.path.insert(0, cdir+"/..")


import pyOTDR

logger = logging.getLogger('pyOTDR')
logger.setLevel(logging.DEBUG)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('SOR_file', type=str, help='Name of the sor file to transform')
    parser.add_argument('format', type=str, default='JSON', help='Output format : JSON or XML', nargs='?')
    args = parser.parse_args()
    
    logging.basicConfig(format='%(message)s')
    # logging.basicConfig()
    
    filename = args.SOR_file
    opformat = args.format
    
    _, results, tracedata = pyOTDR.sorparse(filename) 
    
    # construct data file name to dump results
    fn_strip, _ = os.path.splitext( os.path.basename(filename) )
    if opformat == "JSON":
        datafile = fn_strip+"-dump.json"
    else:
        datafile = fn_strip+"-dump.xml"
    
    with open(datafile,"w") as output:
        pyOTDR.tofile(results, output, format=opformat)
    
    # construct data file name
    fn_strip, _ = os.path.splitext( os.path.basename(filename) )
    opfile = fn_strip+"-trace.dat"
    
    with open(opfile,"w") as output:
        for xy in tracedata:
            output.write(xy)

# ==============================================
if __name__ == '__main__':
    main()