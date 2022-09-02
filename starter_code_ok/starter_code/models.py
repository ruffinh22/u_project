from flask import Flask
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from datetime import datetime, timedelta




app = Flask(__name__)
db = SQLAlchemy()

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False, unique=True)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.Integer, nullable = False, unique=True)
    website_link = db.Column(db.String(120), nullable = True, unique=True)
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable = True)
    facebook_link = db.Column(db.String(120), unique=True)
    shows = db.relationship('Show', backref='venue', lazy = True)
    genres = db.Column(db.ARRAY(db.String()))

   

    def __repr__(self):
        return f'venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.website_link} {self.seeking_talent} {self.seeking_description} {self.image_link} {self.facebook_link} {self.genres} >'


    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False, unique=True)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.Integer, nullable = False, unique=True)
    website_link = db.Column(db.String(120), nullable = True, unique=True)
    facebook_link = db.Column(db.String(120), unique=True)
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable = True)
    shows = db.relationship('Show', backref='artist', lazy = True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.website_link} {self.seeking_talent} {self.seeking_description} {self.image_link} {self.facebook_link} {self.genres} >'

    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# show model


class Show(db.Model):

    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False,
                           default=datetime.utcnow)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def __repr__(self):
        return f'<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>' 
