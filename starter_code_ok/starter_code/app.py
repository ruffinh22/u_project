#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import logging
from operator import itemgetter
from time import time, strftime
from forms import VenueForm, ArtistForm, ShowForm
from forms import *
from flask_wtf import Form
from logging import Formatter, FileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import babel
import dateutil.parser
import json
from flask_migrate import Migrate
#from flask_script import Manager
import sys
import os
import secrets
from db_obj import db_setup
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from models import app, db, Venue, Artist, Show

#from app import views
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

#phone_number = os.environ.get('PHONE_NUMBER', '+11234567890')


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#--------------S--------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
#db.create.all()
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  venue_state_and_city = ''
  data = []
  
  for venue in venues:
    
    upcoming_shows = db.session.query(Venue).join(Show).filter(Show.start_time > datetime.now()).all()
    if venue_state_and_city == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(upcoming_shows) 
      })
    else:
      venue_state_and_city == venue.city + venue.state
      data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })


  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  resultat = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()
  response = {
    "count": len(resultat),
    "data": resultat
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # j= Venue.join(Show, Venue.c.id == Show.c.venue_id)
  venue=Venue.query.get(venue_id)
  show_venues = db.session.query(Show).join(Venue).filter(Show.venue_id==Venue.id).all()
  upcoming_shows = []
  data = []
  for show in show_venues:
    if show.start_time > datetime.now():
      upcoming_shows.append(show)
    
    data = ({
    "id": venue.id,
    "name": venue.name,
    "upcoming_shows_count": len(upcoming_shows)
    })
  return render_template("pages/show_venue.html", venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  data = Venue()
  try:
    if request.method == 'POST':
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      
      data.name = name
      data.city = city
      data.state = state
      data.address = address
      data.phone = phone
      data.genres = genres
      data.facebook_link = facebook_link
      data.image_link = image_link
      
      db.session.add(data)
      db.session.commit()
      flash('Venue ' + data.name + ' was successfully listed!')
      return redirect(request.url)
      #return render_template('forms/new_venue.html')
  except:
      flash('An error occurred.'  'Venue ' + data.name + ' could not be listed.')
      db.session.rollback()
  finally:
      db.session.close()
      # on successful db insert, flash success
      
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue " + venue.name + " was deleted successfully!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Venue was not deleted successfully.")
    finally:
        db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()
  response = {
    "count": len(result),
    "data": result
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
   # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  #artist_genres = [s.strip() for s in artist.genres[1:-1].split(',')]
  up_pa_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==Artist.id).filter(Show.start_time>= datetime.now()).all()
 

  past_shows = []
  upcoming_shows = []
  for show in up_pa_shows:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
      "start_time": str(show.start_time)
    }
    if(up_pa_shows):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
   
    
    "past_shows": past_shows
    
   
    
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
 

  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)
   

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form['image_link']
  artist.website_link = request.form['website_link']
  try:
    db.session.add(artist)
    db.session.commit()
    flash("Artist {} is updated successfully".format(artist.name))
  except:
    db.session.rollback()
    flash("Artist {} isn't updated successfully".format(artist.name))
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form.getlist('genres')
  venue.facebook_link = request.form['facebook_link']
  venue.image_link = request.form['image_link']
    
  try:
    db.session.add(venue)
    db.session.commit()
    flash("Venue {} is updated successfully".format(venue.name))
  except:
    db.session.rollback()
    flash("Venue {} isn't updated successfully".format(venue.name))
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  data = Artist()
  try:
    if request.method == 'POST':
      req = request.form
      name = req['name']
      city = req['city']
      state = req['state']
      phone = req['phone']
      genres = request.form.getlist('genres')
      facebook_link = req['facebook_link']
      image_link= req['image_link']
      seeking_venue = True if 'seeking_venue' in req else False
      seeking_description = req['seeking_description']
      
      
      data.name = name
      data.city = city
      data.state = state
      data.phone = str(phone)
      data.genres = genres
      data.facebook_link = facebook_link
      data.image_link = image_link
      data.seeking_venue = seeking_venue
      data.seeking_description = seeking_description
      


      db.session.add(data)
      db.session.commit()
      flash('Artist ' + data.name + ' was successfully listed!')
    return redirect(request.url)
    #return render_template('forms/new_artist.html')
  except:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  ##shows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).filter(Show.start_time > datetime.now()).all()
  data = []
  for show in db.session.query(Show).join(Artist).join(Venue).all():
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                "artist_id": Artist.query.filter_by(id=show.artist_id).first().id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": str(show.start_time)
            }
        )
        
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():

  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  data = {
  'artist_id':int(request.form.get('artist_id')),
  'venue_id':int(request.form.get('venue_id')),
  'start_time':str(request.form.get('start_time'))
  }
  try:
    new_show = Show(
      venue_id=request.form['venue_id'],
      artist_id=request.form['artist_id'],
      start_time=request.form['start_time'],
    )
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except SQLAlchemyError as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occured. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

