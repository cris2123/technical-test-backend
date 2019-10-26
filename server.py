# Run with "python server.py"

import peewee as pw
import os
import json
import operator


from bottle import get, post, run, static_file, route, template, hook, request, response
from marshmallow import Schema, fields, pprint, post_load, pre_dump, post_dump
from datetime import date, datetime
from functools import reduce


### Database and model Section

sql_database = pw.SqliteDatabase('notes.db')

class BaseModel(pw.Model):
  'Set base model where we especify which database are we gonna use'
  class Meta:
    database = sql_database

class Note(BaseModel):
  
  title = pw.CharField()
  content = pw.CharField()
  created_by = pw.CharField()
  edited_at = pw.DateField()
  created_at = pw.DateField()
  active = pw.BooleanField()
  #uuid = pw.UUIDField(unique=True)


class ErrorBase():

  _error_dict = {

    '1': "Bad query arguments for resource",
    '2': "Cannot find any expected values",
    '3': "Bad pagination offset",
    '4': "Cannot filter queries when searching a record by id",

  }

class ErrorObject(ErrorBase):

  def __init__(self,**kwargs):

     allowed_keys = set(['_status', '_title', '_source','_detail'])
     self.__dict__.update((key, False) for key in allowed_keys)
     self.__dict__.update((key, value) for key,value in kwargs.items() if key in allowed_keys )

  def setSourceError(self, originURI):

    self._source = originURI

  def getErrorCode(self,error):

    return self._error_dict[error]

    
## Serializers definition

class NoteSchema(Schema):

  title = fields.Str()
  content = fields.Str()
  created_by = fields.Str()
  edited_at = fields.Date()
  created_at = fields.Date()
  active = fields.Boolean()

  @post_load
  def create_note(self, data,**kwargs):

    data.update({
      'created_at': datetime.now().date(),
      'edited_at': datetime.now().date(),
      'created_by': "Cristhian"
    })
    
    return Note(**data)

  @post_dump(pass_many=True)
  def create_envelope(self,data,many,**kwargs):
    return({'data': data})


class ErrorSchema(Schema):

  status = fields.Str()
  title = fields.Str()
  source = fields.Str()
  detail = fields.Str()

  @post_dump(pass_many=True)
  def create_error(self,data,many,**kwargs):

    """ Function to wrap my error objects """
    return({'error': data })



def _parseTypeValue(value):

  """ Utility function to get queryParameters type using a naive approach
  
    If paramter is a boolean like true or False function return the equivalent boolean
    If input can be converte to a number base 10 , return number
    else is a simple string and i need to filter by it
  
  """

  if value == "True":
    return True
  
  elif value == "False":
    return False

  else:

    result = ""

    try:
      result = int(value)
    except ValueError:
      result = value

    return result


# helper function // Maybe create a function named queryManager
def _filterResourceFields(resourceFields, Resource):
  """ Return list of tuples with querystring parameters which are defined in ou resource
      
      input : Resource object 
      input : [(parameter, value), ......]
      output : [(parameter, value), ......]

  """
  attributes = Resource._meta.fields.keys()

  return [fields for fields in resourceFields if fields[0] in attributes]


def _prepareQueryParameters(queryParameters, Resource):
  """ Returns a tuple with  a list of queryString variables and values for the system (pagination, metadata, etc)
      and another with filters to get data from resource endpoint
  """
  systemParams = ['pageSize', 'continuationToken', 'limit']

  systemValues = []
  filterValues = []

  for parameter in queryParameters:

    if parameter in systemParams:
      systemValues.append(( parameter, _parseTypeValue(queryParameters[parameter]) ))
    else:
      filterValues.append(
          ( parameter, _parseTypeValue(queryParameters[parameter]) )
      )

  filterValues = _filterResourceFields(filterValues, Resource)
  return (filterValues, systemValues)

def _getQueryExpression(filterValues, Resource):

  
  exp = [(getattr(Resource, attribute) == value) for attribute,value in filterValues ]
  return reduce(operator.and_, exp)
  
def computeRequestQueries(Resource,queryParameters):

  """ function computes query expression to get record base on api request """

  expressionFilter  = ""
  expressionSystem = ""
  
  filterValues, systemValues = _prepareQueryParameters(queryParameters, Resource)

  if filterValues:
    expressionFilter = _getQueryExpression(filterValues, Resource)

  #####TODO: Implement maybe paginationClass to get this data
  if systemValues:
    expressionSystem = ""

  return (expressionFilter,expressionSystem)


def _get_query_parameters(query):

  filters = [ parameter for parameter in query if parameter not in ['pageSize','continuationToken','limit']]
  print(filters)
  return filters

@hook('before_request')
def db_connect():
    sql_database.connect()


@hook('after_request')
def db_close():
    if not sql_database.is_closed():
      sql_database.close()

    return response

def _get_attr(object,filters):


  exp = [ (getattr(object,f) == v ) for f,v in zip(filters,[False])]
  exp2 = reduce(operator.and_,exp)
  print(exp2)

  return exp2

@get('/api/v1/notes')
@get('/api/v1/notes/<id:int>')
def get_all_notes(id=None):

  response.headers['Content-Type'] = 'application/json'

  ## TODO : Check documentation to find another way, maybe use keys instead of len
  if len(request.query) > 0:
    filterQueries, systemQueries = computeRequestQueries(Note,request.query.decode())

  if not id:

    """maybe something like:

    if selectQueries:
       notes = Note.select(selectQueries)
     if filterQueries:
       notes.where(filterQueries)
     if systemQueries:
       notes.page(bla bla bla)

    """
 
    if filterQueries:
      notes = Note.select().where(filterQueries)
    else:
      notes = Note.select()

    schema = NoteSchema(many=True)

  else:
    notes = Note.get(Note.id == id)
    schema = NoteSchema()

  jsonNotes = schema.dumps(notes)

  return jsonNotes.data

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
          "edited_at": "2019-10-24",
          "created_by": "Jesenia",
          "created_at": "2019-10-24"
      })

  Note.insert_many(new_notes).execute()

if __name__ == "__main__":
  
  print("Removing database")
  os.remove('notes.db')

  set_initial_data(sql_database, [Note])
  
  run( reloader=True, host='localhost', port=8000)

  
  

 




  
