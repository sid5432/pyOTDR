# pyOTDR: Simple OTDR SOR file parse written in Python

The SOR ("Standard OTDR Record") data format is used to store OTDR 
([optical time-domain
reflectometer](http://https://en.wikipedia.org/wiki/Optical_time-domain_reflectometer)
) fiber data.  The format is defined by the Telcordia [SR-4731, issue
2](http://telecom-info.telcordia.com/site-cgi/ido/docs.cgi?ID=SEARCH&DOCUMENT=SR-4731&)
standard.  While it is a standard, it is unfortunately not open, in
that the specifics of the data format are not openly available.  You
can buy the standards document from Telcordia for $750 US (as of this
writing), but this was beyond my budget. (And likely comes with
all sorts of licensing restrictions. I wouldn't know; I have never
seen the document!)


There are several freely available OTDR trace readers available for
download on the web, but most do not allow exporting the trace curve
into, say, a CSV file for further analysis, and only one that I've
found that runs natively on Linux (but without source code; although
some of these do work in the Wine emulator).  There have been requests
on various Internet forums asking for information on how to extract
the trace data, but I am not aware of anyone providing any answers
beyond pointing to the free readers and the Telcordia standard.


Fortunately the data format is not particularly hard to decipher.  The
table of contents on the Telcordia [SR-4731, issue
2](http://telecom-info.telcordia.com/site-cgi/ido/docs.cgi?ID=SEARCH&DOCUMENT=SR-4731&)
page provides several clues, as does the Wikipedia page on [optical
time-domain
reflectometer](http://https://en.wikipedia.org/wiki/Optical_time-domain_reflectometer).


Using a binary-file editor/viewer and comparing the outputs from
some free OTDR SOR file readers, I was able to piece together most of
the encoding in the SOR data format and written a simple program (in
Python) that parses the SOR file and dumps the trace data into a file.
(For a more detailed description, other than reading the source code,
see [my blog
post](http://morethanfootnotes.blogspot.com/2015/07/the-otdr-optical-time-domain.html?view=sidebar)).


Presented here for your entertainment are my findings, in the hope
that it will be useful to other people.  But be aware that the
information provided here is based on guess work from looking at a
limited number of sample files.  I can not guarantee that there are no
mistakes, or that I have uncovered all possible exceptions to the
rules that I have deduced from the sample files.  **use it at your own
risk! You have been warned!** 

The program was ported over from my original [pubOTDR](https://github.com/sid5432/pubOTDR)
written in Perl.  To parse an OTDR SOR file, run the program as

<code>% pyOTDR.py myfile.sor</code>

where "mfile.sor" is the name (path) to your SOR file.  A OTDR trace file "myfile-trace.dat" and a JSON file "myfile-dump.json" will be produced.  You can also output the results as an XML file "myfile-dump.xml" with:

<code>% pyOTDR.py myfile.sor XML</code>

There is also a Clojure version, [cljotdr](https://github.com/sid5432/cljotdr); this will be of interest to people looking for a Java version, since Clojure runs on top of a Java Virtual Machine (JVM).


## Install

This program require python 2. to install dependency :

    pip install -r requirement.txt

### Docker

A docker file (*Dockerfile*) is provided to help you test this program. In the top level directory, type the command

	Make docker-build
    
or type the command 

	docker build . -t sidneyli/pyotdr:latest

to build the docker image. It will take a while to download the base image and compile. If 
all goes well, it should successfully build a new docker image *sidneyli/pyotdr:latest*.
You can check with the command:

	docker images
    
once the build is completed. You can now run the command

	Make docker-run
    
or type the docker command:

	docker run -ti --rm -v $HOME:/data sidneyli/pyotdr:latest /bin/bash

to spin up an instance of the docker image. This will start a command shell for you to run the *pyOTDR.py* program.  The docker command
above will mount your home directory to the */data* folder inside the docker instance.  The
command pyOTDR.py (installed as */pyOTDR/pyOTDR.py*) will be in your execution path.
The docker instance removes itself when you exit the instance.

(*Last Revised 2017-12-27*)


