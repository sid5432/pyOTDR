clean:
	rm -f Makefile.bak *-trace.dat *~ test/*~ *-dump.json

realclean: clean
	rm -rf *.json *.xml *.pyc test/*.pyc test/__pycache__ .cache test/.cache

docker:
	docker build . -t sidneyli/pyotdr:latest
	
docker-run:
	echo "NOTE: not checking of docker image exists already"
	docker run -ti --rm -v /home/sid/:/data sidneyli/pyotdr:latest /bin/bash

test:
	pytest
