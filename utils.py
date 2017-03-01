import hashlib
import os
import subprocess

import requests
from peewee import IntegrityError

from config import GOOGLE_API_KEY, GOOGLE_CX, IMDB_API_URL
from models import Movie

genres = []
netflix_api_url = 'http://netflixroulette.net/api/api.php?'

try:
    VERSION = 'v' + subprocess.check_output(['git', 'describe', '--tags', 'HEAD']).decode('UTF-8')
except:
    VERSION = 'unknown'


def help_text():
    return {'text': "Invalid command. The following commands are recognized:\n",
            'attachments': [{
                'text': ("choose [category] - Select a random movie in the given category. "
                         "To pick from all categories, no extra argument is necessary.\n"
                         "watched [movie] - Mark a movie as watched. "
                         "This will prevent it from being selected again.\n"
                         "add [movie] - Add a movie to the list that you'd like to watch in the future.\n"
                         "list [movies|genres] - List all of the movies or genres that exist within the database."
                         )
            }]
            }


def add_movie(movie_title, year="", depth=0):
    url = IMDB_API_URL + '&t={}&y='.format(movie_title, year)
    r = requests.get(url).json()
    if r.get('Response') == 'False':
        depth += 1
        if depth < 3:
            return True, add_movie(custom_google_search(movie_title + " " + year, "add"), depth=depth)
        return False, custom_google_search(movie_title + " " + year)
    try:
        for genre in r['Genre'].split(', '):
            if genre not in genres:
                genres.append(genre)
        return True, Movie.create(name=r['Title'], genre=r['Genre'], imdb_id=r['imdbID'])
    except IntegrityError:
        return False, {'text': "This movie has already been added!"}


def custom_google_search(query, mode="search"):
    url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}'.format(
        GOOGLE_API_KEY, GOOGLE_CX, query
    )
    r = requests.get(url).json()
    if mode == "search":
        response = {'text': "Couldn't find an exact hit. Check your spelling and try again.",
                    'attachments': []
                    }
        if r.get('items'):
            for item in r['items'][:3]:
                response['attachments'].append({
                    'text': "{} -- {}".format(item.get('title'), item.get('snippet')),
                    'color': '#FF0000',
                })
        else:
            response = {'text': "Please try refining your search to make sure that you aren't crazy."}
    else:
        if r.get('items'):
            return r['items'][0].get('title').split(' -')[1]
        else:
            response = {'text': "Please try refining your search to make sure that you aren't crazy."}
    return response


def import_from_file(filename):
    """
    Read a file, one movie per line, and try to add each movie to the database
    :param filename:
    :return:
    """
    with open(filename) as f:
        not_added = []
        for line in f:
            if line[0] != '#':
                s, m = add_movie(line)
                if not s:
                    not_added.append(m)
                else:
                    print(m)
    for m in not_added:
        print(m)


def get_genres():
    for movie in Movie.select():
        for genre in movie.genre.split(', '):
            if genre not in genres:
                genres.append(genre)


def format_genres():
    if not genres:
        get_genres()
    text = ""
    for genre in sorted(genres):
        text += '{0}\n'.format(genre)
    result = {
        'text': 'The following genres are currently available:',
        'attachments': [{
            'color': '#001100',
            'text': text
        }]
    }
    return result


def movies_in_genre(genre):
    search = "%{}%".format(genre)
    return Movie.filter(Movie.genre ** search).order_by(Movie.name)


def format_movies(genre=None):
    text = ""
    if genre:
        movies = movies_in_genre(genre)
    else:
        movies = Movie.select().order_by(Movie.name)
    for movie in movies:
        text += '{0}{1}\n'.format(movie.name,
                                  ':heavy_check_mark:' if movie.watched else '')
    result = {
        'text': 'The following movies are currently available:',
        'attachments': [{
            'color': '#000011',
            'text': text
        }]
    }
    return result


def reload():
    subprocess.call(['sudo', 'systemctl', 'restart', 'movies'])


def update():
    subprocess.call(['git', 'stash'])
    subprocess.call(['git', 'pull', 'origin', 'master'])
    subprocess.call(['git', 'stash', 'apply'])
    subprocess.call(['/srv/movies/env/bin/pip', 'install', '-r', 'requirements.txt', '--upgrade'])
    reload()


def get_netflix_id(show_title, year=0):
    title = show_title
    title = title.replace(" ", "%20")
    payload = requests.get("{}title={}&year={}".format(netflix_api_url, title, year)).json()
    return payload.get('show_id')
