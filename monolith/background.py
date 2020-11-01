from celery import Celery
from celery.schedules import crontab
from monolith.database import db,User
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

celery = Celery()
_APP = None

@celery.task
def add_together(a, b):
    return a + b

@celery.task
def test_db():
    log("hello")
    app = _APP
    user = db.session.query(User).first()
    log(user.email)
    return user.email

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
    global _APP
    _APP = app
    if not worker:
        pass