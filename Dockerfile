FROM python:3.9-slim

WORKDIR /pyotdr
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install .


CMD ["pyotdr"]
