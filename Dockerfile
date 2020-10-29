FROM python:3.7-alpine3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD . /code
WORKDIR /code
ENV FLASK_APP=monolith.app:create_app_testing
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
