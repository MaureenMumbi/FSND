#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from alembic import op
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues=Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  data=[]
  
  venue_state_and_city = ''
  num_upcoming_shows= 0
  for v in venues:
   #filter upcoming shows given that the show start time is greater than the current time
   
    shows = Show.query.filter_by(venue_id=v.id).all()
    current_date = datetime.now()

    for show in shows:
      if show.start_time > current_date:
          num_upcoming_shows += 1

    # v.venue.filter(Show.start_time > current_time).all()
    if venue_state_and_city == v.city + v.state:
      data[len(data) - 1]["venues"].append({
        "id": v.id,
        "name":v.name,
        "num_upcoming_shows": num_upcoming_shows
       
      })
    else:
      venue_state_and_city == v.city + v.state
      data.append({
        "city":v.city,
        "state":v.state,
        "venues": [{
          "id": v.id,
          "name":v.name,
          "num_upcoming_shows":num_upcoming_shows
         
        }]
      })
   
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 
  term = request.form.get('search_term', '')
  venues= Venue.query.filter(Venue.name.ilike('%'+term+'%'))
  data = []
  for venue in venues:
    results= {
      'id': venue.id,
      'name':venue.name,
      'num_upcoming_shows':len(venue_upcoming_shows(venue.id)) 
    }
    data.append(results)

    response = {
      'count':venues.count(),
      'data': data

    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
 
  data ={
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city':venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent':venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': venue_past_shows(venue.id),
    'upcoming_shows': venue_upcoming_shows(venue.id),
    'past_shows_count': len(venue_past_shows(venue.id)),
    'upcoming_shows_count': len(venue_upcoming_shows(venue.id)),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    error=False
    form = VenueForm(request.form)
    try:
      venue = Venue(name=form.name.data,
                    city=form.city.data, 
                    state=form.state.data, 
                    address= form.address.data, 
                    phone=form.phone.data, 
                    genres=form.genres.data,
                    facebook_link= form.facebook_link.data,
                    image_link= form.image_link.data, 
                    website_link = form.website_link.data,
                    seeking_talent=form.seeking_talent.data,
                    seeking_description=form.seeking_description.data
                    ) 
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
     
    if error:
       flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
       flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
       # TODO: on unsuccessful db insert, flash an error instead.
       # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
       # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
       # on successful db insert, flash success
   

 
  

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # To delete venues 
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue {} deleted successfully'.format(venue.name))
  except:
    flash('Unable to delete Venue {}'.format(venue.name))
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # list our artists
  artist_data =Artist.query.all()
  data =[]
  for artist in artist_data:
        details = {
          'id':artist.id,
          'name':artist.name
        }
        data.append(details)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # searching artists with partial string search and case-insensitive.

  term = request.form.get('search_term', '')
  artists= Artist.query.filter(Artist.name.ilike('%'+term+'%'))
  data = []
  for artist in artists:
    results= {
      'id': artist.id,
      'name':artist.name,
      'num_upcoming_shows':len(artist_upcoming_shows(artist.id))
    }
    data.append(results)

    response = {
      'count':artists.count(),
      'data': data

    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  
  artist = Artist.query.filter_by(id=artist_id).one()
  data={
    'id': artist.id,
    'name': artist.name,
    'genres':artist.genres,
    'city': artist.city,
    'state':artist.state,
    'phone':artist.phone,
    'website':artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description':artist.seeking_description,
    'past_show': artist_past_shows(artist.id),
    'upcoming_shows':artist_upcoming_shows(artist.id),
    'past_shows_count':len(artist_past_shows(artist.id)),
    'upcoming_shows_count': len(artist_upcoming_shows(artist.id))
  }
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  #edit artist details 
  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  form = ArtistForm(request.form, meta={'csrf': False})
 
  if form.validate:
      try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.image_link = form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.website_link = form.website_link.data
            artist.seeking_venue= form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            print(artist)
            db.session.commit()
            flash("Artist {} is updated successfully".format(artist.name))
      except Exception as e:
          print(f'Error ==> {e}')
          db.session.rollback()
          flash("Error updating Artist {}".format(artist.name))
      finally:
          db.session.close()
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
        message = []
        for field, err in form.errors.items():
          message.append(field + ' ' + '|' .join(err))
          flash('Errors ' + str(message))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  #fetch venue details for editing 
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
 #submit edited venue data
  venue = db.session.query(Venue).filter_by(id = venue_id).first()
  form = VenueForm(request.form)
  
  if form.validate:
      try:
          venue.name = form.name.data
          venue.city = form.city.data
          venue.state = form.state.data
          venue.address = form.address.data
          venue.phone = form.phone.data
          venue.genres = form.genres.data
          venue.image_link =form.image_link.data
          venue.facebook_link = form.facebook_link.data
          venue.website_link = form.website_link.data
          venue.seeking_talent=form.seeking_talent.data
          venue.seeking_description = form.seeking_description.data
          db.session.commit()
          flash("Venue {} is updated successfully".format(venue.name))
      except ValueError as e:
          if app.debug:
              print(e)
          db.session.rollback()
          flash("Error updating Venue {}".format(venue.name))
      finally:
          db.session.close()
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
        message = []
        for field, err in form.errors.items():
          message.append(field + ' ' + '|' .join(err))
          print(str(message))
          flash('Errors ' + str(message))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
      error =False
      form = ArtistForm(request.form)
      try:
        artist = Artist(name=form.name.data,
                        city=form.city.data, 
                        state=form.state.data,
                        phone=form.phone.data,
                        genres=form.genres.data,
                        image_link= form.image_link.data,
                        facebook_link = form.facebook_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data,
                        website_link= form.website_link.data
                        ) 
        db.session.add(artist)
        db.session.commit()
      except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
      finally:
        db.session.close()
      if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows 
  data =[]
  shows = Show.query.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    venue_data= {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    }
    data.append(venue_data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

    error=False
    try:
      show = ShowForm(request.form)
      start_time = show.start_time.data,
      venue_id = show.venue_id.data,
      artist_id = show.artist_id.data,
      show = Show(start_time = start_time, venue_id = venue_id, artist_id=artist_id)
      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
       # on successful db insert, flash success
       flash('Show was successfully listed!')
    else:
       flash('An error occurred. Show could not be listed.')
 
    return render_template('pages/home.html')

# Additional Functions
def artist_past_shows(id):
#  get the past shows of an artist
  shows =  db.session.query(Artist, Show).join(Show).join(Venue).filter(
                                                                             Show.artist_id == id,
                                                                             Show.venue_id == Venue.id,
                                                                             Show.start_time < datetime.now()).all()
  past_shows=[]
  for venue, show in shows:
      showdata = {  
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": format_datetime(str(show.start_time))
        }
      past_shows.append(showdata)
     
  return past_shows

def artist_upcoming_shows(id):
#  get the upcoming shows of an artist
  shows =  db.session.query(Artist, Show).join(Show).join(Venue).filter(
                                                                             Show.artist_id == id,
                                                                             Show.venue_id == Venue.id,
                                                                             Show.start_time > datetime.now()).all()
 

  upcoming_shows=[]
  for venue, show in shows:
      showdata={ 
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": format_datetime(str(show.start_time))
        }
      upcoming_shows.append(showdata)
      
  return upcoming_shows

def venue_past_shows(id):
  #  get the upcoming shows of a venue
  shows =  db.session.query(Artist, Show).join(Show).join(Venue).filter(
                                                                             Show.venue_id == id,
                                                                             Show.artist_id == Artist.id,
                                                                             Show.start_time < datetime.now()).all()
  
  past_shows=[]
  for artist, show in shows:
    showdata= { 
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
    past_shows.append(showdata)
  return past_shows

  

def venue_upcoming_shows(id):
#  get the upcoming shows of an venue
  shows =  db.session.query(Artist, Show).join(Show).join(Venue).filter(
                                                                             Show.venue_id == id,
                                                                             Show.artist_id == Artist.id,
                                                                             Show.start_time > datetime.now()).all()
 
  upcoming_shows=[]
  for artist, show in shows:
    showdata= { 
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
    upcoming_shows.append(showdata)
     
  return upcoming_shows


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


 