FROM python:3.7-alpine3.11
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
ENV FLASK_APP=monolith.app:create_app_testing
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
