clean:
	rm -f Makefile.bak *-trace.dat *~ */*~ *-dump.json

realclean: clean
	rm -rf *.json *.xml *.pyc test/*.pyc test/__pycache__ __pycache__ .cache test/.cache

docker-build:
	docker build . -t sidneyli/pyotdr:latest
	
docker-run:
	echo "NOTE: not checking if docker image exists already!"
	docker run -ti --rm -v $(HOME):/data sidneyli/pyotdr:latest /bin/bash

test: testall

testall:
	echo "run tests in test/"
	pytest

test1:
	./pyOTDR/main.py data/demo_ab.sor

test2:
	./pyOTDR/main.py data/sample1310_lowDR.sor
