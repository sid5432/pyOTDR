clean:
	rm -f Makefile.bak *-trace.dat *~ test/*~ *-dump.json

realclean: clean
	rm -rf *.json *.xml *.pyc test/*.pyc test/__pycache__ .cache test/.cache
