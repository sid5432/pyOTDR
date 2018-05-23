#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import logging
from . import parts

logger = logging.getLogger('pyOTDR')

def process(fh, results): 
    """
    fh: file handle;
    results: dict for results;
    """
    
    fh.seek(0)
    
    tt = parts.get_string(fh)
    if tt == 'Map':
        results['format'] = 2
        logger.debug("MAIN: bellcore 2.x version")
    else:
        results['format'] = 1
        logger.debug("MAIN: bellcore 1.x version")
        # rewind to start
        fh.seek(0)
    
    # get version number
    results['version'] = "%.2f" % (parts.get_uint(fh, 2) * 0.01)
    
    # get number of bytes in map block
    results['mapblock'] = dict();
    results['mapblock']['nbytes'] = parts.get_uint(fh,4)
    
    logger.debug("MAIN: Version {}, block size {:d} bytes; next position {:#X}".format( \
        results['version'], results['mapblock']['nbytes'], fh.tell()))
    
    # get number of block; not including the Map block
    results['mapblock']['nblocks'] = parts.get_uint(fh, 2) - 1
    
    logger.debug("MAIN: {:d} blocks to follow; next position {:#X}X".format( \
                results['mapblock']['nblocks'], fh.tell()))
    logger.debug(parts.divider)
    
    # get block information
    logger.debug("MAIN: BLOCKS:")
    
    results['blocks'] = dict()
    startpos = results['mapblock']['nbytes']
    
    for i in range( results['mapblock']['nblocks'] ):
        bname = parts.get_string(fh)
        bver  = "%.2f" % (parts.get_uint(fh,2) * 0.01)
        bsize = parts.get_uint(fh,4)
        
        ref = { 'name': bname, 'version': bver, 'size': bsize, 'pos': startpos, 'order': i }
        results['blocks'][bname] = ref
        
        logger.debug("MAIN: {}  block: version {},".format(bname, bver))
        logger.debug("block size {:d} bytes,".format(bsize))
        logger.debug("start at pos {:#X}".format(startpos))
    
        # start position of next block
        startpos += bsize
    
    logger.debug(parts.divider+"\n")
    logger.debug("MAIN: next position {:#X}".format(fh.tell()))
    logger.debug(parts.divider+"\n")

    status = 'ok'
    return status

