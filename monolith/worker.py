from celery import Celery

from monolith.app import create_worker_app

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

#@celery.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
    # Calls print every 10 seconds.
#    sender.add_periodic_task(10.0, print("HEllO!!"), name="reverse every 10")

    # Calls log('Logging Stuff') every 30 seconds
    #sender.add_periodic_task(30.0, log.s(("Logging Stuff")), name="Log every 30")

    # Executes every Monday morning at 7:30 a.m.
    #sender.add_periodic_task(
    #    crontab(hour=7, minute=30, day_of_week=1), log.s("Monday morning log!"),
    #)