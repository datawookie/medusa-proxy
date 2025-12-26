# ==================================================================================================
# BUILDER
# ==================================================================================================

FROM python:3.13-alpine3.23 AS builder

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev
RUN uv sync --frozen --no-install-project --no-dev

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

COPY --from=builder /build/.venv /.venv

COPY proxy/ /proxy
COPY templates/ /templates
COPY config.py health-check.py proxy-list.py start.py /

HEALTHCHECK --interval=5m --retries=3 --start-period=15s --timeout=5s CMD ["/health-check.py"]

EXPOSE 1080 2090 8800 8888

ENV PATH="/.venv/bin:$PATH"

CMD ["python3", "/start.py"]
