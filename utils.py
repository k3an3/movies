import requests
from peewee import IntegrityError

from config import GOOGLE_API_KEY, GOOGLE_CX, IMDB_API_URL
from models import Movie


def help_text():
    return {'text': "Invalid command. The following commands are recognized:\n",
            'attachments': [{
                'text': ("_choose [category]_ - Select a random movie in the given category. "
                         "To pick from all categories, no extra argument is necessary.\n"
                         "_watched [movie]_ - Mark a movie as watched. "
                         "This will prevent it from being selected again.\n"
                         "_add [movie]_ [-y year] - Add a movie to the list that you'd like to watch in the future.\n"
                         )
            }]
            }


def add_movie(movie_title, year=""):
    url = IMDB_API_URL + '&t={}&y='.format(movie_title, year)
    r = requests.get(url).json()
    if r.get('Response') == 'False':
        return False, ("Oops, couldn't get an exact hit. Check your spelling and try again. Does this help?"
                       "{}").format(custom_google_search(movie_title + " " + year))
    try:
        return True, Movie.create(name=r['Title'], genre=r['Genre'], imdb_id=r['imdbID'])
    except IntegrityError:
        return False, "This movie has already been added!"


def custom_google_search(query):
    url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}'.format(
        GOOGLE_API_KEY, GOOGLE_CX, query
    )
    r = requests.get(url).json()
    response = ""
    if r.get('items'):
        for item in r['items'][:3]:
            response += "{} -- {}".format(item.get('title'), item.get('snippet'))
    else:
        response = "Please try refining your search to make sure that you aren't crazy."
    return response
