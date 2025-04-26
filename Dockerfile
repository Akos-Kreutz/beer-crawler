FROM python:3.14.0a7-alpine3.21

COPY --chown=root:root main.py /main.py
COPY --chown=root:root lang /lang
COPY --chown=root:root modules /modules

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    libffi-dev \
    openssl-dev

RUN pip install requests html5lib lxml beautifulsoup4 XlsxWriter

ENTRYPOINT [ "python", "/main.py" ]