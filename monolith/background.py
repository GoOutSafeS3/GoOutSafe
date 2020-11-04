from celery import Celery
from celery.schedules import crontab
from monolith.database import db,User,Rating,Restaurant
from celery.utils.log import get_task_logger
import datetime
from monolith.utilities.contact_tracing import unmark_as_positive

logger = get_task_logger(__name__)

celery = Celery()
_APP = None


@celery.task
def unmark():
    with _APP.app_context():
        now = datetime.datetime.now()
        users = db.session.query(User)\
        .filter_by(is_positive = True)\
        .all() 

        negatives = []
        for u in users:
            if u.positive_datetime+datetime.timedelta(days=14) <= now:
                negatives.append(u)
                unmark_as_positive(u.id)

        log(negatives)

@celery.task
def recompute_ratings():
    with _APP.app_context():
        try:
            ratings = db.session.query(Rating).filter().all()
            rests_rating = {}
            for rate in ratings:
                sum,num = rests_rating.get(rate.restaurant_id, (0,0))
                rests_rating[rate.restaurant_id] = (sum+rate.rating, num+1)
                rate.marked = True
            for rest_id,(sum,num) in rests_rating.items():
                rest = db.session.query(Restaurant).filter(Restaurant.id == rest_id).first()
                rest.rating_val = sum/num
                rest.rating_num = num
        except: # pragma: no cover
            traceback.print_exc()
            logger.info("hello-rollback")
            db.session.rollback()
            raise
        else:
            logger.info("hello-commit")
            db.session.commit()
import traceback


@celery.task
def check_ratings():
    with _APP.app_context():
        try:
            ratings = db.session.query(Rating).filter(Rating.marked == False).all()
            for rate in ratings:
                val = rate.restaurant.rating_val
                num = rate.restaurant.rating_num
                rate.restaurant.rating_val = (val*num + rate.rating) / (num+1)
                rate.restaurant.rating_num += 1
                rate.marked = True
        except:
            traceback.print_exc()
            logger.info("hello-rollback")
            db.session.rollback()
            raise
        else:
            logger.info("hello-commit")
            db.session.commit()

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