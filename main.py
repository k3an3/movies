import datetime
import json
import random
from functools import wraps

from flask import Flask, request, abort, Response, render_template
from peewee import fn

import config
from models import db_init, Movie, db
from utils import help_text, add_movie, update, reload, format_genres, get_genres, format_movies, movies_in_genre, \
    genres, get_netflix_id, VERSION

app = Flask(__name__)


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.form.get('token')
        if not token == config.SLACK_TOKEN:
            abort(401)
            return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    genre = request.args.get('genre')
    if genre and genre.lower() != "any":
        movie = movies_in_genre(genre).order_by(fn.Random()).get()
    else:
        movie = Movie.select().order_by(fn.Random()).get()
    r = movie.get_details(plot="full")
    title = r['attachments'][0]['title']
    link = r['attachments'][0]['title_link']
    description = r['attachments'][0]['text']
    image = r['attachments'][0]['image_url']
    netflix = get_netflix_id(title.split(' (')[0], title.split('(')[-1].split(')')[-2])
    saying = random.choice(config.SAYINGS)
    if not genres:
        get_genres()
    list_genres = ["Any"]
    list_genres.extend(sorted(genres))
    year = datetime.datetime.now().year
    version = VERSION
    return render_template("index.html", **locals())


@auth_required
@app.route("/command", methods=['POST'])
def command():
    text = request.form.get('text')
    if not text:
        return '', 400
    args = text.split()
    # Check if we know about this command
    if args[0] == 'add':
        success, m = add_movie(' '.join(args[1:]))
        if success:
            m = m.get_details()
            m['text'] = "Added movie:"
        return Response(json.dumps(m), mimetype='application/json')
    elif args[0] == 'choose':
        if len(args) == 1:
            rand = Movie.select().order_by(fn.Random())
        else:
            genre = ' '.join(args[1:])
            rand = movies_in_genre(genre).order_by(fn.Random())
        try:
            m = rand.get().get_details()
            m['text'] = random.choice(config.SAYINGS)
            return Response(json.dumps(m), mimetype='application/json')
        except Movie.DoesNotExist:
            return "No movies yet!"
    elif args[0] == 'watched':
        name = ' '.join(args[1:])
        try:
            movie = Movie.get(fn.Lower(Movie.name) == name.lower())
        except Movie.DoesNotExist:
            return "Sorry, I couldn't find that movie. You need to be exact."
        movie.watched = True
        movie.save()
        return "Marked _{}_ as watched".format(movie.name)
    elif args[0] == 'unwatch':
        # Undocumented commands
        name = ' '.join(args[1:])
        try:
            movie = Movie.get(fn.Lower(Movie.name) == name.lower())
        except Movie.DoesNotExist:
            return "Sorry, I couldn't find that movie. You need to be exact."
        movie.watched = False
        movie.save()
        return "Marked _{}_ as un-watched".format(movie.name)
    elif args[0] == 'list':
        data = {'text': "Must specify `movies` or `genres`."}
        if len(args) > 1:
            if args[1] == 'movies':
                if len(args) > 2:
                    data = format_movies(' '.join(args[2:]))
                else:
                    data = format_movies()
            elif args[1] == 'genres':
                data = format_genres()
        return Response(json.dumps(data), mimetype='application/json')
    # Management commands
    elif args[0] == 'refresh_genres':
        get_genres()
        return 'Done'
    elif args[0] == 'update':
        update()
        return '', 204
    elif args[0] == 'reload':
        reload()
        return '', 204
    return Response(json.dumps(help_text()), mimetype='application/json')


# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    db.connect()


# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


def add_header(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'" \
                                                  " https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.5/css" \
                                                  "/bootstrap.min.css; img-src * ;" \
                                                  "script-src https://code.jquery.com/jquery-3.1.1.min.js " \
                                                  "https://code.jquery.com/jquery-3.1.1.min.js "
    return response


if __name__ == "__main__":
    app.debug = config.DEBUG
    db_init()
    app.run()
