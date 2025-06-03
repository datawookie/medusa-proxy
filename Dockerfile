FROM python:3.13-alpine

RUN apk add tor haproxy privoxy

RUN wget http://dl-cdn.alpinelinux.org/alpine/edge/community/x86_64/lyrebird-0.6.1-r1.apk
RUN apk add --allow-untrusted lyrebird-0.6.1-r1.apk

COPY requirements.txt .

RUN pip3 install -r requirements.txt

WORKDIR /

COPY start.py proxy-list.py config.py /
COPY proxy/ /proxy
COPY templates/ /templates
RUN chmod +x *.py

EXPOSE 2090 1080 8888 8800

CMD python start.py
