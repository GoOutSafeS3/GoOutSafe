import os
from flask import Flask
from flask_googlemaps import GoogleMaps, Map

from monolith.database import db, User, Restaurant, Booking, Table
from monolith.views import blueprints
from monolith.auth import login_manager
from monolith.background import init_celery
from celery import Celery
import sys
import os
import datetime
import configparser


DEFAULT_CONFIGURATION = {

    "fake_data" : False,
    "remove_db" : False,
    "db_dropall" : False,

    "wtf_csrf_secret_key" : 'A SECRET KEY',
    "secret_key" : 'ANOTHER ONE',
    "sqlalchemy_database_uri" : 'sqlite:///db/gooutsafe.db',
    "sqlalchemy_track_modifications" : False,
    
    "result_backend" : os.getenv("BACKEND", "redis://localhost:6379"),
    "broker_url" : os.getenv("BROKER", "redis://localhost:6379")
}

def get_config(configuration=None):
    parser = configparser.ConfigParser()
    if parser.read('config.ini') != []:
        
        if type(configuration) != str:
            configuration = parser["CONFIG"]["CONFIG"]

        print("- GoOutSafe CONFIGURATION:",configuration)
        configuration = parser._sections[configuration]

        for k,v in DEFAULT_CONFIGURATION.items():
            if not k in configuration:
                configuration[k] = v

        return configuration
    else:
        return DEFAULT_CONFIGURATION

