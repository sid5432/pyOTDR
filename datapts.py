#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import functools
from . import parts

sep = "    :"

def process(fh, results, tracedata, debug=False, logfile=sys.stderr):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "DataPts"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = "DataPts.process():"
    ref = None
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        print(pname, " ", bname, "block starting position unknown", file=logfile)
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname+'\0':
            print(pname, " incorrect header ", mystr, file=logfile)
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    # extra parameters
    xref['_datapts_params'] = { 'xscaling': 1, 'offset': 'STV' }
    # method used by STV: minimum reading shifted to zero
    # method used by AFL/Noyes Trace.Net: maximum reading shifted to zero (approx)
    
    status = _process_data(fh, results, tracedata, debug=debug, logfile=logfile)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

# ================================================================
def _process_data(fh, results, tracedata, debug=False, logfile=sys.stderr, dumptrace=True):
    """ process version 1 format """
    bname = "DataPts"
    xref  = results[bname]
    
    try:
        # we assume SupParams block already processed
        model = results['SupParams']['OTDR']
    except:
        model = ""

    # special case:
    # old Noyes/AFL OFL250 model is off by factor of 10
    if model == 'OFL250':
        xref['_datapts_params']['xscaling'] = 0.1
    
    if debug:
        print("%s [initial 12 byte header follows]" % sep, file=logfile)
    
    N = parts.get_uint(fh, 4)
    # confirm N equal to FxdParams num data points
    if N != results['FxdParams']['num data points']:
        print("!!! WARNING !!! block says number of data points ",\
        "is ",N," instead of ",results['FxdParams']['num data points'])
    
    xref['num data points'] = N
    if debug:
        print("%s num data points = %d" % (sep,N), file=logfile)
    
    val = parts.get_signed(fh, 2)
    xref['num traces'] = val
    if debug:
        print("%s number of traces = %d" % (sep,val), file=logfile)
    
    if val > 1:
        print("WARNING!!!: Cannot handle multiple traces (%d); aborting" % val)
        sys.exit()
    
    val = parts.get_uint(fh, 4)
    xref['num data points 2'] = val
    if debug:
        print("%s num data points again = %d" % (sep,val), file=logfile)

    val = parts.get_uint(fh, 2)
    scaling_factor = val / 1000.0
    xref['scaling factor'] = scaling_factor
    if debug:
        print("%s scaling factor = %f" % (sep,scaling_factor), file=logfile)
    
    # .....................................
    # adjusted resolution
    dx = results['FxdParams']['resolution']
    dlist = []
    for i in range(N):
        val = parts.get_uint(fh, 2)
        dlist.append(val)
    
    ymax = max( dlist )
    ymin = min( dlist )
    fs = 0.001* scaling_factor
    disp_min = "%.3f" % (ymin * fs)
    disp_max = "%.3f" % (ymax * fs)
    xref['max before offset'] = float(disp_max)
    xref['min before offset'] = float(disp_min)
    
    if debug:
        print("%s before applying offset: max %s dB, min %s dB" % (sep, disp_max, disp_min), file=logfile)
    
    # .........................................
    # save to file
    offset = xref['_datapts_params']['offset']
    xscaling = xref['_datapts_params']['xscaling']
    
    # convert/scale to dB
    if offset == 'STV':
        nlist = [(ymax - x )*fs for x in dlist]
    elif offset == 'AFL':
        nlist = [(ymin - x )*fs for x in dlist]
    else: # invert
        nlist = [-x*fs for x in dlist]
    
    for i in range(N):
        # more work but (maybe) less rounding issues
        x = dx*i*xscaling / 1000.0 # output in km
        tracedata.append( "%f\t%f" % (x, nlist[i]) )
    
    # .........................................
    status = 'ok'
    
    return status
