FROM python:3.7-alpine3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest pytest-cov
ADD . /code
WORKDIR /code

ENV FLASK_APP=monolith.app:create_app
ENV BROKER=redis://redis:6379
ENV BACKEND=redis://redis:6379
ENV CONFIG=PRODUCTION

RUN cp /code/docker/* /code/
RUN chmod +x /code/*
CMD ["/code/monolith.sh"]