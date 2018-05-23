#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import datetime
import logging
from . import parts

logger = logging.getLogger('pyOTDR')

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

def process(fh, results):
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
        logger.error('{} {} block starting position unknown'.format(pname, bname))
        return status
    
    format = results['format']
    
    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname+'\0':
            logger.error('{}  incorrect header {}'.format(pname, mystr))
            return status
    
    results[bname] = dict()
    xref = results[bname]
    
    if format == 1:
        plist = (# name, start-pos, length (bytes), type, multiplier, precision, units
                 # type: display type: 'v' (value) or 'h' (hexidecimal) or 's' (string)
                 ["date/time",0,4,'v','','',''], # ............... 0-3 seconds in Unix time
                 ["unit",4,2,'s','','',''], # .................... 4-5 distance units, 2 char (km,mt,ft,kf,mi)
                 ["wavelength",6,2,'v',0.1,1,'nm'], # ............ 6-7 wavelength (nm)
                 
                 # from Andrew Jones
                 ["acquisition offset",8,4,'i','','',''], # .............. 8-11 acquisition offset; units?
                 ["number of pulse width entries",12,2,'v','','',''], # .. 12-13 number of pulse width entries
                 
                 ["pulse width",14,2,'v','',0,'ns'],  # .......... 14-15 pulse width (ns)
                 ["sample spacing", 16,4,'v',1e-8,'','usec'], # .. 16-19 sample spacing (in usec)
                 ["num data points", 20,4,'v','','',''], # ....... 20-23 number of data points
                 ["index", 24,4,'v',1e-5,6,''], # ................ 24-27 index of refraction
                 ["BC", 28,2,'v',-0.1,2,'dB'], # ................. 28-29 backscattering coeff
                 ["num averages", 30,4,'v','','',''], # .......... 30-33 number of averages
                 ["range", 34,4,'v',2e-5,6,'km'], # .............. 34-37 range (km)
                 
                 # from Andrew Jones
                 ["front panel offset",38,4,'i','','',''], # ................ 38-41
                 ["noise floor level",42,2,'v','','',''], # ................. 42-43 unsigned
                 ["noise floor scaling factor",44,2,'i','','',''], # ........ 44-45
                 ["power offset first point",46,2,'v','','',''], # .......... 46-47 unsigned
                 
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
                 
                 # from Andrew Jones
                 ["acquisition offset",8,4,'i','','',''], # .............. 8-11 acquisition offset; units?
                 ["acquisition offset distance",12,4,'i','','',''], # .... 12-15 acquisition offset distance; units?
                 ["number of pulse width entries",16,2,'v','','',''], # .. 16-17 number of pulse width entries
                                  
                 ["pulse width",18,2,'v','',0,'ns'],  # .......... 18-19 pulse width (ns)
                 ["sample spacing", 20,4,'v',1e-8,'','usec'], # .. 20-23 sample spacing (usec)
                 ["num data points", 24,4,'v','','',''], # ....... 24-27 number of data points
                 ["index", 28,4,'v',1e-5,6,''], # ................ 28-31 index of refraction
                 ["BC", 32,2,'v',-0.1,2,'dB'], # ................. 32-33 backscattering coeff
                 
                 ["num averages", 34,4,'v','','',''], # .......... 34-37 number of averages
                 
                 # from Dmitry Vaygant:
                 ["averaging time", 38,2,'v',0.1,0,'sec'], # ..... 38-39 averaging time in seconds
                 
                 ["range", 40,4,'v',2e-5,6,'km'], # .............. 40-43 range (km); note x2
                 
                 # from Andrew Jones
                 ["acquisition range distance",44,4,'i','','',''], # ........ 44-47
                 ["front panel offset",48,4,'i','','',''], # ................ 48-51
                 ["noise floor level",52,2,'v','','',''], # ................. 52-53 unsigned
                 ["noise floor scaling factor",54,2,'i','','',''], # ........ 54-55
                 ["power offset first point",56,2,'v','','',''], # .......... 56-57 unsigned
                 
                 ["loss thr", 58,2,'v',0.001,3,'dB'], # .......... 58-59 loss threshold
                 ["refl thr", 60,2,'v',-0.001,3,'dB'], # ......... 60-61 reflection threshold
                 ["EOT thr",62,2,'v',0.001,3,'dB'], # ............ 62-63 end-of-transmission threshold
                 ["trace type",64,2,'s','','',''], # ............. 64-65 trace type (ST,RT,DT, or RF)
                 
                 # from Andrew Jones
                 ["X1",66,4,'i','','',''], # ............. 66-69
                 ["Y1",70,4,'i','','',''], # ............. 70-73
                 ["X2",74,4,'i','','',''], # ............. 74-77
                 ["Y2",78,4,'i','','',''], # ............. 78-81
                )
    
    status = _process_fields(fh, plist, results)
    
    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read( endpos - fh.tell() )
    status = 'ok'
    return status

# ================================================================
def _process_fields(fh, plist, results):
    bname = "FxdParams"
    xref  = results[bname]
    
    # functions to use
    # 'h': get_hexstring
    # 'v': get_uint
    # 's': get_string
    # 'i': get_signed
    count = 0
    for field in plist:
        name  = field[0]
        fsize = field[2]
        ftype = field[3]
        scale = field[4]
        dgt   = field[5]
        unit  = field[6]
        xstr  = ""
        
        if ftype == 'i':
            val = parts.get_signed(fh, fsize)
            xstr = val
        elif ftype == 'v':
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
        
        # don't bother even trying if there are multiple pulse width entries; too lazy
        # to restructure code to handle this case
        if name == 'number of pulse width entries' and val > 1:
            logger.warning('Cannot handle multiple pulse width entries ({}); aborting'.format(val))
            # TODO should raise an exception instead of brutaly exit
            sys.exit()
                    
        # .................................
        logger.debug("%s %d. %s: %s %s" % (sep, count, name, xstr, unit)) 
        
        xref[name] = xstr if unit=="" else str(xstr)+" "+unit
        count += 1
    
    # corrrections/adjustment:
    ior = float(xref['index'])
    ss = xref['sample spacing'].split(' ')[0]
    dx  = float( ss ) * parts.sol / ior
    xref['range'] = dx * int(xref['num data points'])
    xref['resolution'] = dx * 1000.0 # in meters

    logger.debug("%s [adjusted for refractive index]" % (sep)) 
    logger.debug("%s resolution = %.14f m" % (sep,xref['resolution']))
    logger.debug("%s range      = %.13f km" % (sep,xref['range']))

    status = 'ok'
    
    return status
