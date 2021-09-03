"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.txt")) as f:
    # deps are specified in requirements.txt. Avoid empty line.
    requirements = [x for x in f.read().split("\n") if x]

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="pyotdr",
    version="2.1.0",
    description="A simple OTDR SOR file parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sid5432/pyOTDR",
    author="Sidney Li, Rémi Desgrange",
    author_email="sidneyli5432@gmail.com, remi+pyotdr@desgran.ge",
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Utilities",
        # Pick your license as you wish
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="SR-4731 reflectometer Telcordia OTDR SOR ",
    packages=find_packages(),
    install_requires=requirements,
)
