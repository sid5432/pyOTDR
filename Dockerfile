FROM python:2

COPY . /pyOTDR

WORKDIR /pyOTDR

RUN pip install -r requirements.txt

ENTRYPOINT ["python2", "read.py"]
