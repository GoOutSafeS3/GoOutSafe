from celery import Celery
from celery.schedules import crontab
from monolith.database import db

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

celery = Celery()

@celery.task(run_every=crontab(minute=1))
def every_monday_morning():
    print("This runs every Monday morning at 7:30a.m.")


@celery.task
def add_together(a, b):
    return a + b

@celery.task
def log(message):
    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)

def init_celery(app, worker=False):
    #print(app.config,flush=True)
    # load celery config
    celery.config_from_object(app.config)

    if not worker:
        # register celery irrelevant extensions
        pass