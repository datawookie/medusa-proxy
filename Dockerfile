FROM alpine:edge

COPY requirements.txt .

RUN apk add 'tor' --no-cache \
      --repository http://dl-cdn.alpinelinux.org/alpine/edge/community \
      --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
      --allow-untrusted haproxy privoxy python3 && \
    python3 -m ensurepip && \
    pip3 install -r requirements.txt

WORKDIR /

COPY start.py proxy-list.py /
COPY proxy/ /proxy
COPY templates/ /templates
RUN chmod +x *.py

EXPOSE 2090 1080 8888 8800

CMD ./start.py
