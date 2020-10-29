from monolith.database import User, db, Restaurant
import datetime

def mark_as_positive(user_id):
    qry = db.session.query(User).filter_by(id = user_id).first()
    if qry is None:
        return False
    else:
        qry.is_positive = True
        qry.positive_datetime = datetime.datetime.now()
        db.session.commit()
        return True

def unmark_as_positive(user_id):
    qry = db.session.query(User).filter_by(id = user_id).first()
    if qry is None:
        return False
    else:
        qry.is_positive = False
        qry.positive_datetime = None
        db.session.commit()
        return True