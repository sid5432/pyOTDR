#!/usr/bin/python
import sys
import crcmod
import parts

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
        print >>logfile, "%s checksum from file %d (0x%X)" % (sep, csum, csum)
        print >>logfile, "%s checksum calculated %d (0x%X) %s" % (sep, digest, digest, verdict)
    
    status = 'ok'
    return status

