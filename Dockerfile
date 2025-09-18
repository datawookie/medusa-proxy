FROM docker.io/library/python:3.13-alpine

RUN apk --no-cache --no-progress add haproxy privoxy tor lyrebird=~0.6

WORKDIR /

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY start.py proxy-list.py config.py /
COPY proxy/ /proxy
COPY templates/ /templates

RUN chmod +x *.py

EXPOSE 1080 2090 8800 8888

CMD ["./start.py"]
