import traceback
from types import FunctionType

from moviemanager.models import Movies
from moviemanager.objects import GetMovieDataMixin, get_data_from_files


class Test(object):

    def _case_data_creation(self):
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

        gd = GetMovieDataMixin(data)
        headers, row, status = gd.get_data()
        if status:
            gd.commit(headers, [row], Movies)
        return True

    def _case_api_flow(self):
        testfilepath='/home/darkknight/Downloads/torrents/movies/Momentum.2015.HDRip.XViD-ETRG/Momentum.2015.HDRip.XViD-ETRG.avi'
        get_data_from_files([testfilepath])
        return True

    def test(self):
        passed = failed = 0
        for k, v in self.__class__.__dict__.items():
            if type(v) == FunctionType and k.startswith('_case_') == True:
                try:
                    print 'Running Test Case %s: '%(k)
                    status = v(self)
                    print "Successfull Status: %s"%(status)
                except:
                    failed += 1
                    print "Error in %s: %s"%(k,traceback.format_exc())
                else:
                    passed += 1
        print "Test Completed Passed:%d, Failed: %d "%(passed, failed)