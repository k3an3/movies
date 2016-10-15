import requests
import subprocess
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


def add_movie(movie_title, year="", depth=0):
    url = IMDB_API_URL + '&t={}&y='.format(movie_title, year)
    r = requests.get(url).json()
    if r.get('Response') == 'False':
        depth += 1
        if depth < 3:
            return True, add_movie(custom_google_search(movie_title + " " + year, "add"), depth=depth)
        return False, custom_google_search(movie_title + " " + year)
    try:
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
    with open(filename) as f:
        genre = ""
        not_added = []
        for line in f:
            if line[0] == '#':
                genre = line[1:]
            else:
                s, m = add_movie(line)
                if not s:
                    not_added.append(m)
                else:
                    print(m)
    for m in not_added:
        print(m)


def get_genres():
    genres = []
    for movie in Movie.select():
        for genre in movie.genre.split(', '):
            if genre not in genres:
                genres.append(genre)


def update():
    subprocess.call(['git', 'pull', 'origin', 'master'])
    subprocess.call(['/srv/movies/env/bin/pip', 'install', '-r', 'requirements.txt', '--upgrade'])
    subprocess.call(['sudo', 'systemctl', 'restart', 'movies'])
