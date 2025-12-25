FROM python:3.13-alpine3.23

WORKDIR /

COPY proxy/ /proxy
COPY templates/ /templates
COPY config.py health-check.py proxy-list.py start.py /
COPY requirements.txt .

RUN apk --no-cache --no-progress add haproxy lyrebird=~0.7 privoxy tor; \
  pip3 install --no-cache-dir --requirement requirements.txt; \
  rm requirements.txt

HEALTHCHECK --interval=5m --retries=3 --start-period=15s --timeout=5s CMD ["/health-check.py"]

EXPOSE 1080 2090 8800 8888

CMD ["/start.py"]
