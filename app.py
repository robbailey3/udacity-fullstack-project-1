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
import phonenumbers
from logging import Formatter, FileHandler
from flask_wtf import Form
from wtforms import ValidationError
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from forms import *
from models import Artist, Show, Venue, app, db

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if(isinstance(value, str)):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


def phone_validator(num):
    parsed = phonenumbers.parse(num, "US")
    if not phonenumbers.is_valid_number(parsed):
        raise ValidationError('Must be a valid US phone number.')


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
    data = []
    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()

    for venue in venues:
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": 1
            }]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    venues = Venue.query.filter(Venue.name.ilike(
        '%' + request.form['search_term'] + '%'))

    response = {
        "count": len(list(venues)),
        "data": list(venues)
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

    future_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    venue = venue.__dict__
    venue['past_shows'] = past_shows
    venue['past_shows_count'] = len(past_shows)
    venue['upcoming_shows'] = future_shows
    venue['upcoming_shows_count'] = len(future_shows)

    return render_template('pages/show_venue.html', venue=venue)

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
    try:
        form = VenueForm()
        name = form.name.data
        genres = form.genres.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        phone_validator(phone)
        website = form.website.data
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        seeking_description = form.seeking_description.data

        venue = Venue(name=name, genres=genres, city=city, state=state, address=address, phone=phone, website=website,
                      image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except ValidationError as e:
        # catch validation error from phone, rollback changes

        db.session.rollback()
        flash('The phone number was invalid. Venue ' +
              request.form['name'] + ' could not be added. ' + str(e))

    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be added.')

    finally:
        db.session.close()

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
        flash('Venue successfully deleted')
    except Exception as err:
        db.session.rollback()
        print('delete failed')
        print(str(err))
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artists = Artist.query.filter(Artist.name.ilike(
        '%' + request.form['search_term'] + '%'))

    response = {
        "count": len(list(artists)),
        "data": list(artists)
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist = Artist.query.filter_by(id=artist_id).first()
    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

    future_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    artist = artist.__dict__
    artist['past_shows'] = past_shows
    artist['past_shows_count'] = len(past_shows)
    artist['upcoming_shows'] = future_shows
    artist['upcoming_shows_count'] = len(future_shows)

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.filter_by(id=artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.filter(Artist.id == artist_id).first()

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        # check the phone number is a valid US number
        phone_validator(form.phone.data)
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.image_link = form.image_link.data
        artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        artist.seeking_description = form.seeking_description.data

        # add new artist and commit session
        db.session.commit()

        # flash message if successful
        flash('Artist ' + request.form['name'] + ' was updated successfully!')
    except ValidationError as e:
        # catch validation error from phone, rollback changes

        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated. ' + str(e))

    except Exception as err:
        # catch any other exceptions
        db.session.rollback()
        flash('An unknown error occurred. Artist ' +
              request.form['name'] + ' could not be updated. ' + str(err))
    finally:
        # always close the session
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        venue = Venue.query.filter(Venue.id == venue_id).first()

        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        phone_validator(form.phone.data)
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    except ValidationError as e:
        # catch validation error from phone, rollback changes

        db.session.rollback()
        flash('The phone number was invalid. Venue ' +
              request.form['name'] + ' could not be amended. ' + str(e))

    except Exception as err:
        print(err)
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be amended.')

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
    try:
        form = ArtistForm()
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        # check the phone number is valid
        phone_validator(phone)
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        website = form.website.data
        image_link = form.image_link.data
        seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        seeking_description = form.seeking_description.data

        # create new artist from form data
        artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres, facebook_link=facebook_link,
                        website=website, image_link=image_link,
                        seeking_venue=seeking_venue,
                        seeking_description=seeking_description)

        # add new artist and commit session
        db.session.add(artist)
        db.session.commit()

        # flash message if successful
        flash('Artist ' + request.form['name'] + ' was added successfully!')
    except ValidationError as e:
        # catch validation error from phone, rollback changes

        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be added. ' + str(e))
    except:
        # catch any other exceptions
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be added.')
    finally:
        # always close the session
        db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows

    data = Show.query.options(db.joinedload(
        Show.Venue), db.joinedload(Show.Artist)).all()
    data = list(map(Show.detail, data))
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
    try:
        form = ShowForm()
        venue_id = form.venue_id.data
        artist_id = form.artist_id.data
        start_time = form.start_time.data

        show = Show(venue_id=venue_id, artist_id=artist_id,
                    start_time=start_time)

        db.session.add(show)
        db.session.commit()
        flash('Show successfully added')

    except:
        flash('Ooops, looks like an error occured')
        db.session.rollback()
    finally:
        db.session.close()

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
