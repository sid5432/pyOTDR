#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os

from . import parts
from . import mapblock 
from . import genparams
from . import supparams
from . import fxdparams
from . import keyevents
from . import datapts
from . import cksum
from . import dump

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
            print("MAIN:  %s block: %d bytes, start pos 0x%X (%d)" % (bname, bsize, start, start), file=logfile)
        
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
            print(file=logfile)
            
        # stop immediately if any errors
        if status != 'ok':
            break
    
    # ...................................
    fh.close()
    
    return status, results, tracedata
    

