FROM python:3.13-alpine

RUN apk add tor haproxy privoxy

COPY requirements.txt .

RUN pip3 install -r requirements.txt

WORKDIR /

COPY start.py proxy-list.py config.py /
COPY proxy/ /proxy
COPY templates/ /templates
RUN chmod +x *.py

EXPOSE 2090 1080 8888 8800

CMD ./start.py
