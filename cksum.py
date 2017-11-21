#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import crcmod
from . import parts

def process(fh, results, debug=False, logfile=sys.stderr):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "Cksum"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = "Cksum.process():"
    ref = None
    sep = "    :"
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        print(pname," ",bname,"block starting position unknown", file=logfile)
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname+'\0':
            print(pname," incorrect header ", mystr, file=logfile)  
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
    

    if debug:
        print("%s checksum from file %d (0x%X)" % (sep, csum, csum), file=logfile)  
        print("%s checksum calculated %d (0x%X) %s" % (sep, digest, digest, verdict), file=logfile)
    
    status = 'ok'
    return status

