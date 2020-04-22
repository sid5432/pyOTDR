#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import json
from functools import reduce

import xmltodict

def replace_keys(results):
    newresults = {}
    for key in results.keys():
        newkey = reduce(lambda x,y: x.replace(y,'_'), [' ','/','(',')'], key )
        
        newresults[ newkey ] = results[key]
        if type( newresults[newkey] ) is dict:
            newresults[ newkey ] = replace_keys( newresults[ newkey ] )
    
    return newresults

def tofile(results, logfile, format='JSON'):
    """ 
    dump results to file (specifiled by file handle logfile)
    """
    
    if format == 'JSON':
        json.dump(results, logfile, sort_keys=True, indent=8, separators=(',',': '))
    elif format == 'XML':
        newresults = replace_keys(results) 
        res = xmltodict.unparse(newresults, pretty=True)
        logfile.write(res)
    else:
        raise ValueError('Format has to be JSON or XML')
