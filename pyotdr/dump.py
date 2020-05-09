import json
from functools import reduce
from dicttoxml import dicttoxml


def replace_keys(results):
    newresults = {}
    for key in results.keys():
        newkey = reduce(lambda x, y: x.replace(y, "_"), [" ", "/", "(", ")"], key)

        newresults[newkey] = results[key]
        if type(newresults[newkey]) is dict:
            newresults[newkey] = replace_keys(newresults[newkey])

    return newresults


def tofile(results, logfile, format="JSON"):
    """ 
    dump results to file (specifiled by file handle logfile)
    """

    if format == "JSON":
        json.dump(results, logfile, sort_keys=True, indent=8, separators=(",", ": "))
    elif format == "XML":
        newresults = replace_keys(results)
        logfile.write(
            dicttoxml(newresults, custom_root="sor", attr_type=False).decode("utf-8")
        )

        # lazyxml.dump(newresults, logfile, indent=' '*4, cdata=False, root='sor')
    else:
        raise ValueError("Format has to be JSON or XML")
        # sanity check; should run without problems
        # lazyxml.loads(xmlstring)
