#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import os
import logging

from . import parts
from . import mapblock 
from . import genparams
from . import supparams
from . import fxdparams
from . import keyevents
from . import datapts
from . import cksum

logger = logging.getLogger('pyOTDR')

# -----------------------------------------------------
def sorparse(filename, dumptrace=True):
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
    status = mapblock.process(fh, results)
    if status != 'ok':
        return status, results, tracedata
    
    
    # all the other blocks --------------------
    klist = sorted( results['blocks'], key=lambda x: results['blocks'][x]['order'] )
    
    for bname in klist:
        ref = results['blocks'][bname]
        bname = ref['name']
        bsize = ref['size']
        start = ref['pos']
        

        logger.debug("\nMAIN:  {} block: {:d} bytes, start pos {:#X} ({:d})".format(bname, bsize, start, start))
        
        if bname == 'GenParams':
            status = genparams.process(fh, results)
        elif bname == 'SupParams':
            status = supparams.process(fh, results)
        elif bname == 'FxdParams':
            status = fxdparams.process(fh, results)
        elif bname == 'DataPts':
            status = datapts.process(fh, results, tracedata)
        elif bname == 'KeyEvents':
            status = keyevents.process(fh, results)
        elif bname == 'Cksum':
            status = cksum.process(fh, results)
        else:
            parts.slurp(fh, bname, results)
            status = 'ok'
            pass
            
        # stop immediately if any errors
        if status != 'ok':
            break
    
    # ...................................
    fh.close()
    
    return status, results, tracedata
    

