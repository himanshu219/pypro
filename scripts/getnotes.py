import os
import sys
import traceback
# coding: utf-8
import evernote.edam.type.ttypes as Types
import unicodedata
from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMUserException, EDAMErrorCode, EDAMSystemException, EDAMNotFoundException
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from os.path import isfile, join


class NoteBookDoesNotExist(Exception):
    pass

class NoteBookAlreadyExist(Exception):
    pass

class Notebook(object):
    def __init__(self, client):
        self.client= client

    def _get_notebooks(self):
        note_store = self.client.get_note_store()
        notebooks = note_store.listNotebooks()
        return {n.name: n for n in notebooks}

    def _create_notebook(self, notebook):
        note_store = self.client.get_note_store()
        return note_store.createNotebook(notebook)

    def _update_notebook(self, notebook):
        note_store = self.client.get_note_store()
        note_store.updateNotebook(notebook)
        return

    notebooks = property(_get_notebooks)

    def create_or_update(self, notebook_name, stack=None):
        notebook = self.get(notebook_name, None)
        if notebook:
            if stack:
                notebook.stack = stack
                self._update_notebook(notebook)
            return notebook
        else:
            self.create(notebook_name, stack)


    def get(self, notebook_name, raise_exception=True):
        notebooks = self._get_notebooks()
        if notebook_name in notebooks:
            notebook = notebooks[notebook_name]
            return notebook
        else:
            if raise_exception:
                raise NoteBookDoesNotExist("%s notebook does not exist"%(notebook_name))
            else:
                return raise_exception

    def create(self, notebook_name, stack=None):
        if self.get(notebook_name, None):
            raise NoteBookAlreadyExist("%s notebook already exist"%(notebook_name))
        else:
            notebook = Types.Notebook()
            notebook.name = notebook_name
            if stack:
                notebook.stack = stack
            notebook = self._create_notebook(notebook)
            return notebook

    def get_or_create(self, notebook_name):
        return self.get(notebook_name, False) or self.create(notebook_name)



class Note(object):

    def __init__(self, client, notebook):
        self.client = client
        self.notebook = notebook

    def _create_evernote_note(self, data):
        # Create the new note
        note = Types.Note()
        note.title = data['title']
        note.notebookGuid = self.notebook.guid
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">' \
                       '<en-note>%s<br/>' \
                       '</en-note>'%(data['content'])
        return note

    def getnotes(self,auth_token, nb_guid, fun):
        spec = NotesMetadataResultSpec()
        spec.includeTitle=True
        filter=NoteFilter()
        filter.notebookGuid=nb_guid
        note_store = self.client.get_note_store()
        notelist = []
        for i in range(0,500,250):
            notes = note_store.findNotesMetadata(auth_token, filter, i, i+250, spec)
            notelist.extend([fun(n) for n in notes.notes])
        return notelist
    #
    # def _update_notebook(self, notebook):
    #     note_store = self.client.get_note_store()
    #     note_store.updateNotebook(notebook)
    #     return


    def upload_to_notebook(self, html):
        # Check if the evernote notebook exists
        from bs4 import BeautifulSoup as bs
        print("Uploading %s to %s" % (html['title'], self.notebook.name))
        soup = bs(html['content'].decode('UTF-8','ignore'), "html.parser")

        # empty_tags = soup.findAll(lambda tag: tag.name in ['en-media','en-todo'] and not tag.contents and (tag.string is None or not tag.string.strip()))
        # [empty_tag.extract() for empty_tag in empty_tags]
        [div.extract() for div in soup.findAll('en-media')]

        html['content'] = str(soup)
        note = self._create_evernote_note(html)
        note_store = self.client.get_note_store()
        note = note_store.createNote(note)

def get_data(query="select id,title,content from notes where id > 156 and id not in (10,15,16,17,20,26,29);",
                     db='/home/darkknight/evdat/everpad.db', arraysize=1000):

    'An iterator that uses fetchmany to keep memory usage down'
    import sqlite3
    conn = sqlite3.connect(db)
    cursor = conn.execute(query)
    colnames = [description[0] for description in cursor.description]
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break

        for result in results:
            yield dict(zip(colnames, result))


