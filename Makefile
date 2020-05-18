clean:
	rm -f Makefile.bak *-trace.dat *~ */*~ *-dump.json

realclean: clean
	rm -rf *.json *.xml pyOTDR/*.pyc *.pyc test/*.pyc */__pycache__ __pycache__ .cache tests/.cache
	rm -rf build dist pyOTDR.egg-info

build: realclean
	python setup.py build
	
dist: build
	python setup.py sdist bdist_wheel

upload: dist
	twine upload dist/*

install: build
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
	pyOTDR data/demo_ab.sor

test2:
	pyOTDR data/sample1310_lowDR.sor
