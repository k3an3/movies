import requests
from peewee import *

from config import DEBUG, IMDB_API_URL

if DEBUG:
    db = SqliteDatabase('app.db')
else:
    db = MySQLDatabase(host="localhost", database="movies", user="movies", passwd="changeme")


def db_init():
    db.connect()
    try:
        db.create_tables([Movie])
        print('Creating tables...')
    except OperationalError:
        pass
    db.close()


class BaseModel(Model):
    class Meta:
        database = db


class Movie(BaseModel):
    name = CharField(unique=True)
    genre = CharField()
    imdb_id = CharField(max_length=16)
    watched = BooleanField(default=False)

    def get_details(self):
        url = IMDB_API_URL + '&i={}'.format(self.imdb_id)
        r = requests.get(url).json()
        return """
        *{}* - _{}_
        _{}_
        {}""".format(r['Title'], r['Year'], r['Plot'], r.get('Poster', ''))