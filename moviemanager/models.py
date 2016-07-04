from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Text, Table, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy_utils import URLType, ScalarListType
from sqlalchemy_utils.functions import create_database, database_exists
from sqlalchemy_utils.listeners import force_auto_coercion, force_instant_defaults

from moviemanager import settings
from utils import Numeric

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

engine = create_engine('sqlite:///%s.db'%(settings.DBNAME))
if settings.DEBUG:
    engine.echo = True

if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.bind = engine
Base.metadata.create_all()
DBSession.configure(bind=engine)
