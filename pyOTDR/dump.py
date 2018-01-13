#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import json
import lazyxml
from . import parts

def replace_keys(results):
    
    newresults = {}
    for key in results.keys():
        newkey = reduce( lambda x,y: x.replace(y,'_'), [' ','/','(',')'], key )
        
        newresults[ newkey ] = results[key]
        if type( newresults[newkey] ) is dict:
            newresults[ newkey ] = replace_keys( newresults[ newkey ] )
    
    return newresults

def tofile(results, logfile, format='JSON'):
    """ 
    dump results to file (specifiled by file handle logfile)
    """
    
    if format == 'JSON':
        print(json.dumps(results, sort_keys=True, indent=8, separators=(',',': ')), file=logfile)
    else:
        newresults = replace_keys(results)
        xmlstring = lazyxml.dumps(newresults, indent=' '*4, cdata=False, root='sor')
        print(xmlstring, file=logfile)
        
        # sanity check; should run without problems
        # lazyxml.loads(xmlstring)
    
    return
