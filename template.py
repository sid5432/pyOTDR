#!/usr/bin/python
import sys
import parts

sep = "    :"

def process(fh, results, debug=False, logfile=sys.stderr):
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
    
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

