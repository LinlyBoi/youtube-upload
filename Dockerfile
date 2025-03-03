FROM python:3.7-alpine3.8

ENV workdir /data
WORKDIR ${workdir}

RUN mkdir -p ${workdir} && adduser python --disabled-password
COPY . ${workdir}
WORKDIR ${workdir}
RUN pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 progressbar2 && \
    python setup.py install

USER python

ENTRYPOINT ["youtube-upload"]
