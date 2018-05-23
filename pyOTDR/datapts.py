#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys

from . import parts

sep = "    :"

logger = logging.getLogger('pyOTDR')


def process(fh, results, tracedata):
    """
    fh: file handle;
    results: dict for results;
    
    we assume mapblock.process() has already been run
    """
    bname = "DataPts"
    hsize = len(bname) + 1  # include trailing '\0'
    pname = "DataPts.process():"
    ref = None
    status = 'nok'

    try:
        ref = results['blocks'][bname]
        startpos = ref['pos']
        fh.seek(startpos)
    except:
        logger.error('{} {} block starting position unknown'.format(pname, bname))
        return status

    format = results['format']

    if format == 2:
        mystr = fh.read(hsize).decode('ascii')
        if mystr != bname + '\0':
            logger.error('{}  incorrect header {}'.format(pname, mystr))
            return status

    results[bname] = dict()
    xref = results[bname]

    # extra parameters
    xref['_datapts_params'] = {'xscaling': 1, 'offset': 'STV'}
    # method used by STV: minimum reading shifted to zero
    # method used by AFL/Noyes Trace.Net: maximum reading shifted to zero (approx)

    status = _process_data(fh, results, tracedata)

    # read the rest of the block (just in case)
    endpos = results['blocks'][bname]['pos'] + results['blocks'][bname]['size']
    fh.read(endpos - fh.tell())
    status = 'ok'
    return status


# ================================================================
def _process_data(fh, results, tracedata, dumptrace=True):
    """ process version 1 format """
    bname = "DataPts"
    xref = results[bname]

    try:
        # we assume SupParams block already processed
        model = results['SupParams']['OTDR']
    except:
        model = ""

    # special case:
    # old Noyes/AFL OFL250 model is off by factor of 10
    if model == 'OFL250':
        xref['_datapts_params']['xscaling'] = 0.1

    logger.debug("{} [initial 12 byte header follows]".format(sep))

    N = parts.get_uint(fh, 4)
    # confirm N equal to FxdParams num data points
    if N != results['FxdParams']['num data points']:
        logger.warning(
            "block says number of data points is {} instead of {}".format(N, results['FxdParams']['num data points']))

    xref['num data points'] = N
    logger.debug("{} num data points = {}".format(sep, N))

    val = parts.get_signed(fh, 2)
    xref['num traces'] = val
    logger.debug('{} number of traces = {}'.format(sep, val))

    if val > 1:
        logger.warning("Cannot handle multiple traces ({}); aborting".format(val))
        sys.exit()

    val = parts.get_uint(fh, 4)
    xref['num data points 2'] = val
    logger.debug("{} num data points again = {}".format(sep, val))

    val = parts.get_uint(fh, 2)
    scaling_factor = val / 1000.0
    xref['scaling factor'] = scaling_factor
    logger.debug("{} scaling factor = {}".format(sep, scaling_factor))

    # .....................................
    # adjusted resolution
    dx = results['FxdParams']['resolution']
    dlist = []
    for i in range(N):
        val = parts.get_uint(fh, 2)
        dlist.append(val)

    ymax = max(dlist)
    ymin = min(dlist)
    fs = 0.001 * scaling_factor
    disp_min = "%.3f" % (ymin * fs)
    disp_max = "%.3f" % (ymax * fs)
    xref['max before offset'] = float(disp_max)
    xref['min before offset'] = float(disp_min)
    
    logger.debug("{} before applying offset: max {} dB, min {} dB".format(sep, disp_max, disp_min))

    # .........................................
    # save to file
    offset = xref['_datapts_params']['offset']
    xscaling = xref['_datapts_params']['xscaling']

    # convert/scale to dB
    if offset == 'STV':
        nlist = [(ymax - x) * fs for x in dlist]
    elif offset == 'AFL':
        nlist = [(ymin - x) * fs for x in dlist]
    else:  # invert
        nlist = [-x * fs for x in dlist]

    for i in range(N):
        # more work but (maybe) less rounding issues
        x = dx * i * xscaling / 1000.0  # output in km
        tracedata.append("{:f}\t{:f}\n".format(x, nlist[i]))
        
    # .........................................
    status = 'ok'

    return status
