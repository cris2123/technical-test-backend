# Run with "python server.py"

import peewee as pw
import os
import json
import operator

from bottle import get, post, run, static_file, route, template, hook, request, response
from datetime import date, datetime

### My own modules
from database.database import sql_database
from serializers.noteSerializer import NoteSchema
from serializers.linkSerializer import LinkSchema
from models.note import Note
from models.links import Links
from utils.helpers import addSerializerParameters, getResourcePath
from utils.querycomposer import QueryComposer



@hook('before_request')
def db_connect():
    sql_database.connect()


@hook('after_request')
def db_close():
    if not sql_database.is_closed():
      sql_database.close()

    return response


def mergeJson(jsonA, jsonB):

  jsonMerged = {**json.loads(jsonA.data), **json.loads(jsonB.data), }
  print(jsonMerged)
  asString = json.dumps(jsonMerged)
  print(asString)

  return asString


def _getPagination(request, recordNumber):

  parameter = request.query.decode()

  completeURL = str(request.url)
  completeURL = completeURL.replace("%2C", ',')
  
  currentURL = ""
  previousURL = ""
  forwardURL = ""

  print(recordNumber)

  if not parameter.get('pagesize',False):

    if not (recordNumber < 5):

      forwardURL = completeURL + "&pagesize=5" + "&continuetoken=2"

  else:

    pagesize = int(parameter.get('pagesize'))
    currentURL = completeURL

    if not parameter.get('continuetoken',False):
  
      if not (recordNumber < pagesize):
        forwardURL = completeURL + "&continuetoken=2"

    else:
      
      tokenValue = int(parameter.get('continuetoken',False))

      previous = tokenValue -1
      forward = tokenValue + 1

      if previous > 0:
        previousURL = completeURL.replace("continuetoken="+ str(tokenValue), "continuetoken=" + str(previous))

      if not (recordNumber < pagesize):
        print("Entre aqui")
        print("continuetoken=" + str(forward))
        
        forwardURL = completeURL.replace("continuetoken="+ str(tokenValue),"continuetoken=" + str(forward))

  requestPagination = Links(current=completeURL,previous=previousURL,following=forwardURL)

  showValues = []

  if forwardURL:
    showValues.append('following')

  if previousURL:
    showValues.append('previous')

  showValues.append('current')

  schema = LinkSchema()
  schema.only = tuple(showValues)
  jsonLinks = schema.dumps(requestPagination)

  print(jsonLinks.data)

  return jsonLinks.data
  
@get('/api/v1/notes')
@get('/api/v1/notes/<id:int>')
def get_all_notes(id=None):

  response.headers['Content-Type'] = 'application/json'

  ## TODO : Check documentation to find another way, maybe use keys instead of len
  if len(request.query) > 0:
    
    queries = QueryComposer.computeRequestQueries(Note,request.query.decode())

  if not id:

    schema = NoteSchema(many=True)

    notes = Note()

    if queries.get('selection',False):
      notes = Note.select(*queries['selection'][0])
      showOnSerializer = addSerializerParameters(queries['selection'][1], 'links')
      schema.only = showOnSerializer

    else:
      notes = notes.select()

    if queries.get('sort', False):
      notes = notes.order_by(*queries['sort'])
    else:
      notes = notes.order_by(Note.id)

    notes = notes.paginate(queries['pagination'][0],queries['pagination'][1])

    if queries.get('search',False):
      notes = notes.where(queries['search'])
    
    # schema = NoteSchema(many=True)
    searchCount = notes.count()

    links = Links()
    links.setLinks(request,searchCount)

    lschema = LinkSchema()
    lschema.only = links._getVisibleFields()
    jsonLinks = lschema.dumps(links)

    
  else:
    notes = Note.get(Note.id == id)

    schema = NoteSchema()

  jsonNotes = schema.dumps(notes, {"requestData": "/api/v1/notes/id"})

  jsonComplete = mergeJson(jsonLinks,jsonNotes)
  return jsonComplete
  #return jsonNotes.data

@post('/api/v1/notes')
def post_note():

  requestData = request.json
  print(requestData)

  schema = NoteSchema()
  noteObject = schema.load(requestData).data

  noteObject.save()

  jsonNotes = schema.dumps(noteObject)
  response.headers['Content-Type'] = 'application/json'

  return jsonNotes.data

@post('/api/v1/notes/batchnotes')
def post_notes():

  requesData = request.json

  schema = NoteSchema(many=True)

  noteObjects = schema.load(requesData).data

  ## TDO : Fix problem with objects not getting bulk create method
  with sql_database.atomic():
    Note.bulk_create(noteObjects)

  jsonNotes = schema.dumps(noteObjects)
  response.headers['Content-Type'] = 'application/json'

  return jsonNotes.data


# Start your code here, good luck (: ...
def set_initial_data(db_handler, tables):

  with db_handler:
    db_handler.create_tables(tables)
    load_data(db_handler)

  
def load_data(db_handler):

  """ Method to generate random notes to fill our database and test endpoints"""

  from random import seed
  from random import random
  
  seed(1)

  new_notes = []

  for i in range(1,10):

    new_notes.append({


        'title': str(i) + str(random()),
        'content': 'Lorem ipsum' + str(i),
        'active': True,
        'created_by':"Cristhian" + str(i),
        'created_at': date.today(),
        'edited_at':date.today(),
        
    })

  new_notes.append(
      {
          "active": False,
          "content": "Jesenia",
          "edited_at": "2019-10-24",
          "title": "Jesenia La chica de al lado",
          "created_by": "Cristhian1",
          "created_at": "2019-10-24"
      })

  new_notes.append(
      {
          "active": False,
          "title": "La vida de los numeros",
          "content": "Lorem ipsum y los numeros de la muerte",
          "edited_at": "2019-10-25",
          "created_by": "Jesenia",
          "created_at": "2019-10-24"
      })

  Note.insert_many(new_notes).execute()

if __name__ == "__main__":
  
  print("Removing database")
  os.remove('notes.db')

  set_initial_data(sql_database, [Note])
  
  run( reloader=True, host='localhost', port=8000)

  
  

 




  
