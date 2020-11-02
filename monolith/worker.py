from celery import Celery
from celery.schedules import crontab

from monolith.app import create_worker_app
from monolith.background import log,test_db

def create_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config["result_backend"],
        broker=app.config["broker_url"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_worker_app()
celery = create_celery(app)

#commented scheduled task work
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #here call only tasks, it does not work with normal functions (at least print does not work)
    # Calls log every 10 seconds.
    sender.add_periodic_task(10.0, log.s("Logging Stuff 10"), name="reverse every 10")

    # Calls log('Logging Stuff') every 30 seconds
    #sender.add_periodic_task(15.0, test_db.s(), name="Log every 15")

    # Executes every Monday morning at 7:30 a.m.
    #sender.add_periodic_task(
    #    crontab(minute=30, hour=7), log.s("Monday morning log!"),
    #)