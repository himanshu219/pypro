import copy
import ctypes
import os
import sqlite3
import traceback

from decimal import Decimal
from types import FunctionType

from pymediainfo import MediaInfo
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Text, Table, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
# from sqlalchemy.sql import functions as func
from sqlalchemy.sql import func
from sqlalchemy_utils import URLType, ChoiceType, ScalarListType
from sqlalchemy_utils.functions import create_database, database_exists
from sqlalchemy_utils.listeners import force_auto_coercion, force_instant_defaults
from scripts.utils import Numeric
import datetime
force_auto_coercion()
force_instant_defaults()

DBSession = scoped_session(sessionmaker())

class BaseMixin(object):
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=BaseMixin)


genre_movie_map = Table('genre_movie_map', Base.metadata,
                         Column('movie_id', ForeignKey('movies.id'), primary_key=True),
                         Column('genre_id', ForeignKey('genre.id'), primary_key=True)
)

class Genre(Base):

    name = Column(String(50), nullable=False, unique=True)
    movies = relationship('Movies', secondary=genre_movie_map, back_populates='genres')

    def __init__(self, name):
        self.name = name

person_movie_map = Table('person_movie_map', Base.metadata,
                         Column('movie_id', ForeignKey('movies.id'), primary_key=True),
                         Column('person_id', ForeignKey('person.id'), primary_key=True)
                         )


class Person(Base):
    PROFESSION_TYPES = [
        (u'director', u'Director'),
        (u'writer', u'Writer'),
        (u'actor', u'Actor')
    ]

    name = Column(String(50), nullable=False, unique=False)
    profession_type =  Column(String(50), nullable=False)

    __table_args__ = (UniqueConstraint('name', 'profession_type', name='_name_prof_type_uc'),)
    __mapper_args__ = {
        'polymorphic_on': profession_type,
        'polymorphic_identity': 'person',
        'with_polymorphic':'*'
    }


class Director(Person):
    __tablename__ = None
    movies = relationship('Movies', secondary=person_movie_map, back_populates='directors')

    __mapper_args__ = {
        'polymorphic_identity':'director'
    }

    def __init__(self, name):
        self.name = name
        self.profession_type = self.PROFESSION_TYPES[0][0]


class Writer(Person):
    __tablename__ = None
    movies = relationship('Movies', secondary=person_movie_map, back_populates='writers')

    __mapper_args__ = {
        'polymorphic_identity':'writer'
    }

    def __init__(self, name):
        self.name = name
        self.profession_type = self.PROFESSION_TYPES[1][0]

class Actor(Person):
    __tablename__ = None
    movies = relationship('Movies', secondary=person_movie_map, back_populates='actors')

    __mapper_args__ = {
        'polymorphic_identity':'actor'
    }

    def __init__(self, name):
        self.name = name
        self.profession_type = self.PROFESSION_TYPES[2][0]

'''
3 types of inheritance possible
1st base class and derived class table separate with fk of base class in  derived class derived class will contain joined attributes of base class also
2nd only base class table exists table name missing from derived classes
3rd all have separate tables with concrete inheritance
'''

class Movies(Base):

    title = Column(String(250), nullable=False)
    released_date = Column(Date, nullable=False) #convert in dateformat 26 feb year
    rating = Column(Numeric(2,2), nullable=False) #convert in decimal
    rated = Column(String(50))
    metascore = Column(Integer, nullable=False)
    votes = Column(Integer, nullable=False)
    imdbid = Column(String(50), unique=True)
    entertainment_type = Column(String(100), nullable=False)
    runtime = Column(Integer, nullable=False) #convert in min
    poster_url = Column(URLType)
    description = Column(Text())
    awards = Column(String(500))
    language = Column(ScalarListType()) #convert to list
    country = Column(String(250))
    genres = relationship('Genre', secondary=genre_movie_map, back_populates='movies')
    directors = relationship('Director', secondary=person_movie_map, back_populates='movies')
    writers = relationship('Writer', secondary=person_movie_map, back_populates='movies')
    actors = relationship('Actor', secondary=person_movie_map, back_populates='movies')
    is_watched = Column(Boolean, unique=False, default=False)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    file_path = Column(String(250), nullable=False)
    file_name = Column(String(250), nullable=False)
    file_size = Column(Float, nullable=False)
    format = Column(String(50), nullable=False)

