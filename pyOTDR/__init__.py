"""
USAGE: pyOTDR SOR_file [format]
     : format: JSON (default) or XML
     
For using pyOTDR in a module, see the code in pyOTDR/main.py.  The two main functions are:

* sorparse(): to parse the SOR file
* tofile(): to dump the results into a JSON file

"""

from .read import sorparse
from .dump import tofile
from .main import main

__version__ = "1.0.0.c1"

