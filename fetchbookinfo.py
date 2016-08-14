import re
from functools import wraps,update_wrapper
import traceback
import pickle
import sys
import csv
GOOGLE_API_KEY = "AIzaSyAlwpepFBQIOcJzRqcLCdSAynmGFsqUSCk"

class persistent_locals(object):
    def __init__(self, func):
        self._locals = {}
        self.func = func
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        def tracer(frame, event, arg):
            if event=='return':
                self._locals = frame.f_locals.copy()

        # tracer is activated on next call, return or exception
        sys.setprofile(tracer)
        try:
            # trace the function call
            res = self.func(*args, **kwargs)
        finally:
            # disable tracer and replace with old one
            sys.setprofile(None)
        return res

    def clear_locals(self):
        self._locals = {}

    @property
    def locals(self):
        return self._locals


def loggerfactory(startmsg, endmsg, printfn=None, s_loc=False, s_inp=True, s_out=False):
    def logger(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if startmsg:
                print "\n","--"*20, "%s..."%(startmsg), "--"*20
            ret = None
            if s_inp:
                print "Input: ", args, kwargs
            
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                print "Error in %s, traceback: %s, errormsg: %s"%(func.__name__, traceback.format_exc(), str(e))
                #import pdb;pdb.set_trace()
                #ret = func(*args, **kwargs)
                           
            if s_loc and hasattr(func, "locals"):
                if printfn:
                    print "Locals: ", printfn(func.locals)
                else:
                    print "Locals: ", func.locals
            if s_out:
                if ret:
                    print "Output: ", ret
                else:
                    print "No Output"            
            if endmsg:
                print "--"*20, "%s..."%(endmsg), "--"*20
            return ret
        return wrapper
    return logger

class PersistentDict(dict):
    def __init__(self, filename):
                

    def has_id(self, id):

    def update(self, newdata):

    def create(self, newdata):

    def flush(self,)
    
def savep(outfile, alldata):
    with open(outfile+".pickle", 'wb') as handle:
      pickle.dump(alldata, handle)

def loadp(infile):
    with open(infile+'.pickle', 'rb') as handle:
      b = pickle.load(handle)
    return b

'''

@loggerfactory("Reading file from CSV...", "Finished Reading CSV...",printfn=lambda x:str(len(x["alldata"]))+" lines read",s_loc=True)
@persistent_locals
def readdata(infile):
    alldata = []
    with open(infile) as f:
        headers = [h.strip() for h in f.readline().split(',')]
        for line in f.readlines():
            #data = [token.strip() for token in re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)]
            data = [token.strip() for token in line.rsplit(',', len(headers)-1)]
            alldata.append(dict(zip(headers, data)))
    return alldata


@loggerfactory("Fetching Data from API...", "Finished Fetching Data From API")
def get_data_from_url(url,TOTAL_API_RETRIES=5, WAIT_TIME=0.1):
    import requests
    from requests.packages.urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    s = requests.Session()
    fetcheddata = {}
    retries = Retry(total=TOTAL_API_RETRIES,
                    backoff_factor=WAIT_TIME,
                    status_forcelist=[500, 502, 503, 504])

    s.mount('http://', HTTPAdapter(max_retries=retries))
    try:
        resp = s.get(url)
        if resp.ok:
            fetcheddata = resp.json()
    except Exception as e:
        import pdb;pdb.set_trace()
        print "Error in %s: %s" % (url, traceback.format_exc())

    return fetcheddata

@loggerfactory("Saving Data in CSV...", "Finished Fetching Data From API",printfn=lambda x:"saving %d lines, with headers: %s"%(len(alldata),x["headers"]),s_loc=True)
@persistent_locals
def savedata(alldata, outfile):
    from collections import OrderedDict
    headers = OrderedDict([(k, None) for k in alldata[0].keys()])
    with open(outfile, 'wb') as fou:
        dw = csv.DictWriter(fou, delimiter='\t', fieldnames=headers)
        dw.writeheader()
        for row in alldata:
            dw.writerow(row)

@loggerfactory('Parsing API Data...', 'Finished Parsing API Data...', printfn = lambda x: "keys in apidata: %s"%(x["newdata"]) ,s_inp=False, s_loc=True)
@persistent_locals
def parsedata(apidata):
    newdata = {}
    if apidata and apidata.get("volumeInfo", {}):
        apidata = apidata["volumeInfo"]
        newdata = {"description":apidata.get("description", ''), "categories":",".join(apidata.get("categories", [])), "averageRating": apidata.get("averageRating",''), "ratingsCount":apidata.get("ratingsCount",0), "imageLinks":apidata.get("imageLinks", {}).get('smallThumbnail',''), "pageCount":apidata.get("pageCount",0)}
    
    return newdata

    
                
@loggerfactory("BookInfo Script Started....", "BookInfo Script Finished...")
def main():
    bookdata = readdata("kcbooks.csv")    
    for i,data in enumerate(bookdata):
        url = "https://www.googleapis.com/books/v1/volumes?q=%s&key=%s"%(data.get('title', ''),GOOGLE_API_KEY)
        apidata = get_data_from_url(url).get("items",[None])[0]
        newdata = parsedata(apidata)
        if not newdata:
            import pdb;pdb.set_trace()            
            print "NOT FOUND",url,newdata        
        data.update(newdata)
        print "data updated for %d"%(i)
    import pdb;pdb.set_trace()
    savedata(bookdata,"newkcbooks.csv")    
        

if __name__ == "__main__":
    main()
