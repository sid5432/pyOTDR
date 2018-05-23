#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import logging
from . import parts

logger = logging.getLogger('pyOTDR')

sep = "    :"

def process(fh, results): 
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "GenParams"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = "genparam.process():"
    ref = None
    status = 'nok'
    
    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek( startpos )
    except:
        logger.error('{} {} block starting position unknown'.format(pname, bname))
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname+'\0':
            logger.error('{} incorrect header {} vs "{}"'.format(pname,mystr,bname))
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    if format == 1:
        status = process1(fh, results) 
    else:
        status= process2(fh, results)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    
    return status

# ================================================================
def build_condition(bcstr):
    """decode build condition"""
    if bcstr == 'BC':
        bcstr += " (as-built)"
    elif bcstr == 'CC':
        bcstr+= " (as-current)"
    elif bcstr == 'RC':
        bcstr+= " (as-repaired)"
    elif bcstr == 'OT':
        bcstr+= " (other)"
    else:
        bcstr+= " (unknown)"
    
    return bcstr

# ================================================================
def fiber_type(val):
    """ 
    decode fiber type 
    REF: http://www.ciscopress.com/articles/article.asp?p=170740&seqNum=7
    """
    if val == 651: # ITU-T G.651
        fstr = "G.651 (50um core multimode)"
    elif val == 652: # standard nondispersion-shifted 
        fstr = "G.652 (standard SMF)"
        # G.652.C low Water Peak Nondispersion-Shifted Fiber            
    elif val == 653:
        fstr = "G.653 (dispersion-shifted fiber)"
    elif val == 654:
        fstr = "G.654 (1550nm loss-minimzed fiber)"
    elif val == 655:
        fstr = "G.655 (nonzero dispersion-shifted fiber)"
    else: # TODO add G657
        fstr = "%d (unknown)" % val
    
    return fstr

# ================================================================
def process1(fh, results):
    """ process version 1 format """
    bname = "GenParams"
    xref  = results[bname]
    
    lang = fh.read(2).decode('ascii')
    xref['language'] = lang
    logger.debug("{} language '{}', next pos {}".format(sep, lang, fh.tell()))
    
    fields = (
              "cable ID",    # ........... 0
              "fiber ID",    # ........... 1
              "wavelength",  # ............2: fixed 2 bytes value
              
              "location A", # ............ 3
              "location B", # ............ 4
              "cable code/fiber type", # ............ 5
              "build condition", # ....... 6: fixed 2 bytes char/string
              "user offset", # ........... 7: fixed 4 bytes (Andrew Jones)
              "operator",    # ........... 8
              "comments",    # ........... 9
             )
    
    count = 0
    for field in fields:
        if field == 'build condition':
            xstr = build_condition( fh.read(2).decode('ascii') )
        elif field == 'wavelength':
            val = parts.get_uint(fh, 2)
            xstr = "%d nm" % val
        elif field == "user offset":
            val = parts.get_signed(fh, 4)
            xstr = "%d" % val
        else:
            xstr = parts.get_string(fh)
        
        logger.debug("{}  {}. {}: {}".format(sep, count, field, xstr))
        
        xref[field] = xstr
        count += 1
        
    status = 'ok'
    
    return status

# ================================================================
def process2(fh, results):
    """ process version 2 format """
    bname = "GenParams"
    xref  = results[bname]
    
    lang = fh.read(2).decode('ascii')
    xref['language'] = lang
    logger.debug("{}  language: '{}', next pos {}".format(sep, lang, fh.tell()))
    
    fields = (
              "cable ID",    # ........... 0
              "fiber ID",    # ........... 1
              
              "fiber type",  # ........... 2: fixed 2 bytes value
              "wavelength",  # ............3: fixed 2 bytes value
              
              "location A", # ............ 4
              "location B", # ............ 5
              "cable code/fiber type", # ............ 6
              "build condition", # ....... 7: fixed 2 bytes char/string
              "user offset", # ........... 8: fixed 4 bytes int (Andrew Jones)
              "user offset distance", # .. 9: fixed 4 bytes int (Andrew Jones)
              "operator",    # ........... 10
              "comments",    # ........... 11
             )
    
    count = 0
    for field in fields:
        if field == 'build condition':
            xstr = build_condition( fh.read(2).decode('ascii') )
        elif field == 'fiber type':
            val = parts.get_uint(fh, 2)
            xstr = fiber_type( val )
        elif field == 'wavelength':
            val = parts.get_uint(fh, 2)
            xstr = "%d nm" % val
        elif field == "user offset" or field == "user offset distance":
            val = parts.get_signed(fh, 4)
            xstr = "%d" % val
        else:
            xstr = parts.get_string(fh)
        
        logger.debug("{} {}. {}: {}".format(sep, count, field, xstr))
        
        xref[field] = xstr
        count += 1
    
    status = 'ok'
    
    return status