engine = create_engine('sqlite:///entertainment.db')
engine.echo = True

if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.bind = engine
Base.metadata.create_all()
DBSession.configure(bind=engine)


class GetMovieDataMixin(object):
    '''prompt for movies to add,
     automatic movie name normalize
     and (edit distance)similar movies prompt,
     move and rename movies,
         ask have u watched,
         optimize previously added movies using __bak
     add serials and episodes support
     add csv upload and download support with angular js frontend and server
     add update functionality with cron folder lookup
     poster download
     '''
    def __init__(self,data):
        self.data = copy.deepcopy(data)
        self.exclude_fields = ['Response', 'Year']
        self.header_mapping = {'Plot': 'description', 'Rated': 'rated',
                        'Language':'language', 'Title':'title', 'Country':'country',
                        'Writer':'writers', 'Metascore':'metascore', 'imdbRating':'rating',
                        'Director':'directors','Released':'released_date', 'Actors':'actors',
                        'Genre':'genres', 'Awards':'awards', 'Runtime':'runtime',
                        'Type':'entertainment_type', 'Poster':'poster_url', 'imdbVotes':'votes', 'imdbID':'imdbid'}


    def get_data(self):
        headers = []
        row = ()
        status = False
        try:
            self.exclude_data(self.data, self.exclude_fields)
            self.map_header(self.data, self.header_mapping)
            self.update_data(self.data)
            if self.is_exists(Movies,imdbid=self.data.get('imdbid')):
                print self.data
                ifyes = raw_input('Do u want to include this movie(): ')
                if ifyes == 'n':
                    return headers,row,False
        except Exception as e:
            print "Error in transforming data: %s"%(traceback.format_exc()),self.data
            return headers,row,status

        for k,v in self.data.items():
            headers.append(k)
            row = row + (v,)
        status = True
        return headers,row,status

    def _get_writers(self, v):
        list_of_writers = [self.get_or_create(Writer,name=name) for name in v.split(',')]
        return list_of_writers

    def _get_directors(self, v):
        list_of_directors = [self.get_or_create(Director,name=name) for name in v.split(',')]
        return list_of_directors

    def _get_actors(self, v):
        list_of_actors = [self.get_or_create(Actor,name=name) for name in v.split(',')]
        return list_of_actors

    def _get_genres(self, v):
        list_of_genres = [self.get_or_create(Genre,name=name) for name in v.split(',')]
        return list_of_genres

    def _get_metascore(self, v):
        try:
            metascore = int(v)
        except ValueError:
            metascore = -1
        return metascore

    def _get_language(self, v):
        return v.split(',')

    def _get_rating(self, v):
        return Decimal(v)

    def _get_released_date(self, v):
        return datetime.datetime.strptime(v, "%d %b %Y").date()

    def _get_votes(self, v):
        return int(v.replace(',',''))

    def _get_runtime(self, v):
        v = v.split()
        if 'hour' in v:
            return int(v[0])*60
        return int(v[0])

    @classmethod
    def update_data(cls, data):
        update_fields = {k.split('_get_')[1]: v for k, v in cls.__dict__.items() if type(v) == FunctionType and k.startswith('_get_') == True}
        for k,func in update_fields.items():
            data[k] = func(cls, data[k])

    @classmethod
    def map_header(cls, data, header_mapping):
        for k,v in header_mapping.items():
            data[v] = data[k]
            del data[k]

    @classmethod
    def exclude_data(cls, data, exclude_fields):
        for k in exclude_fields:
            del data[k]

    @classmethod
    def get_or_create(cls, model, session=DBSession, **kwargs):
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            return instance

    @classmethod
    def is_exists(cls,model,session=DBSession, **kwargs):
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return True
        else:
            return False

class Rows(object):
    def __init__(self, header, rows):
        self.header = header
        self.rows = rows

    def commit(self, model, session=DBSession, commiter=DBSession):
        header = self.header
        try:
            for row in self.rows:
                o = model(**dict(zip(header, row)))
                session.add(o)
            commiter.commit()
        except:
            commiter.rollback()
            print "Error in saving data: %s"%(traceback.format_exc()),self.rows

