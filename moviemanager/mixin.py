import ctypes
import os
import traceback
from types import FunctionType

from moviemanager import settings
from moviemanager.models import DBSession


class GetDataMixin(object):

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

    def get_data(self):
        raise NotImplementedError('To use getdatamixin implement get_data which returns(header,row,status)')

    @classmethod
    def commit(cls,headers,rows, model, session=DBSession, commiter=DBSession):
        header = headers
        try:
            for row in rows:
                o = model(**dict(zip(header, row)))
                session.add(o)
            commiter.commit()
        except:
            commiter.rollback()
            print "Error in saving data: %s"%(traceback.format_exc()),rows

class ModifyDataMixin(object):


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

class FetchAPIMixin(object):

    @classmethod
    def get_data_from_url(self, url):
        import requests
        from requests.packages.urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter
        s = requests.Session()

        retries = Retry(total=settings.TOTAL_API_RETRIES,
                        backoff_factor=settings.WAIT_TIME,
                        status_forcelist=[500, 502, 503, 504])

        s.mount('http://', HTTPAdapter(max_retries=retries))
        try:
            resp = s.get(url)
            if resp.ok:
                return resp.json()
            else:
                return {}
        except Exception as e:
            print "Error in %s: %s" % (url, traceback.format_exc())

class FileMixin(object):

    @classmethod
    def is_hidden(self, filepath):
        name = os.path.basename(os.path.abspath(filepath))
        return name.startswith('.') or self.has_hidden_attribute(filepath)

    @classmethod
    def has_hidden_attribute(self, filepath):
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
            assert attrs != -1
            result = bool(attrs & 2)
        except (AttributeError, AssertionError):
            result = False
        return result

    @classmethod
    def has_size(self, filepath, szlimit):
        size = os.path.getsize(filepath) / (1024 * 1024.0)
        if size > szlimit:
            return True
        else:
            return False
