FROM python:3.8-slim

WORKDIR /pyotdr
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install .


ENTRYPOINT ["pyOTDR"]
