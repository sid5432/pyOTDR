#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import datetime
from . import parts

sep = "    :"
unit_map = {
            "mt": " (meters)",
            "km": " (kilometers)",
            "mi": " (miles)",
            "kf": " (kilo-ft)"
           }

tracetype = {
             'ST': "[standard trace]",
             'RT': "[reverse trace]",
             'DT': "[difference trace]",
             'RF': "[reference]",
            }

def process(fh, results, debug=False, logfile=sys.stderr):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "FxdParams"
    hsize = len(bname) + 1 # include trailing '\0'
    pname = "FxdParams.process():"
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
    
    if format == 1:
        plist = (# name, start-pos, length (bytes), type, multiplier, precision, units
                 # type: display type: 'v' (value) or 'h' (hexidecimal) or 's' (string)
                 ["date/time",0,4,'v','','',''], # ............... 0-3 seconds in Unix time
                 ["unit",4,2,'s','','',''], # .................... 4-5 distance units, 2 char (km,mt,ft,kf,mi)
                 ["wavelength",6,2,'v',0.1,1,'nm'], # ............ 6-7 wavelength (nm)
                 ["unknown 1",8,6,'h','','',''], # ............... 8-13 ???
                 ["pulse width",14,2,'v','',0,'ns'],  # .......... 14-15 pulse width (ns)
                 ["sample spacing", 16,4,'v',1e-8,'','usec'], # .. 16-19 sample spacing (in usec)
                 ["num data points", 20,4,'v','','',''], # ....... 20-23 number of data points
                 ["index", 24,4,'v',1e-5,6,''], # ................ 24-27 index of refraction
                 ["BC", 28,2,'v',-0.1,2,'dB'], # ................. 28-29 backscattering coeff
                 ["num averages", 30,4,'v','','',''], # .......... 30-33 number of averages
                 ["range", 34,4,'v',2e-5,6,'km'], # .............. 34-37 range (km)
                 ["unknown 2",38,10,'h','','',''], # ............. 38-47 ???
                 ["loss thr", 48,2,'v',0.001,3,'dB'], # .......... 48-49 loss threshold
                 ["refl thr", 50,2,'v',-0.001,3,'dB'], # ......... 50-51 reflection threshold
                 ["EOT thr",52,2,'v',0.001,3,'dB'], # ............ 52-53 end-of-transmission threshold
                )
    else:
        plist = (# name, start-pos, length (bytes), type, multiplier, precision, units
                 # type: display type: 'v' (value) or 'h' (hexidecimal) or 's' (string)
                 ["date/time",0,4,'v','','',''], # ............... 0-3 seconds in Unix time
                 ["unit",4,2,'s','','',''], # .................... 4-5 distance units, 2 char (km,mt,ft,kf,mi)
                 ["wavelength",6,2,'v',0.1,1,'nm'], # ............ 6-7 wavelength (nm)
                 ["unknown 1",8,10,'h','','',''], # .............. 8-17 ???
                 ["pulse width",18,2,'v','',0,'ns'],  # .......... 18-19 pulse width (ns)
                 ["sample spacing", 20,4,'v',1e-8,'','usec'], # .. 20-23 sample spacing (usec)
                 ["num data points", 24,4,'v','','',''], # ....... 24-27 number of data points
                 ["index", 28,4,'v',1e-5,6,''], # ................ 28-31 index of refraction
                 ["BC", 32,2,'v',-0.1,2,'dB'], # ................. 32-33 backscattering coeff
                 
                 ["num averages", 34,4,'v','','',''], # .......... 34-37 number of averages
                 
                 # from Dmitry Vaygant:
                 ["averaging time", 38,2,'v',0.1,0,'sec'], # ..... 38-39 averaging time in seconds
                 
                 ["range", 40,4,'v',2e-5,6,'km'], # .............. 40-43 range (km); note x2
                 ["unknown 2",44,14,'h','','',''], # ............. 44-57 ???
                 
                 ["loss thr", 58,2,'v',0.001,3,'dB'], # .......... 58-59 loss threshold
                 ["refl thr", 60,2,'v',-0.001,3,'dB'], # ......... 60-61 reflection threshold
                 ["EOT thr",62,2,'v',0.001,3,'dB'], # ............ 62-63 end-of-transmission threshold
                 ["trace type",64,2,'s','','',''], # ............. 64-65 trace type (ST,RT,DT, or RF)
                 ["unknown 3",66,16,'h','','',''], # ............. 66-81 ???
                )
    
    status= _process_fields(fh, plist, results, debug=debug, logfile=logfile)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

# ================================================================
def _process_fields(fh, plist, results, debug=False, logfile=sys.stderr):
    bname = "FxdParams"
    xref  = results[bname]
    
    # functions to use
    # 'h': get_hexstring
    # 'v': get_uint
    # 's': get_string
    #
    count = 0
    for field in plist:
        name  = field[0]
        fsize = field[2]
        ftype = field[3]
        scale = field[4]
        dgt   = field[5]
        unit  = field[6]
        xstr  = ""
        
        if ftype == 'v':
            val = parts.get_uint(fh, fsize)
            if scale != '':
                val *= scale
            if dgt != '':
                fmt = "%%.%df" % dgt
                xstr = fmt % val
            else:
                xstr = val
            
        elif ftype == 'h':
            xstr = parts.get_hex(fh, fsize)
        elif ftype == 's':
            xstr = fh.read( fsize ).decode('utf-8')
        else:
            val = fh.read(fsize)
            xstr = val

        # .................................
        if name == 'date/time':
            # xstr = str(datetime.datetime.fromtimestamp(val))+(" (%d sec)" % val)
            xstr = datetime.datetime.fromtimestamp(val).strftime("%a %b %d %H:%M:%S %Y") + \
            (" (%d sec)" % val)
        elif name == 'unit':
            xstr += unit_map[ xstr ]
        elif name == 'trace type':
            try:
                xstr += tracetype[ xstr ]
            except:
                pass
            
        # .................................
        if debug:
            print("%s %d. %s: %s %s" % (sep, count, name, xstr, unit), file=logfile)
        
        xref[name] = xstr if unit=="" else str(xstr)+" "+unit
        count += 1
    
    # corrrections/adjustment:
    ior = float(xref['index'])
    ss = xref['sample spacing'].split(' ')[0]
    dx  = float( ss ) * parts.sol / ior
    xref['range'] = dx * int(xref['num data points'])
    xref['resolution'] = dx * 1000.0 # in meters
    if debug:
        print("", file=logfile)
        print("%s [adjusted for refractive index]" % (sep), file=logfile)
        print("%s resolution = %.14f m" % (sep,xref['resolution']), file=logfile)
        print("%s range      = %.13f km" % (sep,xref['range']), file=logfile)

    status = 'ok'
    
    return status
