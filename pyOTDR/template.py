#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
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
    bname = "TBD"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = bname+".process():"
    ref = None
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        logger.error('{} {} block starting position unknown'.format(pname, bname))
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize)
        if mystr != bname+'\0':
            logger.error('{}  incorrect header {} '.format(pname, mystr))
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

