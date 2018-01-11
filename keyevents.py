#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import re
from . import parts

sep = "    :"

def process(fh, results, debug=False, logfile=sys.stderr):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "KeyEvents"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = bname+".process():"
    ref = None
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
            print(pname," incorrect header ",mystr, file=logfile)
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    status = _process_keyevents(fh, format, results, debug=debug, logfile=logfile)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

# ================================================================
def _process_keyevents(fh, format, results, debug=False, logfile=sys.stderr):
    """ process version 1 or 2 format """
    bname = "KeyEvents"
    xref  = results[bname]
    
    # number of events
    nev = parts.get_uint(fh, 2)
    if debug:
        print("%s %d events" % (sep, nev), file=logfile)
    
    xref['num events'] = nev
    
    factor = 1e-4 * parts.sol / float(results['FxdParams']['index'])
    
    pat = re.compile("(.)(.)9999LS")
    
    for j in range(nev):
        x2ref = xref['event %d' % (1+j)] = {};
        
        xid  = parts.get_uint(fh, 2)             # 00-01: event number
        dist = parts.get_uint(fh, 4) * factor    # 02-05: time-of-travel; need to convert to distance
        
        slope  = parts.get_signed(fh, 2) * 0.001 # 06-07: slope
        splice = parts.get_signed(fh, 2) * 0.001 # 08-09: splice loss
        refl   = parts.get_signed(fh, 4) * 0.001 # 10-13: reflection loss
        
        xtype = fh.read(8)                       # 14-21: event type
        xtype = xtype.decode('ascii')
        
        mresults = pat.match( xtype )
        if mresults != None:
            subtype = mresults.groups(0)[0]
            manual  = mresults.groups(0)[1]
            
            if manual == 'A':
                xtype += " {manual}"
            else:
                xtype += " {auto}"
            
            if subtype == '1':
                xtype += " reflection"
            elif subtype == '0':
                xtype += " loss/drop/gain"
            elif subtype == '2':
                xtype += " multiple"
            else:
                xtype += " unknown '"+subtype+"'"
        else:
            xtype += " [unknown type "+xtype+"]"
        
        if format == 2:
            end_prev   = parts.get_uint(fh, 4) * factor    # 22-25: end of previous event
            start_curr = parts.get_uint(fh, 4) * factor    # 26-29: start of current event
            end_curr   = parts.get_uint(fh, 4) * factor    # 30-33: end of current event
            start_next = parts.get_uint(fh, 4) * factor    # 34-37: start of next event
            pkpos      = parts.get_uint(fh, 4) * factor    # 38-41: peak point of event
            
        comments = parts.get_string(fh)
        
        x2ref['type'] = xtype
        x2ref['distance'] = ("%.3f" % dist)
        x2ref['slope'] = ("%.3f" % slope)
        x2ref['splice loss'] = ("%.3f" % splice)
        x2ref['refl loss'] = ("%.3f" % refl)
        x2ref['comments'] = comments
        
        if format == 2:
            x2ref['end of prev'] = ("%.3f" % end_prev)
            x2ref['start of curr'] = ("%.3f" % start_curr)
            x2ref['end of curr'] = ("%.3f" % end_curr)
            x2ref['start of next'] = ("%.3f" % start_next)
            x2ref['peak'] = ("%.3f" % pkpos)
        
        
        if debug:
            print("%s Event %d: type %s" % (sep,xid, xtype), file=logfile)
            print("%s%s distance: %.3f km" % (sep,sep,dist),file=logfile)
            print("%s%s slope: %.3f dB/km" % (sep,sep,slope),file=logfile)
            print("%s%s splice loss: %.3f dB" % (sep,sep,splice),file=logfile)
            print("%s%s refl loss: %.3f dB" % (sep,sep,refl),file=logfile)
            # version 2
            if format == 2:
                print("%s%s end of previous event: %.3f km" % (sep,sep,end_prev), file=logfile)
                print("%s%s start of current event: %.3f km" % (sep,sep,start_curr), file=logfile)
                print("%s%s end of current event: %.3f km" % (sep,sep,end_curr), file=logfile)
                print("%s%s start of next event: %.3f km" % (sep,sep,start_next), file=logfile)
                print("%s%s peak point of event: %.3f km" % (sep,sep,pkpos), file=logfile)
            
            # common
            print("%s%s comments: %s" % (sep,sep,comments), file=logfile)
    
    # ...................................................
    total      = parts.get_signed(fh, 4) * 0.001  # 00-03: total loss
    loss_start = parts.get_signed(fh, 4) * factor # 04-07: loss start position
    loss_finish= parts.get_uint(fh, 4) * factor   # 08-11: loss finish position
    orl        = parts.get_uint(fh, 2) * 0.001    # 12-13: optical return loss (ORL)
    orl_start  = parts.get_signed(fh, 4) * factor # 14-17: ORL start position
    orl_finish = parts.get_uint(fh, 4) * factor   # 18-21: ORL finish position
    if debug:
        print("%s Summary:" % sep, file=logfile)
        print("%s%s total loss: %.3f dB" % (sep,sep,total), file=logfile)
        print("%s%s ORL: %.3f dB" % (sep,sep,orl), file=logfile)
        print("%s%s loss start: %f km" % (sep,sep,loss_start), file=logfile)
        print("%s%s loss end: %f km" % (sep,sep,loss_finish), file=logfile)
        print("%s%s ORL start: %f km" % (sep,sep,orl_start), file=logfile)
        print("%s%s ORL finish: %f km" % (sep,sep,orl_finish), file=logfile)
    
    x3ref = xref["Summary"] = {}
    x3ref["total loss"] = float( "%.3f" % total)
    x3ref["ORL"]        = float( "%.3f" % orl )
    x3ref["loss start"] = float( "%.6f" % loss_start )
    x3ref["loss end"]   = float( "%.6f" % loss_finish )
    x3ref["ORL start"]  = float( "%.6f" % orl_start )
    x3ref["ORL finish"] = float( "%.6f" % orl_finish )
    
    # ................
    status = 'ok'
    return status

