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
    
    if format == 1:
        status = process1(fh, results, debug=debug, logfile=logfile)
    else:
        status= process2(fh, results, debug=debug, logfile=logfile)
    
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
    else:
        fstr = "%d (unknown)" % val
    
    return fstr

# ================================================================
def process1(fh, results, debug=False, logfile=sys.stderr):
    """ process version 1 format """
    bname = "GenParams"
    xref  = results[bname]
    
    lang = fh.read(2)
    xref['language'] = lang
    if debug:
        print >>logfile, "%s  language: '%s', next pos %d" % (sep, lang, fh.tell())
    
    fields = (
              "cable ID",    # ........... 0
              "fiber ID",    # ........... 1
              "wavelength",  # ............2: fixed 2 bytes value
              
              "location A", # ............ 3
              "location B", # ............ 4
              "cable code/fiber type", # ............ 5
              "build condition", # ....... 6: fixed 2 bytes char/string
              "(unknown 2)", # ........... 7: fixed 4 bytes
              "operator",    # ........... 8
              "comments",    # ........... 9
             )
    
    count = 0
    for field in fields:
        if field == 'build condition':
            xstr = build_condition( fh.read(2) )
        elif field == 'wavelength':
            val = parts.get_uint(fh, 2)
            xstr = "%d nm" % val
        elif field == "(unknown 2)":
            val = parts.get_uint(fh, 4)
            xstr = "VALUE %d" % val
        else:
            xstr = parts.get_string(fh)
        
        if debug:
            print >>logfile, "%s %d. %s: %s" % (sep, count, field, xstr)
        
        xref[field] = xstr
        count += 1
        
    status = 'ok'
    
    return status

# ================================================================
def process2(fh, results, debug=False, logfile=sys.stderr):
    """ process version 2 format """
    bname = "GenParams"
    xref  = results[bname]
    
    lang = fh.read(2)
    xref['language'] = lang
    if debug:
        print >>logfile, "%s  language: '%s', next pos %d" % (sep, lang, fh.tell())
    
    fields = (
              "cable ID",    # ........... 0
              "fiber ID",    # ........... 1
              
              "fiber type",  # ........... 2: fixed 2 bytes value
              "wavelength",  # ............3: fixed 2 bytes value
              
              "location A", # ............ 4
              "location B", # ............ 5
              "cable code/fiber type", # ............ 6
              "build condition", # ....... 7: fixed 2 bytes char/string
              "(unknown 2)", # ........... 8: fixed 8 bytes
              "operator",    # ........... 9
              "comments",    # ........... 10
             )
    
    count = 0
    for field in fields:
        if field == 'build condition':
            xstr = build_condition( fh.read(2) )
        elif field == 'fiber type':
            val = parts.get_uint(fh, 2)
            xstr = fiber_type( val )
        elif field == 'wavelength':
            val = parts.get_uint(fh, 2)
            xstr = "%d nm" % val
        elif field == "(unknown 2)":
            val = parts.get_uint(fh, 8)
            xstr = "VALUE %ld" % (val)
        else:
            xstr = parts.get_string(fh)
        
        if debug:
            print >>logfile, "%s %d. %s: %s" % (sep, count, field, xstr)
        
        xref[field] = xstr
        count += 1
    
    status = 'ok'
    
    return status