def fake_data():
    example_cust = User()
    example_cust.firstname = 'Customer'
    example_cust.lastname = 'Customer'
    example_cust.email = 'customer@example.com'
    example_cust.phone = 5551234561
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
        example.opening_hour_lunch = 10
        example.closing_hour_lunch = 16
        example.opening_hour_dinner = 21
        example.closing_hour_dinner = 23
        example.occupation_time = 2
        example.closed_days = "17"
        example.cuisine_type = "True Italian Restaurant"
        example.menu = "Pasta Bolognese\nPizza\nBreadsticks"
        db.session.add(example)
        db.session.commit()

        table_1 = Table()
        table_1.rest_id = example.id
        table_1.capacity = 5
        db.session.add(table_1)
        db.session.commit()

        table_2 = Table()
        table_2.rest_id = example.id
        table_2.capacity = 6
        db.session.add(table_2)
        db.session.commit()

        table_3 = Table()
        table_3.rest_id = example.id
        table_3.capacity = 7
        db.session.add(table_3)
        db.session.commit()

        table_4 = Table()
        table_4.rest_id = example.id
        table_4.capacity = 9
        db.session.add(table_4)
        db.session.commit()

        table_5 = Table()
        table_5.rest_id = example.id
        table_5.capacity = 8
        db.session.add(table_5)
        db.session.commit()

        example_op = User()
        example_op.firstname = 'Operator'
        example_op.lastname = 'Operator'
        example_op.email = 'operator@example.com'
        example_op.phone = 5551234563
        example_op.dateofbirth = datetime.datetime(2020, 10, 5)
        example_op.is_admin = False
        example_op.set_password('operator')
        example_op.rest_id = 1
        db.session.add(example_op)
        db.session.commit()

    q = db.session.query(Restaurant).filter(Restaurant.id == 2)
    restaurant = q.first()
    if restaurant is None:
        example = Restaurant()
        example.name = 'Osteria dei Santi'
        example.likes = 102
        example.phone = 555127156
        example.lat = 43.7191589
        example.lon = 10.3973009
        example.opening_hour_lunch = 11
        example.closing_hour_lunch = 16
        example.opening_hour_dinner = 20
        example.closing_hour_dinner = 23
        example.occupation_time = 2
        example.closed_days = "17"
        example.cuisine_type = "typical Tuscan cuisine"
        example.menu = "Primi\nSecondi\nDolci"
        db.session.add(example)
        db.session.commit()

        example_op = User()
        example_op.firstname = 'Operator2'
        example_op.lastname = 'Operator2'
        example_op.email = 'operator2@example.com'
        example_op.phone = 3484051562
        example_op.dateofbirth = datetime.datetime(2020, 10, 5)
        example_op.is_admin = False
        example_op.set_password('operator2')
        example_op.rest_id = 2
        db.session.add(example_op)
        db.session.commit()

    q = db.session.query(Restaurant).filter(Restaurant.id == 3)
    restaurant = q.first()
    if restaurant is None:
        example = Restaurant()
        example.name = 'Le Bandierine'
        example.likes = 140
        example.phone = 555427156
        example.lat = 43.7177699
        example.lon = 10.4038814
        example.opening_hour_lunch = 11
        example.closing_hour_lunch = 16
        example.opening_hour_dinner = None
        example.closing_hour_dinner = None
        example.occupation_time = 2
        example.closed_days = "1"
        example.cuisine_type = "typical Tuscan cuisine"
        example.menu = "Primi\nSecondi\nDolci"
        db.session.add(example)
        db.session.commit()

        example_op = User()
        example_op.firstname = 'Operator3'
        example_op.lastname = 'Operator3'
        example_op.email = 'operator3@example.com'
        example_op.phone = 3484051566
        example_op.dateofbirth = datetime.datetime(2020, 10, 5)
        example_op.is_admin = False
        example_op.set_password('operator3')
        example_op.rest_id = 3
        db.session.add(example_op)
        db.session.commit()

        example_positive = User()
        example_positive.firstname = 'Positive'
        example_positive.lastname = 'Positive'
        example_positive.email = 'positive@example.com'
        example_positive.phone = 5551234565
        example_positive.dateofbirth = datetime.datetime(2020, 10, 5)
        example_positive.is_admin = False
        example_positive.is_positive = True
        example_positive.positive_datetime = datetime.datetime.now()
        example_positive.set_password('positive')
        db.session.add(example_positive)
        db.session.commit()

        example_positive1 = User()
        example_positive1.firstname = 'Another'
        example_positive1.lastname = 'Positive'
        example_positive1.email = 'a.positive@example.com'
        example_positive1.phone = "0987654321"
        example_positive1.ssn = "987654321"
        example_positive1.dateofbirth = datetime.datetime(2020, 10, 5)
        example_positive1.is_admin = False
        example_positive1.is_positive = True
        example_positive1.positive_datetime = datetime.datetime.now()
        example_positive1.set_password('positive')
        db.session.add(example_positive1)

        example_cust1 = User()
        example_cust1.firstname = 'Another'
        example_cust1.lastname = 'Customer'
        example_cust1.email = 'a.customer@example.com'
        example_cust1.phone = "1234567890"
        example_cust1.ssn = "1234567890"
        example_cust1.dateofbirth = datetime.datetime(2020, 10, 5)
        example_cust1.is_admin = False
        example_cust1.set_password('customer')
        db.session.add(example_cust1)
        db.session.commit()

        booking_1 = Booking()
        booking_1.rest_id = 1
        booking_1.user_id = example_cust.id
        booking_1.booking_datetime = datetime.datetime(2020,10,20,10,15,0,0)
        booking_1.entrance_datetime = datetime.datetime(2020,10,20,10,15,0,0)
        booking_1.people_number = 5
        booking_1.table_id = 1
        db.session.add(booking_1)
        db.session.commit()

        booking_2 = Booking()
        booking_2.rest_id = 1
        booking_2.user_id = example_positive.id
        booking_2.booking_datetime = datetime.datetime(2020,10,20,10,15,0,0)
        booking_2.entrance_datetime = datetime.datetime(2020,10,20,10,15,0,0)
        booking_2.people_number = 5
        booking_2.table_id = 2
        db.session.add(booking_2)
        db.session.commit()

        booking_3 = Booking()
        booking_3.rest_id = 1
        booking_3.user_id = example_cust.id
        booking_3.booking_datetime = datetime.datetime(2020,10,5,11,30,0,0)
        booking_3.people_number = 5
        booking_3.table_id = 3
        db.session.add(booking_3)
        db.session.commit()

        booking_4 = Booking()
        booking_4.rest_id = 1
        booking_4.user_id = example_positive.id
        booking_4.booking_datetime = datetime.datetime(2020,10,5,18,30,0,0)
        booking_4.people_number = 5
        booking_4.table_id = 5
        db.session.add(booking_4)
        db.session.commit()

        booking_1 = Booking()
        booking_1.rest_id = 1
        booking_1.user_id = example_cust.id
        booking_1.booking_datetime = datetime.datetime.now() + datetime.timedelta(days=1)
        booking_1.people_number = 5
        booking_1.table_id = 4
        db.session.add(booking_1)
        db.session.commit()


        booking_6 = Booking()
        booking_6.rest_id = 1
        booking_6.user_id = example_positive.id
        booking_6.booking_datetime = datetime.datetime(2021,10,5,18,30,0,0)
        booking_6.people_number = 5
        booking_6.table_id = 5
        db.session.add(booking_6)
        db.session.commit()

        booking_7 = Booking()
        booking_7.rest_id = 1
        booking_7.user_id = example_cust.id
        booking_7.booking_datetime = datetime.datetime(2010,10,5,18,30,0,0)
        booking_7.people_number = 5
        booking_7.table_id = 5
        db.session.add(booking_7)
        db.session.commit()

        booking_8 = Booking()
        booking_8.rest_id = 1
        booking_8.user_id = example_positive.id
        booking_8.booking_datetime = datetime.datetime.now()
        booking_8.people_number = 5
        booking_8.table_id = 2
        db.session.add(booking_8)
        db.session.commit()

        booking_9 = Booking()
        booking_9.rest_id = 1
        booking_9.user_id = example_cust.id
        booking_9.booking_datetime = datetime.datetime.now()
        booking_9.people_number = 5
        booking_9.table_id = 1
        db.session.add(booking_9)
        db.session.commit()

    user_to_add = User()
    user_to_add.firstname = 'Gianni'
    user_to_add.lastname = 'Verdi'
    user_to_add.email = 'gianni@example.com'
    user_to_add.phone = 2351235651
    user_to_add.dateofbirth = datetime.datetime(1950, 10, 5)
    user_to_add.is_admin = False
    user_to_add.set_password('gianni')
    db.session.add(user_to_add)
    db.session.commit()

    booking_10 = Booking()
    booking_10.rest_id = 1
    booking_10.user_id = user_to_add.id
    booking_10.booking_datetime = datetime.datetime.now() - datetime.timedelta(days=2)
    booking_10.entrance_datetime = datetime.datetime.now() - datetime.timedelta(days=2)
    booking_10.people_number = 2
    booking_10.table_id = 2
    db.session.add(booking_10)
    db.session.commit()

    user_to_add = User()
    user_to_add.firstname = 'Alice'
    user_to_add.lastname = 'Rossi'
    user_to_add.email = 'alice@example.com'
    user_to_add.phone = 2354673561
    user_to_add.dateofbirth = datetime.datetime(1960, 11, 6)
    user_to_add.is_admin = False
    user_to_add.set_password('alice')
    db.session.add(user_to_add)
    db.session.commit()

    booking_11 = Booking()
    booking_11.rest_id = 1
    booking_11.user_id = user_to_add.id
    booking_11.booking_datetime = datetime.datetime.now() - datetime.timedelta(days=2)
    booking_11.entrance_datetime = datetime.datetime.now() - datetime.timedelta(days=2)
    booking_11.people_number = 2
    booking_11.table_id = 3
    db.session.add(booking_11)
    db.session.commit()

