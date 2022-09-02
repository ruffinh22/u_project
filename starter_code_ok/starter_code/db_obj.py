from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from models import app

db = SQLAlchemy()



# TODO: connect to a local postgresql database
def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db
