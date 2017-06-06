#!/usr/bin/python
import sys
import json
import parts

def tofile(results, logfile):
    """ 
    dump results to file (specifiled by file handle logfile)
    """
    
    print >>logfile, json.dumps(results, sort_keys=True, indent=8, separators=(',',': '))
    
    return
