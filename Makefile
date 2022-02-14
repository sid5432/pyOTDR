clean:
	rm -f Makefile.bak *-trace.dat *~ */*~ *-dump.json

realclean: clean
	rm -rf *.json *.xml pyotdr/*.pyc *.pyc test/*.pyc */__pycache__ __pycache__ .cache tests/.cache
	rm -rf build dist pyotdr.egg-info

build: realclean
	python -m build
	
dist: build
	python setup.py sdist bdist_wheel

upload: dist
	twine upload dist/*

install: build
	python -m build

docker-build:
	docker build . -t sidneyli/pyotdr:latest
	
docker-run:
	echo "NOTE: not checking if docker image exists already!"
	docker run -ti --rm -u `id -u`:`id -g` -v $(HOME):/data sidneyli/pyotdr:latest /bin/bash

test: testall

testall:
	echo "run tests in tests/"
	pytest

doc:
	pandoc README.md -o README.rst

html: doc
	rst2html5.py README.rst > README.html

test1:
	./pyotdr/main.py data/demo_ab.sor

test2:
	./pyotdr/main.py data/sample1310_lowDR.sor