def init():
    q = db.session.query(User).filter(User.email == 'example@example.com')
    admin = q.first()
    if admin is None:
        example = User()
        example.firstname = 'Admin'
        example.lastname = 'Admin'
        example.email = 'example@example.com'
        example.dateofbirth = datetime.datetime(2020, 10, 5)
        example.is_admin = True
        example.set_password('admin')
        db.session.add(example)
        db.session.commit()

    q = db.session.query(User).filter(User.email == 'health@authority.com')
    health = q.first()
    if health is None:
        auth = User()
        auth.firstname = 'Health'
        auth.lastname = 'Authority'
        auth.email = 'health@authority.com'
        auth.dateofbirth = datetime.datetime(2020, 10, 5)
        auth.is_health_authority = True
        auth.set_password('health')
        db.session.add(auth)
        db.session.commit()

def create_app(configuration):

    app = Flask(__name__)

    try: 
        os.mkdir("monolith/db") 
    except OSError as error: 
        pass   
    
    configuration = os.getenv("CONFIG", configuration)
    config = get_config(configuration)

    if config["remove_db"]:
        try:
            os.remove(config["sqlalchemy_database_uri"])
        except:
            pass

    app.config['WTF_CSRF_SECRET_KEY'] = config["wtf_csrf_secret_key"]
    app.config['SECRET_KEY'] = config["secret_key"]
    app.config['SQLALCHEMY_DATABASE_URI'] = config["sqlalchemy_database_uri"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["sqlalchemy_track_modifications"]
    app.config['result_backend'] = config['result_backend']
    app.config['broker_url'] = config['broker_url']

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)

    if config["db_dropall"]:
        db.drop_all(app=app)

    db.create_all(app=app)

    init_celery(app)
    GoogleMaps(app)

    # create a first admin user
    with app.app_context():
        init()
        if config["fake_data"]:
            fake_data()

    return app

def create_worker_app():
    configuration = os.getenv("CONFIG", "TEST")
    config = get_config(configuration)
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = config["wtf_csrf_secret_key"]
    app.config['SECRET_KEY'] = config["secret_key"]
    app.config['SQLALCHEMY_DATABASE_URI'] = config["sqlalchemy_database_uri"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["sqlalchemy_track_modifications"]
    app.config['result_backend'] = config['result_backend']
    app.config['broker_url'] = config['broker_url']
    db.init_app(app)
    init_celery(app, worker=True)

    return app

if __name__ == '__main__':
    c = None
    if len(sys.argv) > 1:
        c = sys.argv[1]        

    app = create_app(c)
    app.run()