def get_data_from_url(url):
    import requests
    from requests.packages.urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    s = requests.Session()

    retries = Retry(total=5,
                    backoff_factor=0.,
                    status_forcelist=[ 500, 502, 503, 504 ])

    s.mount('http://', HTTPAdapter(max_retries=retries))
    try:
        print 'Fetching Movie from IMDB'
        resp = s.get(url)
        if resp.ok:
            return resp.json()
        else:
            return {}
    except Exception as e:
        print "Error in %s: %s"%(url, traceback.format_exc())

def get_data_from_files(allfiles):
    for filepath in allfiles:
        file_size = os.path.getsize(filepath)/(1024*1024.0)
        file_name,format = os.path.basename(filepath).rsplit('.', 1)
        data = {'file_name':file_name,'file_size':file_size,'format':format,'file_path':filepath}
        search_url = 'http://www.omdbapi.com/?r=json&s=%s'
        movies = get_data_from_url(search_url%(file_name))
        while (not(movies and movies.get('Search') and movies.get('Response') == "True")):
            ifyes = raw_input('Do u want to include this movie(%s): '%(file_name))
            if ifyes == 'n':
                return
            file_name = raw_input('Enter movie: ')
            movies = get_data_from_url(search_url%(file_name))

        movie = movies.get('Search')[0]
        get_url = 'http://www.omdbapi.com/?r=json&i='+str(movie.get('imdbID', ''))
        movie = get_data_from_url(get_url)
        if movie and movie.get('Response','') == "True":
            data.update(movie)
            headers,row,status = GetMovieDataMixin(data).get_data()
            if status:
                row_obj=Rows(headers,[row])
                row_obj.commit(Movies)
                print '%s movie successfully added'%data['title']
            else:
                print '%s MOVIE NOT ADDED' % data['title']
        else:
            print "Not Found: %s",get_url
        # else:
        #     print "Not Found: %s", search_url

def test():
    print 'Running Test Cases'
    data = {"Title": "Shutter Island", "Year": "2010", "Rated": "R", "Released": "19 Feb 2010", "Runtime": "138 min",
            "Genre": "Mystery, Thriller", "Director": "Martin Scorsese",
            "Writer": "Laeta Kalogridis (screenplay), Dennis Lehane (novel)",
            "Actors": "Leonardo DiCaprio, Mark Ruffalo, Ben Kingsley, Max von Sydow",
            "Plot": "A U.S Marshal investigates the disappearance of a murderess who escaped from a hospital for the criminally insane.",
            "Language": "English, German", "Country": "USA", "Awards": "8 wins & 59 nominations.",
            "Poster": "http://ia.media-imdb.com/images/M/MV5BMTMxMTIyNzMxMV5BMl5BanBnXkFtZTcwOTc4OTI3Mg@@._V1_SX300.jpg",
            "Metascore": "63", "imdbRating": "8.1", "imdbVotes": "771,547", "imdbID": "tt1130884", "Type": "movie",
            "Response": "True",'file_name':'shutter island.mkv','file_size':1000000L/(1024*1024.0),'format':'MKV',
            'file_path':'/home/Darkknight/Downloads/shutter island.mkv'}

    headers, row, status = GetMovieDataMixin(data).get_data()
    row_obj = Rows(headers, [row])
    row_obj.commit(Movies)


def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.') or has_hidden_attribute(filepath)

def has_hidden_attribute(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result

def is_video(filepath):
    media_info = MediaInfo.parse(filepath)
    for track in media_info.tracks:
        if track.track_type == 'Video':
            return True
    return False

def has_size(filepath, szlimit):
    size = os.path.getsize(filepath) / (1024 * 1024.0)
    if size > szlimit:
        return True
    else:
        return False

def is_prev_added(filepath):
    name = os.path.basename(os.path.abspath(filepath)).rsplit('.',1)[0]
    return name.endswith('__bak')


def main():
    # test()
    VIDEO_DIR='/home/darkknight/Downloads/'
    #exclude hidden folders and include mp4 files
    import os
    for root, dirs, files in os.walk(VIDEO_DIR, topdown=True):
        allfiles = [os.path.join(root, name) for name in files if not is_hidden(os.path.join(root, name)) and is_video(os.path.join(root, name)) and has_size(os.path.join(root, name),700)]
        get_data_from_files(allfiles)




if __name__ == '__main__':
    main()