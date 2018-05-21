#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import logging
import crcmod
from . import parts

logger = logging.getLogger('pyOTDR')

def process(fh, results, debug=False):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "Cksum"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = "Cksum.process():"
    sep = "    :"
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        logger.error('{} {} block starting position unknown '.format(pname, bname))
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname+'\0':
            logger.error('{} incorrect header {}'.format(pname, mystr))
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    # before reading the (file) checksum, get the cumulative checksum
    xref['checksum_ours'] = digest = fh.digest()
    csum = xref['checksum'] = parts.get_uint(fh, 2)
    
    if digest == csum:
        xref['match'] = True
        verdict = "MATCHES!"
    else:
        xref['match'] = False
        verdict = "DOES NOT MATCH!"

    logger.debug("%s checksum from file %d (0x%X)" % (sep, csum, csum))
    logger.debug("%s checksum calculated %d (0x%X) %s" % (sep, digest, digest, verdict))
    
    status = 'ok'
    return status
