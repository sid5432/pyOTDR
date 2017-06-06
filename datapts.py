#!/usr/bin/python
import sys
import os
import functools
import parts

sep = "    :"

def process(fh, results, debug=False, logfile=sys.stderr, dumptrace=True):
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
    
    # construct data file name
    fn_strip, ext = os.path.splitext( os.path.basename(results['filename']) )
    datafile = fn_strip+"-trace.dat"
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        print >>logfile, pname," ",bname,"block starting position unknown"
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize)
        if mystr != bname+'\0':
            print >>logfile, pname," incorrect header ",mystr
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    # extra parameters
    results['_datapts_params'] = { 'xscaling': 1, 'offset': 'STV' }
    # method used by STV: minimum reading shifted to zero
    # method used by AFL/Noyes Trace.Net: maximum reading shifted to zero (approx)
    
    status = _process_data(fh, results, datafile, debug=debug, logfile=logfile, dumptrace=dumptrace)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

# ================================================================
def _process_data(fh, results, datafile, debug=False, logfile=sys.stderr, dumptrace=True):
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
        results['_datapts_params']['xscaling'] = 0.1
    
    if debug:
        print >>logfile,"%s [initial 12 byte header follows]" % sep
    
    N = parts.get_uint(fh, 4)
    # confirm N equal to FxdParams num data points
    if N != results['FxdParams']['num data points']:
        print "!!! WARNING !!! block says number of data points ",\
        "is ",N," instead of ",results['FxdParams']['num data points']
    
    xref['num data points'] = N
    if debug:
        print >>logfile,"%s num data points = %d" % (sep,N)
    
    val = parts.get_uint(fh, 2)
    if debug:
        print >>logfile,"%s unknown #1 = %d" % (sep,val)
    
    val = parts.get_uint(fh, 4)
    if debug:
        print >>logfile,"%s num data points again = %d" % (sep,val)

    val = parts.get_uint(fh, 2)
    scaling_factor = val / 1000.0
    if debug:
        print >>logfile,"%s scaling factor = %f" % (sep,scaling_factor)
    
    # .....................................
    # adjusted resolution
    dx = results['FxdParams']['resolution']
    dlist = []
    for i in xrange(N):
        val = parts.get_uint(fh, 2)
        dlist.append(val)
    
    ymax = max( dlist )
    ymin = min( dlist )
    fs = 0.001* scaling_factor
    disp_min = "%.3f" % (ymin * fs)
    disp_max = "%.3f" % (ymax * fs)
    if debug:
        print >>logfile,"%s before applying offset: max %s dB, min %s dB" % (sep, disp_max, disp_min)
    
    # .........................................
    # save to file
    if dumptrace:
        offset = results['_datapts_params']['offset']
        xscaling = results['_datapts_params']['xscaling']
        
        # convert/scale to dB
        if offset == 'STV':
            nlist = [(ymax - x )*fs for x in dlist]
        elif offset == 'AFL':
            nlist = [(ymin - x )*fs for x in dlist]
        else: # invert
            nlist = [-x*fs for x in dlist]
        
        with open(datafile,"w") as output:
            for i in xrange(N):
                # more work but (maybe) less rounding issues
                x = dx*i*xscaling / 1000.0 # output in kkm
                print >>output, "%f\t%f" % (x, nlist[i])
    
    # .........................................
    status = 'ok'
    
    return status
