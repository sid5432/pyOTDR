import os
import logging
from pathlib import Path

from pyotdr.dump import tofile, ExportDataType
from pyotdr.read import sorparse

import click

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logger.setLevel(LOG_LEVEL)


class PathType(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""

    def convert(self, value, param, ctx):
        return Path(super().convert(value, param, ctx))


@click.command()
@click.argument("sor_file", type=PathType(exists=True, dir_okay=False, readable=True))
@click.argument(
    "file_format",
    type=click.Choice([str(x) for x in ExportDataType.__members__]),
    default=str(ExportDataType.JSON),
)
def main(sor_file: str, file_format: ExportDataType) -> None:
    # parser = argparse.ArgumentParser()
    # parser.add_argument("SOR_file", type=str, help="Name of the sor file to transform")
    # parser.add_argument(
    #     "format",
    #     type=ExportDataType,
    #     choices=list(ExportDataType),
    #     default=ExportDataType.JSON,
    #     help="Output format : JSON or XML",
    #     nargs="?",
    # )
    # args = parser.parse_args()

    logging.basicConfig(format="%(message)s")
    root_logger = logging.getLogger("pyotdr")
    root_logger.setLevel(LOG_LEVEL)

    filename = Path(sor_file)
    opformat = ExportDataType(file_format)

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
