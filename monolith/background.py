from celery import Celery
from celery.schedules import crontab
from monolith.database import db, User, Restaurant

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


@celery.task(run_every=crontab(minute=1))
def every_monday_morning():
    print("This runs every Monday morning at 7:30a.m.")


@celery.task
def add_together(a, b):
    return a + b

result = add_together.delay(23, 42)
print("ciao")
print(result.wait())

@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP

    return []

