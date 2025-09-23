FROM docker.io/library/python:3.13-alpine

WORKDIR /

COPY proxy/ /proxy
COPY templates/ /templates
COPY config.py proxy-list.py start.py /
COPY requirements.txt .

RUN apk --no-cache --no-progress add haproxy lyrebird=~0.6 privoxy tor; \
  pip3 install --no-cache-dir --requirement requirements.txt; \
  rm requirements.txt

EXPOSE 1080 2090 8800 8888

CMD ["/start.py"]
