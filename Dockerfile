FROM python:3.11.5-alpine3.18

COPY --chown=root:root main.py /main.py
COPY --chown=root:root lang /lang
COPY --chown=root:root modules /modules

RUN pip install requests html5lib lxml beautifulsoup4 XlsxWriter

ENTRYPOINT [ "python", "/main.py" ]