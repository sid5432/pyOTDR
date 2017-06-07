#!/usr/bin/python
import sys
import os

import parts
import mapblock
import genparams
import supparams
import fxdparams
import keyevents
import datapts
import cksum
import dump

# -----------------------------------------------------
def sorparse(filename, debug=False, logfile=sys.stdout, dumptrace=True):
    """ 
    parse SOR file;
    return status and result (dictionary)
    """
    fh = parts.sorfile(filename)
    if fh == None:
        return "Error opening file", None, None
    
    results = dict()
    status = 'ok'
    
    results['filename'] = os.path.basename( filename )
    
    tracedata = []
    
    # map block -------------------------------
    status = mapblock.process(fh, results, debug=debug, logfile=logfile)
    if status != 'ok':
        return status, results, tracedata
    
    
    # all the other blocks --------------------
    klist = sorted( results['blocks'], key=lambda x: results['blocks'][x]['order'] )
    
    for bname in klist:
        ref = results['blocks'][bname]
        bname = ref['name']
        bsize = ref['size']
        start = ref['pos']
        
        if debug:
            print >>logfile, "MAIN:  %s block: %d bytes, start pos 0x%X (%d)" % (bname, bsize, start, start)
        
        if bname == 'GenParams':
            status = genparams.process(fh, results, debug=debug, logfile=logfile)
        elif bname == 'SupParams':
            status = supparams.process(fh, results, debug=debug, logfile=logfile)
        elif bname == 'FxdParams':
            status = fxdparams.process(fh, results, debug=debug, logfile=logfile)
        elif bname == 'DataPts':
            status = datapts.process(fh, results, tracedata, debug=debug, logfile=logfile)
        elif bname == 'KeyEvents':
            status = keyevents.process(fh, results, debug=debug, logfile=logfile)
        elif bname == 'Cksum':
            status = cksum.process(fh, results, debug=debug, logfile=logfile)
        else:
            parts.slurp(fh, bname, results, debug=debug, logfile=logfile)
            status = 'ok'
            pass
        
        if debug:
            print >>logfile
            
        # stop immediately if any errors
        if status != 'ok':
            break
    
    # ...................................
    fh.close()
    
    return status, results, tracedata
    

# ==============================================
if __name__ == '__main__':
    import os
    
    if len(sys.argv) < 2:
        print "USAGE: %s SOR_file" % sys.argv[0]
        sys.exit()
    
    filename = sys.argv[1]
    
    logfile = sys.stdout
    # logfile = open(os.devnull,"w")
    
    status, results, tracedata = sorparse(filename, debug=True, logfile=logfile)
    
    # construct data file name to dump results
    fn_strip, ext = os.path.splitext( os.path.basename(filename) )
    datafile = fn_strip+"-dump.json"
    
    with open(datafile,"w") as output:
        dump.tofile(results, output)
    
    # construct data file name
    fn_strip, ext = os.path.splitext( os.path.basename(filename) )
    opfile = fn_strip+"-trace.dat"
    
    with open(opfile,"w") as output:
        for xy in tracedata:
            print >>output, xy
    
