clean:
	rm -f Makefile.bak *-trace.dat *~ */*~ *-dump.json

realclean: clean
	rm -rf *.json *.xml *.pyc test/*.pyc */__pycache__ __pycache__ .cache tests/.cache
	rm -rf build dist pyOTDR.egg-info

build:
	python setup.py build

install:
	python setup.py install

docker-build:
	docker build . -t sidneyli/pyotdr:latest
	
docker-run:
	echo "NOTE: not checking if docker image exists already!"
	docker run -ti --rm -v $(HOME):/data sidneyli/pyotdr:latest /bin/bash

test: testall

testall:
	echo "run tests in tests/"
	pytest

doc:
	pandoc README.md -o README.rst

html: doc
	rst2html5.py README.rst > README.html

test1:
	./pyOTDR/main.py data/demo_ab.sor

test2:
	./pyOTDR/main.py data/sample1310_lowDR.sor
