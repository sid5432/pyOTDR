#!/usr/bin/python
import sys
import parts

def process(fh, results, debug=False, logfile=sys.stderr):
    """
    fh: file handle;
    results: dict for results;
    """
    
    fh.seek(0)
    
    tt = parts.get_string(fh)
    if tt == 'Map':
        results['format'] = 2
        if debug:
            print >> logfile, "MAIN: bellcore 2.x version"
    else:
        results['format'] = 1
        if debug:
            print >> logfile, "MAIN: bellcore 1.x version"
        # rewind to start
        fh.seek(0)
    
    # get version number
    results['version'] = "%.2f" % (parts.get_uint(fh, 2) * 0.01)
    
    # get number of bytes in map block
    results['mapblock'] = dict();
    results['mapblock']['nbytes'] = parts.get_uint(fh,4)
    
    if debug:
        print >> logfile, "MAIN: Version %s, block size %d bytes; next position 0x%X" % \
        (results['version'], results['mapblock']['nbytes'], fh.tell())
    
    # get number of block; not including the Map block
    results['mapblock']['nblocks'] = parts.get_uint(fh, 2) - 1
    
    if debug:
        print >> logfile, "MAIN: %d blocks to follow; next position 0x%X" % \
        (results['mapblock']['nblocks'], fh.tell() )
        print >> logfile, parts.divider
    
    # get block information
    if debug:
        print >> logfile, "MAIN: BLOCKS:"
    
    results['blocks'] = dict()
    startpos = results['mapblock']['nbytes']
    
    for i in xrange( results['mapblock']['nblocks'] ):
        bname = parts.get_string(fh)
        bver  = "%.2f" % (parts.get_uint(fh,2) * 0.01)
        bsize = parts.get_uint(fh,4)
        
        ref = { 'name': bname, 'version': bver, 'size': bsize, 'pos': startpos, 'order': i }
        results['blocks'][bname] = ref
        
        if debug:
            print >> logfile, "MAIN: %s block: version %s," % (bname, bver),
            print >> logfile, "block size %d bytes," % (bsize),
            print >> logfile, "start at pos 0x%X" % startpos
        
        # start position of next block
        startpos += bsize
    
    if debug:
        print >> logfile, parts.divider,"\n"
        print >> logfile, "MAIN: next position 0x%X" % fh.tell()
        print >> logfile, parts.divider,"\n\n"
    
    status = 'ok'
    return status

