#!/usr/bin/python
import sys
import re
import parts

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
    print >>logfile, "%s %d events" % (sep, nev)
    xref['num events'] = nev
    
    factor = 1e-4 * parts.sol / float(results['FxdParams']['index'])
    
    pat = re.compile("(.)(.)9999LS")
    
    for j in xrange(nev):
        xid  = parts.get_uint(fh, 2)             # 00-01: event number
        dist = parts.get_uint(fh, 4) * factor    # 02-05: time-of-travel; need to convert to distance
        
        slope  = parts.get_signed(fh, 2) * 0.001 # 06-07: slope
        splice = parts.get_signed(fh, 2) * 0.001 # 08-09: splice loss
        refl   = parts.get_signed(fh, 4) * 0.001 # 10-13: reflection loss
        
        xtype = fh.read(8)                       # 14-21: event type
        
        mresults = pat.match(xtype)
        if mresults != None:
            subtype = mresults.groups(0)[0]
            manual  = mresults.groups(0)[1]
            # print "..........debug ",mresults.group(), mresults.groups(0)[0], mresults.groups(0)[1]
            
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
        
        if debug:
            print >>logfile,"%s Event %d: type %s" % (sep,xid, xtype)
            print >>logfile,"%s%s distance: %.3f km" % (sep,sep,dist)
            print >>logfile,"%s%s slope: %.3f dB/km" % (sep,sep,slope)
            print >>logfile,"%s%s splice loss: %.3f dB" % (sep,sep,splice)
            print >>logfile,"%s%s refl loss: %.3f dB" % (sep,sep,refl)
            # version 2
            if format == 2:
                print >>logfile,"%s%s end of previous event: %.3f km" % (sep,sep,end_prev)
                print >>logfile,"%s%s start of current event: %.3f km" % (sep,sep,start_curr)
                print >>logfile,"%s%s end of current event: %.3f km" % (sep,sep,end_curr)
                print >>logfile,"%s%s start of next event: %.3f km" % (sep,sep,start_next)
                print >>logfile,"%s%s peak point of event: %.3f km" % (sep,sep,pkpos)
            
            # common
            print >>logfile,"%s%s comments: %s" % (sep,sep,comments)
    
    # ...................................................
    total      = parts.get_signed(fh, 4) * 0.001  # 00-03: total loss
    loss_start = parts.get_signed(fh, 4) * factor # 04-07: loss start position
    loss_finish= parts.get_uint(fh, 4) * factor   # 08-11: loss finish position
    orl        = parts.get_uint(fh, 2) * 0.001    # 12-13: optical return loss (ORL)
    orl_start  = parts.get_signed(fh, 4) * factor # 14-17: ORL start position
    orl_finish = parts.get_uint(fh, 4) * factor   # 18-21: ORL finish position
    if debug:
        print >>logfile,"%s Summary:" % sep
        print >>logfile,"%s%s total loss: %.3f dB" % (sep,sep,total)
        print >>logfile,"%s%s ORL: %.3f dB" % (sep,sep,orl)
        print >>logfile,"%s%s loss start: %f km" % (sep,sep,loss_start)
        print >>logfile,"%s%s loss end: %f km" % (sep,sep,loss_finish)
        print >>logfile,"%s%s ORL start: %f km" % (sep,sep,orl_start)
        print >>logfile,"%s%s ORL finish: %f km" % (sep,sep,orl_finish)
    
    # ................
    status = 'ok'
    return status

