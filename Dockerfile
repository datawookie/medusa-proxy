# ==================================================================================================
# BUILDER
# ==================================================================================================

FROM python:3.13-alpine3.23 AS builder

WORKDIR /build

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==================================================================================================
# RUNNER
# ==================================================================================================

FROM python:3.13-alpine3.23 AS runner

WORKDIR /

RUN apk --no-cache --no-progress add \
    haproxy \
    lyrebird=~0.7 \
    privoxy \
    tor && \
    rm -rf /var/cache/apk/*

COPY --from=builder /install /usr/local

COPY proxy/ /proxy
COPY templates/ /templates
COPY config.py health-check.py proxy-list.py start.py /

RUN find /usr/local/lib/python3.13 -name "__pycache__" -type d -exec rm -rf {} + && \
    rm -rf /usr/local/lib/python3.13/idlelib \
           /usr/local/lib/python3.13/ensurepip \
           /usr/local/lib/python3.13/pydoc_data \
           /usr/local/include

HEALTHCHECK --interval=5m --retries=3 --start-period=15s --timeout=5s CMD ["/health-check.py"]

EXPOSE 1080 2090 8800 8888

CMD ["python3", "/start.py"]
