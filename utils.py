import requests

from config import GOOGLE_API_KEY, GOOGLE_CX, IMDB_API_URL
from models import Movie


def help_text():
    return """
    Invalid command. The following commands are recognized:
    _choose [category]_ - Select a random movie in the given category. To pick from all categories, no extra argument is necessary.
    _watched [movie]_ - Mark a movie as watched. This will prevent it from being selected again.
    _add [movie]_ [-y year] - Add a movie to the list that you'd like to watch in the future.
    """


def add_movie(movie_title, year=""):
    url = IMDB_API_URL + '&t={}&y='.format(movie_title, year)
    r = requests.get(url).json()
    if r.get('Response') == 'False':
        print("ombdapi failed, falling back to Google")
        return """
        Oops, couldn't get an exact hit. Check your spelling and try again. Does this help?
        {}""".format(custom_google_search(movie_title + " " + year))
    return Movie.create(name=r['Title'], genre=r['Genre'], imdb_id=r['imdbID'])


def custom_google_search(query):
    url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}'.format(
        GOOGLE_API_KEY, GOOGLE_CX, query
    )
    r = requests.get(url).json()
    response = ""
    for item in r['items'][:3]:
        response += "{} -- {}".format(item.get('title'), item.get('snippet'))
        print(item.get('htmlTitle'), item.get('snippet'))
