import os
import logging
import argparse
from pyotdr.dump import tofile, ExportDataType
from pyotdr.read import sorparse

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logger.setLevel(LOG_LEVEL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("SOR_file", type=str, help="Name of the sor file to transform")
    parser.add_argument(
        "format",
        type=ExportDataType,
        choices=list(ExportDataType),
        default=ExportDataType.JSON,
        help="Output format : JSON or XML",
        nargs="?",
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(message)s")
    root_logger = logging.getLogger("pyotdr")
    root_logger.setLevel(LOG_LEVEL)

    filename = args.SOR_file
    opformat = ExportDataType(args.format)

    _, results, tracedata = sorparse(filename)

    # construct data file name to dump results
    fn_strip, _ = os.path.splitext(os.path.basename(filename))
    datafile = fn_strip + "-dump." + str(opformat).lower()

    with open(datafile, "w") as output:
        tofile(results, output, format=opformat)

    # construct data file name
    fn_strip, _ = os.path.splitext(os.path.basename(filename))
    opfile = fn_strip + "-trace.dat"

    with open(opfile, "w") as output:
        for xy in tracedata:
            output.write(xy)
