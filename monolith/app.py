import os
from flask import Flask
from monolith.database import db, User, Restaurant, Booking
from monolith.views import blueprints
from monolith.auth import login_manager
import datetime


def create_app_testing():
    try:
        os.remove("monolith/gooutsafe_test.db")
        os.remove("test.txt")
    except:
        pass

    app = Flask(__name__)

    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gooutsafe_test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app
    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

            example_cust = User()
            example_cust.firstname = 'Customer'
            example_cust.lastname = 'Customer'
            example_cust.email = 'customer@example.com'
            example_cust.dateofbirth = datetime.datetime(2020, 10, 5)
            example_cust.is_admin = False
            example_cust.set_password('customer')
            db.session.add(example_cust)
            db.session.commit()

            auth = User()
            auth.firstname = 'Health'
            auth.lastname = 'Authority'
            auth.email = 'health@authority.com'
            auth.dateofbirth = datetime.datetime(2020, 10, 5)
            auth.is_health_authority = True
            auth.set_password('health')
            db.session.add(auth)
            db.session.commit()

        q = db.session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        if restaurant is None:
            example = Restaurant()
            example.name = 'Trial Restaurant'
            example.likes = 42
            example.phone = 555123456
            example.lat = 43.720586
            example.lon = 10.408347
            example.tables_number = 10
            example.tables_capacity = 5
            example.opening_hour_lunch = 10
            example.closing_hour_lunch = 16
            example.opening_hour_dinner = 21
            example.closing_hour_dinner = 23
            example.occupation_time = datetime.timedelta(2)
            example.closed_days = "17"
            db.session.add(example)
            db.session.commit()

            example_op = User()
            example_op.firstname = 'Operator'
            example_op.lastname = 'Operator'
            example_op.email = 'operator@example.com'
            example_op.dateofbirth = datetime.datetime(2020, 10, 5)
            example_op.is_admin = False
            example_op.set_password('operator')
            example_op.rest_id = 1
            db.session.add(example_op)
            db.session.commit()

            booking_1 = Booking()
            booking_1.rest_id = 1
            booking_1.user_id = 2
            booking_1.booking_datetime = datetime.datetime(2020,11,1,10,15,0,0)
            booking_1.person_number = 5
            db.session.add(booking_1)
            db.session.commit()

            booking_2 = Booking()
            booking_2.rest_id = 1
            booking_2.user_id = 2
            booking_2.booking_datetime = datetime.datetime(2020,11,1,10,15,0,0)
            booking_2.person_number = 5
            db.session.add(booking_2)
            db.session.commit()

            booking_3 = Booking()
            booking_3.rest_id = 1
            booking_3.user_id = 2
            booking_3.booking_datetime = datetime.datetime(2020,11,1,11,30,0,0)
            booking_3.person_number = 5
            db.session.add(booking_3)
            db.session.commit()


    return app


def create_app_production():
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gooutsafe.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

            auth = User()
            auth.firstname = 'Health'
            auth.lastname = 'Authority'
            auth.email = 'health@authority.com'
            auth.dateofbirth = datetime.datetime(2020, 10, 5)
            auth.is_health_authority = True
            auth.set_password('health')
            db.session.add(auth)
            db.session.commit()

            example_cust = User()
            example_cust.firstname = 'Customer'
            example_cust.lastname = 'Customer'
            example_cust.email = 'customer@example.com'
            example_cust.dateofbirth = datetime.datetime(2020, 10, 5)
            example_cust.is_admin = False
            example_cust.set_password('customer')
            db.session.add(example_cust)
            db.session.commit()

        q = db.session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        if restaurant is None:
            example = Restaurant()
            example.name = 'Trial Restaurant'
            example.likes = 42
            example.phone = 555123456
            example.lat = 43.720586
            example.lon = 10.408347
            example.tables_number = 10
            example.tables_capacity = 5
            example.opening_hour_lunch = 10
            example.closing_hour_lunch = 16
            example.opening_hour_dinner = 21
            example.closing_hour_dinner = 23
            example.occupation_time =  datetime.timedelta(2)
            example.closed_days = "17"
            db.session.add(example)


            example_op = User()
            example_op.firstname = 'Operator'
            example_op.lastname = 'Operator'
            example_op.email = 'operator@example.com'
            example_op.dateofbirth = datetime.datetime(2020, 10, 5)
            example_op.is_admin = False
            example_op.set_password('operator')
            example_op.rest_id(1)
            db.session.add(example_op)
            db.session.commit()

            booking_1 = Booking()
            booking_1.rest_id = 1
            booking_1.user_id = 2
            booking_1.booking_datetime = datetime.datetime(2020,11,1,10,15,0,0)
            booking_1.person_number = 5
            db.session.add(booking_1)
            db.session.commit()

            booking_2 = Booking()
            booking_2.rest_id = 1
            booking_2.user_id = 2
            booking_2.booking_datetime = datetime.datetime(2020,11,1,10,15,0,0)
            booking_2.person_number = 5
            db.session.add(booking_2)
            db.session.commit()

            booking_3 = Booking()
            booking_3.rest_id = 1
            booking_3.user_id = 2
            booking_3.booking_datetime = datetime.datetime(2020,11,1,11,30,0,0)
            booking_3.person_number = 5
            db.session.add(booking_3)
            db.session.commit()


    return app


if __name__ == '__main__':
    app = create_app_production()
    app.run()
