FROM python:3.9-slim-buster
WORKDIR /flask
RUN apt-get update
# Required for mysqlclient pip package
RUN apt-get install -y gcc libmariadb-dev 
COPY app/ .
RUN pip3 install -r requirements.txt
# Required in unix based systems
RUN pip3 install cryptography
