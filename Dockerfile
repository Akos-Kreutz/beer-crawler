FROM kreutzakos/python-base:latest

USER root

COPY --chown=root:root main.py /main.py
COPY --chown=root:root lang /lang
COPY --chown=root:root modules /modules

RUN apt update \
    && apt upgrade -y --no-install-recommends

RUN pip install --upgrade pip

RUN pip install requests html5lib lxml beautifulsoup4 XlsxWriter

ENTRYPOINT [ "python", "/main.py" ]