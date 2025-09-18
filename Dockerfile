FROM docker.io/library/python:3.13-alpine

WORKDIR /

COPY requirements.txt .

RUN pip3 install --no-cache-dir --requirement requirements.txt; \
  rm requirements.txt

COPY proxy/ /proxy
COPY templates/ /templates
COPY config.py proxy-list.py start.py /

RUN apk --no-cache --no-progress add haproxy lyrebird=~0.6 privoxy tor; \
  chmod +x config.py proxy-list.py start.py

EXPOSE 1080 2090 8800 8888

CMD ["/start.py"]
