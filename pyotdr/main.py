import sys
import os
import logging
import argparse

from pyotdr.dump import tofile
from pyotdr.read import sorparse

# if __name__ == "__main__":
#     cdir = os.path.dirname(os.path.realpath(__file__))
#     sys.path.insert(0, cdir + "/..")

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
logger.setLevel(LOG_LEVEL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("SOR_file", type=str, help="Name of the sor file to transform")
    parser.add_argument(
        "format",
        type=str,
        default="JSON",
        help="Output format : JSON or XML",
        nargs="?",
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(message)s")
    root_logger = logging.getLogger("pyotdr")
    root_logger.setLevel(LOG_LEVEL)

    filename = args.SOR_file
    opformat = args.format

    _, results, tracedata = sorparse(filename)

    # construct data file name to dump results
    fn_strip, _ = os.path.splitext(os.path.basename(filename))
    if opformat == "JSON":
        datafile = fn_strip + "-dump.json"
    else:
        datafile = fn_strip + "-dump.xml"

    with open(datafile, "w") as output:
        tofile(results, output, format=opformat)

    # construct data file name
    fn_strip, _ = os.path.splitext(os.path.basename(filename))
    opfile = fn_strip + "-trace.dat"

    with open(opfile, "w") as output:
        for xy in tracedata:
            output.write(xy)
