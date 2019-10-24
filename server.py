# Run with "python server.py"

import peewee as pw
import os
import json

from bottle import get, post, run, static_file, route, template, hook, request, response
from marshmallow import Schema, fields, pprint, post_load
from datetime import date


### Database and model Section

sql_database = pw.SqliteDatabase('notes.db')

class BaseModel(pw.Model):
  'Set base model where we especify which database are we gonna use'
  class Meta:
    database = sql_database

class Person(BaseModel):

  name = pw.CharField()
  birthday = pw.DateField()


class Note(BaseModel):
  
  title = pw.CharField()
  content = pw.CharField()
  created_by = pw.CharField()
  edited_at = pw.DateField()
  created_at = pw.DateField()
  #uuid = pw.UUIDField(unique=True)


## Serializer definition

class NoteSchema(Schema):

  title = fields.Str()
  content = fields.Str()
  created_by = fields.Str()
  edited_at = fields.Date()
  created_at = fields.Date()

  @post_load
  def create_note(self, data,**kwargs):
    print("data")
    print(**kwargs)
    return Note(**data)


@hook('before_request')
def db_connect():
    sql_database.connect()


@hook('after_request')
def db_close():
    if not sql_database.is_closed():
      sql_database.close()


@get('/notes')
def get_all_notes():

  notes = Note.select().where(Note.title != False)
  
  schema = NoteSchema(many=True)
  json_notes = schema.dumps(notes)
  
  response.headers['Content-Type'] = 'application/json'
  
  return json_notes.data

@post('/notes')
def post_notes():

  object_data = request.json
  print(object_data)

  # schema = NoteSchema()
  # result = schema.load(object_data)

  new_notes= Note(
    title = object_data.get('title'),
    content=object_data.get('content'),
    created_by= "Cristhian",
    edited_at=date.today(),
    created_at=date.today() 
  )

  print(new_notes)
  new_notes.save()

  return request.json

  
## Not work so well, mabe i will because need to create __exit__ and __enter__ method manually
def create_tables(sql_database):
  with sql_database:
    sql_database.create_tables([Person])

# Start your code here, good luck (: ...

def set_initial_data(db_handler, tables):

  db_handler.create_tables(tables)
  load_data(db_handler)

  db_handler.close()


def load_data(db_handler):


  """ Method to generate random notes to fill our database and test endpoints"""

  from random import seed
  from random import random
  
  seed(1)

  new_notes = []

  for i in range(1,10):

    new_notes.append({

        'title': str(i) + str(random()),
        'created_by':"Cristhian" + str(i),
        'created_at': date.today(),
        'edited_at':date.today(),
        'content': 'Lorem ipsum' + str(i),
        

    })
  
  Note.insert_many(new_notes).execute()

if __name__ == "__main__":
  
  print("Removing database")
  os.remove('notes.db')

  set_initial_data(sql_database, [Note])
  
  run(host='localhost', port=8000)

  
  

 




  
