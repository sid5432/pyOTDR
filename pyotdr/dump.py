import json
from enum import Enum
from functools import reduce
from dicttoxml import dicttoxml


class ExportDataType(Enum):
    JSON = "JSON"
    XML = "XML"

    def __str__(self) -> str:
        return self.value


def replace_keys(results):
    newresults = {}
    for key in results.keys():
        newkey = reduce(lambda x, y: x.replace(y, "_"), [" ", "/", "(", ")"], key)

        newresults[newkey] = results[key]
        if type(newresults[newkey]) is dict:
            newresults[newkey] = replace_keys(newresults[newkey])

    return newresults


def tofile(results, logfile, format: ExportDataType = ExportDataType.JSON):
    """
    dump results to file (specifiled by file handle logfile)
    """

    if format == ExportDataType.JSON:
        json.dump(results, logfile, sort_keys=True, indent=8, separators=(",", ": "))
    elif format == ExportDataType.XML:
        newresults = replace_keys(results)
        logfile.write(
            dicttoxml(newresults, custom_root="sor", attr_type=False).decode("utf-8")
        )
    else:
        raise ValueError("Format has to be JSON or XML")
