#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import datetime
import json

from flask.globals import session

import dateutil.parser
from sqlalchemy.sql.expression import false, true
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import*
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

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
 
  venues_data_all = Venue.query.with_entities(Venue.city,Venue.state,func.count(Venue.id)).group_by(Venue.state,Venue.city).all()
  data = []
  for venues in venues_data_all:
    venues_data = Venue.query.filter_by(state=venues.state).filter_by(city=venues.city).all()
    venue_data = []
    for venue in venues_data:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      "city":venue.city,
      "state":venue.state,
      "venues": venue_data
    })

    return render_template('pages/venues.html', areas=data);
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get("search_term","")
  search = "%{0}%".format(search_term)
  search_result = Venue.query.filter(Venue.name.like(search)).all()
  
  data = []

  for searching in search_result:
    data.append({
      "id": searching.id,
      "name": searching.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id==searching.id).filter(Show.start_time > datetime.now()).all())
      
    })

  response={
    "count": len(search_result),
    "data":data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venues = Venue.query.get(venue_id)

  if not venues: 
    return render_template('errors/404.html')

  past_shows_data = db.session.query(Show).join(Artist).filter(Show.artist_id==venue_id).filter(Show.start_time<datetime.now())
  past_shows = []
  upcoming_shows_data = db.session.query(Show).join(Artist).filter(Show.artist_id==venue_id).filter(Show.start_time>datetime.now())
  
  upcoming_shows = []
  upcoming_shows_count = len(upcoming_shows)

  for shows in past_shows_data:
    past_shows.append({
      "artist_id": shows.artist_id,
      "artist_name": shows.artist.name,
      "artist_image_link": shows.artist.image_link,
      "start_time": shows.start_time.strftime("%Y-%m-%d %H:%M:%S")  
    })

  for shows in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id": shows.artist_id,
      "artist_name": shows.artist.name,
      "artist_image_link": shows.artist.image_link,
      "start_time": shows.start_time.strftime("%Y-%m-%d %H:%M:%S") 
    })

  data =({
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  })

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False
  
  try: 
      name = request.form.get("name")
      genres = request.form.getlist("genres")
      city = request.form.get("city")
      state = request.form.get("state") 
      address = request.form.get("address")
      phone = request.form.get("phone") 
      image_link = request.form.get("image_link")
      facebook_link = request.form.get("facebook_link") 
      website = request.form.get("website_link")
      seeking_talent = True if 'seeking_talent' in request.form else False 
      seeking_description = request.form.get("seeking_description")
 
      venue = Venue(name=name,genres=genres,city=city,state=state,address=address,phone=phone,image_link=image_link,facebook_link=facebook_link, website=website,seeking_talent=seeking_talent,seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()

  except:
    error = False
    db.session.rollback()

  finally:
    db.session.close()

  if error: 
    flash('An error occurred while submitting the venue form!!! ')
  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE','GET'])
def delete_venue(venue_id):

  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    flash (f"Could not delete record")

  finally:
    db.session.close()

  if error:
    (f"Could not delete record")
  if not error:
    (f"Record successfully deleted")
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get("search_term","")
  search = "%{0}%".format(search_term)
  search_result = Artist.query.filter(Artist.name.like(search)).all()
  
  data = []

  for searching in search_result:
    data.append({
      "id": searching.id,
      "name": searching.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id==searching.id).filter(Show.start_time > datetime.now()).all())
      
    })

  response={
    "count": len(search_result),
    "data":data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
  artist_query = db.session.query(Artist).get(artist_id)

  if not artist_query: 
    return render_template('errors/404.html')

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  error = False
  try:
    artist = Artist.query.get(artist_id)

    #if not venue:
    artist.name = request.form.get("name","")
    artist.genres = request.form.get("genres","genres")
    artist.city = request.form.get("city","")
    artist.state = request.form.get("state","")
    artist.phone = request.form.get("phone","")
    artist.image_link = request.form.get("image_link","")
    artist.facebook_link = request.form.get("facebook_link","")
    artist.website = request.form.get("website","")
    artist.seeking_venue = request.form.get("seeking_venue","")
    artist.seeking_description = request.form.get("seeking_description","")
  
    db.session.commit()
  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone 
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False
  
  venue = Venue.query.get(venue_id)

  #if not venue:

  venue.name = request.form.get("name","")
  venue.genres = request.form.get("genres","genres")
  venue.city = request.form.get("city","")
  venue.state = request.form.get("state","")
  venue.address = request.form.get("address","")
  venue.phone = request.form.get("phone","")
  venue.image_link = request.form.get("image_link","")
  venue.facebook_link = request.form.get("facebook_link","")
  venue.website_link = request.form.get("website_link","")
  venue.seeking_talent = request.form.get("seeking_talent","")
  venue.seeking_description = request.form.get("seeking_description","")
 
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  try:
      name = request.form.get("name")
      city = request.form.get("city")
      state = request.form.get("state")
      phone = request.form.get("phone")
      genres = request.form.getlist("genres")
      image_link = request.form.get("image_link")
      facebook_link = request.form.get("facebook_link")
      website = request.form.get("website_link")
      seeking_venue = True if "seeking_venue" in request.form else False
      seeking_description = request.form.get("seeking_description")
      
      artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website=website,seeking_venue=seeking_venue,seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()

  except:
      error = True
      db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occured while submitting the form')
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  show_data_all = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  for show_data in show_data_all:
    data.append({
      "venue_id": show_data.venue_id,
      "venue_name": show_data.venue.name,
      "artist_id": show_data.artist_id,
      "artist_name": show_data.artist.name,
      "artist_image_link": show_data.artist.image_link,
      "start_time": show_data.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = true

  try:
    venue_id = request.form.get("venue_id")
    artist_id = request.form.get("artist_id")
    start_time = request.form.get("start_time")

    show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()

  except:
    error: false
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occured while submitting the form')
  if not error:
    flash('Show was successfully listed!')
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