class Sync(object):
    token = "S=s245:U=1e2f5ee:E=15ce321c571:C=1558b709860:P=1cd:A=en-devtoken:V=2:H=bd15150c522ef2489eb5a0fe88d86f51"

    def __init__(self, token=None):
        self.client = None
        self.is_authenticated = None
        if token:
            self.token = token

    def get_client(self):
        self.is_authenticated = self._connect_to_evernote(self.token)
        return self.client

    def _connect_to_evernote(self, dev_token):
        user = None
        try:
            self.client = EvernoteClient(token=dev_token, sandbox=False)
            user_store = self.client.get_user_store()
            user = user_store.getUser()
        except EDAMUserException as e:
            err = e.errorCode
            print(
                "Error attempting to authenticate to Evernote: %s - %s" % (
                EDAMErrorCode._VALUES_TO_NAMES[err], e.parameter))
            return False
        except EDAMSystemException as e:
            err = e.errorCode
            print(
                "Error attempting to authenticate to Evernote: %s - %s" % (
                EDAMErrorCode._VALUES_TO_NAMES[err], e.message))
            sys.exit(-1)

        if user:
            print("Authenticated to evernote as user %s" % user.username)
            return True
        else:
            return False

    def get_token(self):
        return self.token

def main():
    notebook_name = 'ubuntunotes'
    sync = Sync()
    client = sync.get_client()
    token = sync.get_token()
    nb = Notebook(client)
    nbobj= nb.get_or_create(notebook_name)
    alltitle = Note(client, nbobj).getnotes(token, nbobj.guid, lambda x:(x.title))
    cnt = 0
    last_id = 0
    # id_list = [10, 15, 16, 17, 20, 26, 29, 165, 185, 194, 229, 235, 242, 246, 276, 294, 297, 309, 314, 324, 331, 338, 340, 343, 348, 360, 370, 374]
    id_list = {}
    # while True:
    #     query="select id,title,content from notes;"# where id > 29 and id <= %s and id not in (%s)"%(str(last_id), ','.join(map(str,id_list)))
    #     try:
            # for data in get_data(query):
            #     last_id = data['id']
            #     if data['title'] in alltitle:
            #         # note = Note(client, nbobj)
            #         # note.upload_to_notebook(data)
            #         cnt += 1
            #         # print "%d  %d %s note created"%(cnt, data['id'], data['title'])
            #     else:
            #         print "%d already exist"%(data['id'])
            #         id_list.update({data['id']:data['title']})
            #         with open(os.path.join("/home","darkknight","evdat","everpadhtml",str(data['id'])+"_"+data['title'].replace(" ","_").replace("/","__")+".html"),'w+') as f:
            #             f.write(data['content'].encode('UTF-8'))

        # except Exception as e:
        #     print traceback.format_exc()
        #     # id_list.update({data['id']: data['title']})
        # if last_id == 381:
        #     break
    hpath = "/home/darkknight/evdat/everpadhtml/"
    onlyfiles = [f for f in os.listdir(hpath) if isfile(join(hpath, f))]
    for fn in onlyfiles:
        id,_ = fn.split("_", 1)
        data = next(get_data("select id,title,content from notes where id = %s" % str(id)))
        try:
            data['title'] = unicodedata.normalize('NFKD',data['title']).encode('ascii', 'ignore')
            data['content'] = unicodedata.normalize('NFKD',data['content']).encode('ascii', 'ignore')
            note = Note(client, nbobj)
            note.upload_to_notebook(data)
            cnt += 1
            id_list.update({data['id']: data['title']})
            print "%d  %d %s note created"%(cnt, data['id'], data['title'])
        except Exception as e:
            print traceback.format_exc()
            print "Error: %d"%(data['id'])

    k = id_list.keys()
    k.sort()
    print "%d notes created"%(cnt)
    print last_id,k,len(k)


if __name__ == '__main__':
    main()

