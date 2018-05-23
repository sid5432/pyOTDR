#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import logging
from . import parts

logger = logging.getLogger('pyOTDR')

sep = "    :"

def process(fh, results):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "SupParams"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = "SupParams.process():"
    ref = None
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        logger.debug('{} {} block starting position unknown'.format(pname, bname) )
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname+'\0':
            logger.error('{} incorrect header {}'.format(pname, mystr))
            return status
    
    results[bname] = dict()
    
    # version 1 and 2 are the same
    status = process_supparam(fh, results)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

# ================================================================
def process_supparam(fh, results):
    """ process SupParams fields """
    bname = "SupParams"
    xref  = results[bname]
    
    fields = (
              "supplier", # ............. 0
              "OTDR", # ................. 1
              "OTDR S/N", # ............. 2
              "module", # ............... 3
              "module S/N", # ........... 4
              "software", # ............. 5
              "other", # ................ 6
             )
    
    count = 0
    for field in fields:
        xstr = parts.get_string(fh)
        logger.debug("{} {}. {}: {}".format(sep, count, field, xstr))
        
        xref[field] = xstr
        count += 1
    
    status = 'ok'
    
    return status

