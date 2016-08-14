import copy
import ctypes
import os
import traceback
import datetime
from decimal import Decimal

from pymediainfo import MediaInfo

from moviemanager import settings
from moviemanager.mixin import GetDataMixin, ModifyDataMixin, FetchAPIMixin, FileMixin
from moviemanager.models import Movies, Writer, Director, Actor, Genre, DBSession


class GetMovieDataMixin(GetDataMixin, ModifyDataMixin):
    '''  BLOCKERS
         move and rename movies and folders,
         ask have u watched, generic list func,create settings for watch
         optimize previously added movies using .movid
         add codec data dump and add owner with watched liked column
         add search google support/automatic movie name normalize/ and (edit distance)similar movies prompt,
     PENDING
     prompt for movies to add
     add serials and episodes support with wikipedia episodes
     add csv upload and download support with angular js frontend and server
     add analytics dashboard
     add update functionality with cron folder lookup
     poster download
     add data functionality in datamixin
     configure logging and add all summary in main
     add torrent
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
                print 'Duplicate Movie %s'%(self.data['title'])
                if settings.ADD_DUPLICATE_PROMPT:
                    print self.data
                    ifyes = raw_input('Movie Already exists do u want to include this movie(%s): '%(self.data['title']))
                    if ifyes == 'n':
                        return headers,row,False
                    else:
                        newimdbid=raw_input('Enter Movie id: ')
                        self.data['imdbid'] = str(newimdbid)
                else:
                    return headers, row, False
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

class FetchApi(FetchAPIMixin):
    search_url = settings.SEARCH_URL + '%s'
    get_url = settings.FETCH_URL + '%s'

    def get_movies(self, file_name):
        print 'Searching Movies from IMDB'
        movies = self.get_data_from_url(self.search_url % (file_name))
        if settings.ASK_MANUAL_NAME:
            while (not (movies and movies.get('Search') and movies.get('Response') == "True")):
                ifyes = raw_input('Unable to find movie do you want to try another name(%s): ' % (file_name))
                if ifyes == 'n':
                    return
                file_name = raw_input('Enter movie: ')
                movies = self.get_data_from_url(self.search_url % (file_name))
        else:
            if movies and movies.get('Search') and movies.get('Response') == "True":
                return movies
            else:
                return None
        return movies.get('Search')

    def get_movie(self, imdbID):

        print 'Fetching Movie from IMDB'
        movie = self.get_data_from_url(self.get_url%(imdbID))
        if movie and movie.get('Response', '') == "True":
            return movie
        else:
            print "Not Found: %s", self.get_url
            return None

def get_data_from_files(allfiles):
    for filepath in allfiles:
        file_size = os.path.getsize(filepath)/(1024*1024.0)
        file_name,format = os.path.basename(filepath).rsplit('.', 1)
        data = {'file_name':file_name,'file_size':file_size,'format':format,'file_path':filepath}
        searchedmovie = FetchApi().get_movies(file_name)
        if searchedmovie:
            searchedmovie = searchedmovie[0]
            movie = FetchApi().get_movie(str(searchedmovie.get('imdbID', '')))
            if movie:
                data.update(movie)
                gd = GetMovieDataMixin(data)
                headers, row, status = gd.get_data()
                if status:
                    gd.commit(headers, [row], Movies)
                    print '%s movie successfully added' % (data['Title'])
                else:
                    print '%s MOVIE NOT ADDED' % data['Title']
        else:
            print 'Unable to fetch movie %s'%(data['file_name'])


class Fileobj(FileMixin):

    @classmethod
    def is_video(self, filepath):
        media_info = MediaInfo.parse(filepath)
        for track in media_info.tracks:
            if track.track_type == 'Video':
                return True
        return False

    @classmethod
    def is_prev_added(self, filepath):
        name = os.path.basename(os.path.abspath(filepath)).rsplit('.',1)[0]
        return name.endswith('__bak')
