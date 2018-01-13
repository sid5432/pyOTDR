FROM python:latest
MAINTAINER Sidney Li <sidney.hy.li@gmail.com>

COPY pyOTDR /pyOTDR

WORKDIR /pyOTDR

# python3 is /usr/local/bin/python in python:latest
RUN sed -i "s/usr\/bin\/python/usr\/local\/bin\/python/" /pyOTDR/main.py
RUN ln -s /pyOTDR/main.py /usr/bin/pyOTDR

# need to complete installation of utils before installing lazyxml
RUN pip install utils
RUN pip install crcmod
RUN pip install lazyxml

