#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
from . import parts

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
            print("MAIN: bellcore 2.x version", file=logfile)
    else:
        results['format'] = 1
        if debug:
            print( "MAIN: bellcore 1.x version", file=logfile)
        # rewind to start
        fh.seek(0)
    
    # get version number
    results['version'] = "%.2f" % (parts.get_uint(fh, 2) * 0.01)
    
    # get number of bytes in map block
    results['mapblock'] = dict();
    results['mapblock']['nbytes'] = parts.get_uint(fh,4)
    
    if debug:
        print("MAIN: Version %s, block size %d bytes; next position 0x%X" % \
        (results['version'], results['mapblock']['nbytes'], fh.tell()), file=logfile)
    
    # get number of block; not including the Map block
    results['mapblock']['nblocks'] = parts.get_uint(fh, 2) - 1
    
    if debug:
        print("MAIN: %d blocks to follow; next position 0x%X" % \
                (results['mapblock']['nblocks'], fh.tell() ), file=logfile)
        print(parts.divider, file=logfile)
    
    # get block information
    if debug:
        print("MAIN: BLOCKS:", file=logfile) 
    
    results['blocks'] = dict()
    startpos = results['mapblock']['nbytes']
    
    for i in range( results['mapblock']['nblocks'] ):
        bname = parts.get_string(fh)
        bver  = "%.2f" % (parts.get_uint(fh,2) * 0.01)
        bsize = parts.get_uint(fh,4)
        
        ref = { 'name': bname, 'version': bver, 'size': bsize, 'pos': startpos, 'order': i }
        results['blocks'][bname] = ref
        
        if debug:
            print("MAIN: %s block: version %s," % (bname, bver), file=logfile)
            print("block size %d bytes," % (bsize), file=logfile)
            print("start at pos 0x%X" % startpos, file=logfile)
        
        # start position of next block
        startpos += bsize
    
    if debug:
        print(parts.divider,"\n", file=logfile)
        print("MAIN: next position 0x%X" % fh.tell(), file=logfile)
        print(parts.divider,"\n\n", file=logfile)
    
    status = 'ok'
    return status

