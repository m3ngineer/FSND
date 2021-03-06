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
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
# moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    show = db.relationship('Show', backref='Venue', lazy=True, cascade='delete')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='Artist', lazy=True, cascade='delete')


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.String(), db.ForeignKey('Venue.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

@app.route('/db')
def create_db_exampes():

    newVenue = Venue(id = 1,
                    name = 'The Musical Hop',
                    genres = '["Jazz", "Reggae", "Swing", "Classical", "Folk"]',
                    city = 'San Francisco',
                    state = 'CA',
                    address = '1015 Folsom Street',
                    phone = '123-123-1234',
                    website = 'https://www.themusicalhop.com',
                    facebook_link = 'https://www.facebook.com/TheMusicalHop',
                    seeking_talent = True,
                    seeking_description = 'We are on the lookout for a local artist to play every two weeks. Please call us.',
                    image_link = 'https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
                    )

    db.session.add(newVenue)
    # db.session.commit()

    newVenue = Venue(id = 2,
                    name = 'The Dueling Pianos Bar',
                    genres = '["Classical", "R&B", "Hip-Hop"]',
                    city = 'New York',
                    state = 'NY',
                    address = '335 Delancey Street',
                    phone = '914-003-1132',
                    website = 'https://www.theduelingpianos.com',
                    facebook_link = 'https://www.facebook.com/theduelingpianos',
                    seeking_talent = False,
                    seeking_description = 'We are on the lookout for a local artist to play every two weeks. Please call us.',
                    image_link = 'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80',
                    )
    db.session.add(newVenue)
    # db.session.commit()

    print('Venue inserted.')

    return 'Venue table successfully created.'

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    ''' Displays list of venues '''

    now = datetime.now()

    venues = Venue.query. \
        join(Show, Show.venue_id == Venue.id, isouter=True).all()

    print([v for v in venues])

    venue_cities = Venue.query.with_entities(Venue.city, Venue.state).distinct()
    venue_cities = [city_state for city_state in venue_cities]
    data = [{'city_state': city_state[0] + ', ' + city_state[1],
            'city': city_state[0],
            'state': city_state[1],
            'venues': []
            } for city_state in venue_cities]

    for venue in venues:
        city_state = venue.city + ', ' + venue.state
        for city_data in data:
            if city_data['city_state'] == city_state:
              venue_data = {
                            'id': venue.id,
                            'name': venue.name,
                            'num_upcoming_shows': [show for show in venue.show if datetime.strptime(str(show.start_time), '%Y-%m-%d %H:%M:%S') > now],
                            }
              city_data['venues'].append(venue_data)

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    print(request.form.get('search_term', ''))

    now = datetime.now()

    venues =  Venue.query. \
                join(Show, Show.venue_id == Venue.id, isouter=True). \
                filter(Venue.name.contains(request.form.get('search_term', '')))

    response = {'data': [], 'count': len([v for v in venues])}
    for venue in venues:
      response['data'].append({
        'count': len([v for v in venues]),
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': [show for show in venue.show if datetime.strptime(str(show.start_time), '%Y-%m-%d %H:%M:%S') > now],
      })

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    ''' Shows the venue page with the given venue_id '''

    now = datetime.now()

    venue = Venue.query. \
        join(Show, Show.venue_id == Venue.id, isouter=True). \
        join(Artist, Artist.id == Show.artist_id, isouter=True). \
        filter_by(id=venue_id).one_or_none()

    if venue:
        for show in venue.show:
            print(venue.image_link)
            show.artist_image_link = show.Artist.image_link
            show.start_time = str(show.start_time)
        venue_data = {
                        'id': venue.id,
                        'name': venue.name,
                        'genres': venue.genres[1:-1].replace('"', '').split(', '),
                        'address': venue.address,
                        'city': venue.city,
                        'state': venue.state,
                        'phone': venue.phone,
                        'website': venue.website,
                        'facebook_link': venue.facebook_link,
                        'seeking_talent': venue.seeking_talent,
                        'seeking_description': venue.seeking_description,
                        'image_link': venue.image_link,
                        'past_shows': [show for show in venue.show if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') <= now], # TODO
                        'upcoming_shows': [show for show in venue.show if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now], # TODO
                        'past_shows_count': len([show for show in venue.show if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') <= now]), # TODO
                        'upcoming_shows_count': len([show for show in venue.show if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now]), # TODO
                        }
    else:
        venue_data = {}

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

    return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
      newVenue = Venue(
                      name = request.form['name'],
                      genres = request.form['genres'],
                      city = request.form['city'],
                      state = request.form['state'],
                      address = request.form['address'],
                      phone = request.form['phone'],
                      website = request.form['website'],
                      facebook_link = request.form['facebook_link'],
                      seeking_talent = True if request.form['seeking_talent'] == 'Yes' else False,
                      seeking_description = request.form['seeking_description'],
                      image_link = request.form['image_link'],
                      )

      db.session.add(newVenue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
      print(e)
      flash('There was an error creating the venue ' + request.form['name'] + '!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    venue = Venue.query.get(venue_id).one_or_none()
    if venue:
        try:
            db.session.delete(venue)
            db.session.commit()

            flash('Venue with id ' + str(venue_id) + ' was successfully deleted!')

        except Exception as e:
            flash('There was an error deleting the venue with id ' + str(venue_id) + '!')

    else:
        flash('There was no venue with the id ' + str(venue_id) + ' found!')
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  print([a for a in artists])
  if artists:
      data = [{"id": artist.id, "name": artist.name} for artist in artists]
  else:
      data = []

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  now = datetime.now()

  artists =  Artist.query. \
    join(Show, Show.artist_id == Artist.id). \
    filter(Artist.name.contains(request.form.get('search_term', ''))).all()

  response = {'data': [], 'count': len([a for a in artists])}

  for artist in artists:
    response['data'].append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len([show for show in artist.show if show.start_time > now]),
    })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    ''' Shows the venue page with the given venue_id '''

    now = datetime.now()

    artist = Artist.query. \
        join(Show, Show.artist_id == Artist.id, isouter=True). \
        join(Venue, Venue.id == Show.venue_id, isouter=True). \
        filter_by(id=artist_id).one_or_none()

    if artist:
        for show in artist.show:
            print(show.Venue.image_link)
            show.venue_image_link = show.Venue.image_link
            show.start_time = show.start_time
        artist_data = {
                      'id': artist.id,
                      'name': artist.name,
                      'genres': artist.genres[1:-1].replace('"', '').split(', '),
                      'phone': artist.phone,
                      'website': artist.website,
                      'facebook_link': artist.facebook_link,
                      'seeking_venue': artist.seeking_venue,
                      'seeking_description': artist.seeking_description,
                      'image_link': artist.image_link,
                      'past_shows': [show for show in artist.show if show.start_time <= now], # TODO
                      'upcoming_shows': [show for show in artist.show if show.start_time > now], # TODO
                      'past_shows_count': len([show for show in artist.show if show.start_time <= now]), # TODO
                      'upcoming_shows_count': len([show for show in artist.show if show.start_time > now]), # TODO
                      }
    else:
        artist_data = {}


  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.filter_by(id=artist_id).one_or_none()

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    '''
    Take values from the form submitted, and update existing
    artist record with ID <artist_id> using the new attributes
    '''

    artist = Artist.query.filter_by(id=artist_id).one_or_none()

    if artist:
        try:
            artist.name = request.form['name']
            artist.genres = request.form['genres']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            artist.website = request.form['website']
            artist.facebook_link = request.form['facebook_link']
            artist.seeking_venue = True if request.form['seeking_venue'] == 'Yes' else False
            artist.seeking_description = request.form['seeking_description']
            artist.image_link = request.form['image_link']

            db.session.commit()

            flash('Artist with id ' + str(artist_id) + ' was successfully edited!')

        except Exception as e:
            flash('There was an error editing the artist with id ' + str(artist_id) + '!')

    else:
        flash('There was no artist with the id ' + str(artist_id) + '!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.filter_by(id=venue_id).one_or_none()

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    venue = Venue.query.filter_by(id=venue_id).one_or_none()

    if venue:
        try:
            venue.name = request.form['name']
            venue.genres = request.form['genres']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.phone = request.form['phone']
            venue.website = request.form['website']
            venue.facebook_link = request.form['facebook_link']
            venue.seeking_talent = True if request.form['seeking_talent'] == 'Yes' else False
            venue.seeking_description = request.form['seeking_description']
            venue.image_link = request.form['image_link']

            db.session.commit()

            flash('Venue with id ' + str(venue_id) + ' was successfully edited!')

        except Exception as e:
            flash('There was an error editing the venue with id ' + str(venue_id) + '!')

    else:
        flash('There was no venue with the id ' + str(venue_id) + '!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  '''
  Called upon submitting the new artist listing form
  '''

  try:
      newArtist = Artist(
                      name = request.form['name'],
                      genres = request.form['genres'],
                      city = request.form['city'],
                      state = request.form['state'],
                      phone = request.form['phone'],
                      website = request.form['website'],
                      facebook_link = request.form['facebook_link'],
                      seeking_venue = True if request.form['seeking_venue'] == 'Yes' else False,
                      seeking_description = request.form['seeking_description'],
                      image_link = request.form['image_link'],
                      )

      db.session.add(newArtist)
      db.session.commit()

      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except Exception as e:
      flash('There was an error creating the artist ' + request.form['name'] + '!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    ''' Displays list of shows at /shows '''

    shows = Show.query. \
        join(Venue, Venue.id == Show.venue_id). \
        join(Artist, Artist.id == Show.artist_id).all()

    data = []
    for show in shows:
        data.append({
        'venue_id': show.Venue.id,
        'venue_name': show.Venue.name,
        'artist_id': show.Artist.id,
        'artist_name': show.Artist.name,
        'artist_image_link': show.Artist.image_link,
        'start_time': str(show.start_time),
        })
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

        return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  '''
  Called to create new shows in the db, upon submitting new show listing form
  '''

  formatted_dt = datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S')
  try:
      newShow = Show(
                      artist_id = request.form['artist_id'],
                      venue_id = request.form['venue_id'],
                      start_time = formatted_dt,
                      )

      db.session.add(newShow)
      db.session.commit()

      flash('Show was successfully listed!')
  except Exception as e:
      flash('There was an error listing the show!')

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
