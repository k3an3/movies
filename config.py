import sys

DEBUG = False
IMDB_API_URL = 'http://www.omdbapi.com/?type=movie'
# Things to print with each random movie pick
SAYINGS = (
    "You should watch this movie:",
    "Whether you like it or not, this is what got picked:",
    "I see this movie in your future:",
    "Who is bringing the popcorn? I picked a movie:",
    "Let us see if this one receives a perfect rating (5/7):",
    "This movie isn't going to watch itself:",
    "Here's my suggestion:",
    "Here's an idea:",
    "Let's try something new (or not):",
    "If you were a movie, I'd pick you:",
    "It's movie night again!",
    "The weather outside may be frightful, so this movie should warm you up:",
    "Take a look-see:",
    "The result from our MOO-V algorithm:",
    "What, you don't have something more productive to do?",
    "No animals were harmed in the selection of this movie:",
    "At least somebody here is capable of making decisions:",
    "3 spooky 5 me:",
    "Hot off the presses:",
    "It's movie o'clock somewhere...",
    "Sit back and enjoy the show.",
    "Don't touch that dial!",
    "Now playing:",
    "You like movies; we've got 'em!",
    "No intermissions.",
    "Is the volume turned up loud enough?",
    "I smell popcorn...",
)

DB_USER = 'movies'
DB_PASS = 'changeme'

try:
    from config_local import *
except ImportError:
    print("`config_local.py` is missing! Copy `example-config_local.py` to get started.")
    sys.exit()
