from functools import wraps

from flask import Flask, request, abort
from peewee import fn

from config import SLACK_TOKEN, SUPPORTED_COMMANDS, DEBUG
from models import db_init, Movie, db
from utils import help_text, add_movie

app = Flask(__name__)


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.form.get('token')
        if not token == SLACK_TOKEN:
            abort(401)
            return f(*args, **kwargs)

    return decorated_function


@auth_required
@app.route("/command", methods=['POST'])
def index():
    text = request.form.get('text')
    if not text:
        return '', 400
    args = text.split()
    # Check if we know about this command
    if len(args) == 0 or args[0] not in SUPPORTED_COMMANDS:
        return help_text()
    if args[0] == 'add':
        success, m = add_movie(' '.join(args[1:]))
        if success:
            return "Added: " + m.get_details()
        return m

    elif args[0] == 'choose':
        if len(args) == 1:
            random = Movie.select().order_by(fn.Random())
        else:
            random = Movie.filter(Movie.genre.lower() == ' '.join(args[1:]).lower())
        return random.get().get_details()
    elif args[0] == 'watched':
        try:
            movie = Movie.get(Movie.name.lower() == ' '.join(args[1:]).lower())
        except Movie.DoesNotExist:
            return "Sorry, I couldn't find that movie."
        movie.watched = True
        movie.save()
        return "Marked {} as watched".format(movie.name)
    return ""


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


if __name__ == "__main__":
    app.debug = DEBUG
    db_init()
    app.run()
