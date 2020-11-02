# GoOutSafe

[![Coverage Status](https://coveralls.io/repos/github/frabert/GoOutSafe/badge.png?branch=master&service=github)](https://coveralls.io/github/frabert/GoOutSafe?branch=master)

## Running the code

Building the Docker images:

```
$ docker-compose build
```

### Unit tests

```
$ docker-compose up tests
```

### Running in production mode

```
$ docker-compose -f docker-compose.yml up monolith
```

### Running in testing mode (with test data)

```
$ docker-compose up monolith
```

### Only run Redis & Celery workers

Flask will be executed locally

```
$ docker-compose up -d local
$ pip install -r requirements.txt
$ FLASK_APP=monolith.app:create_app flask run
```