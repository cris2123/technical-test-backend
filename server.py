# Run with "python server.py"

import peewee as pw
import os
import json
import operator
import bcrypt

from bottle import get, post, run, static_file, route, template, hook, request, response, abort
from datetime import date, datetime , timedelta

### TDO: Refactor inits to import by package 
from database.database import sql_database
from serializers.noteSerializer import NoteSchema
from serializers.linkSerializer import LinkSchema
from serializers.userSerializer import UserSchema
from serializers.errorSerializer import ErrorSchema
from models.note import Note
from models.links import Links
from models.user import User
from models.error import ErrorObject, computeErrorObject
from utils.helpers import addSerializerParameters, getResourcePath, mergeJson
from utils.querycomposer import QueryComposer

import jwt


## Global Variables
JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

@hook('before_request')
def db_connect():
    sql_database.connect()


@hook('after_request')
def cleaning_request():
    if not sql_database.is_closed():
      sql_database.close()

    ## Set header for CORS request
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'

    return response


@route('/api/v1/notes', method=["OPTIONS","GET"])
@route('/api/v1/notes/<id:int>')
def get_all_notes(id=None):

  response.headers['Content-Type'] = 'application/json'
  if request.method == "OPTIONS":
    return response

  else:
    
    queries = ""

    ## TODO : Check documentation to find another way, maybe use keys instead of len
    if len(request.query) > 0:
      queries = QueryComposer.computeRequestQueries(Note,request.query.decode())

    if not id:

      schema = NoteSchema(many=True)

      if queries:

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

      else:

        notes = Note.select()
        #notes = notes.paginate(1,5)

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


@route('/api/v1/notes', method=["POST","OPTIONS"])
def post_note():

  if request.method == "OPTIONS":
    return

  else:

    response.headers['Content-Type'] = 'application/json'
    requestData = request.json
    
    schema = NoteSchema()
    noteObject = schema.load(requestData).data

    # Update notes in database
    try:
      noteObject.save()
    
    except pw.IntegrityError:

      errorDict = {
        'status': 400,
        'detail': 'All note field are required',
        'title': 'Bad data',
        'source': getResourcePath(request.urlparts[:3])
      }

      response.status = 400
      return computeErrorObject(errorDict)

    # Return created note
    jsonNotes = schema.dumps(noteObject)
    response.headers['Content-Type'] = 'application/json'

    return jsonNotes.data

@post('/api/v1/notes/batchnotes')
def post_notes():

  requesData = request.json

  schema = NoteSchema(many=True)

  noteObjects = schema.load(requesData).data

  with sql_database.atomic():
    Note.bulk_create(noteObjects)

  jsonNotes = schema.dumps(noteObjects)
  response.headers['Content-Type'] = 'application/json'

  return jsonNotes.data

@post('/api/v1/register')
def registerUser():

  try:

    userParams = request.json

  except Exception as e:

    errorDict = {
        'status': 400,
        'detail': 'There is not request payload. %s' %(e),
        'title': 'Not data',
        'source': getResourcePath(request.urlparts[:3])
    }

    response.status = 400
    return computeErrorObject(errorDict)

  if userParams:

    password = userParams.get('password', False)
    email = userParams.get('email',False)
    name = userParams.get('name',False)

    if not password or not email or not name:

      errorDict = {
          'status': 400,
          'detail': 'To authenticate you need email and password',
          'title': 'Not data',
          'source': getResourcePath(request.urlparts[:3])
      }
      response.status = 400
      return computeErrorObject(errorDict)

    else:
      
      password= password.encode('utf-8')
      hashed = bcrypt.hashpw(password, bcrypt.gensalt())
      
      userCount = User.select().where(User.email == email).count()

      if userCount > 0:

        errorDict = {
            'status': 400,
            'detail': 'User already exist on database',
            'title': 'Existing user',
            'source': getResourcePath(request.urlparts[:3])
        }

        response.status = 400
        return computeErrorObject(errorDict)

      else:

        User(name=name,email=email,password=hashed).save()
        response.status = 201
        return {"response": "User created sucesfully"}


@route('/api/v1/login', method=["POST","OPTIONS"])
def log_user():

  if request.method == "OPTIONS":
     return response
  else:

    try:
      userData = request.json
    except Exception as e:

      errorDict = {
          'status': 400,
          'detail': 'There is not request payload',
          'title': 'Not data',
          'source': getResourcePath(request.urlparts[:3])
      }

      response.status = 400
      return computeErrorObject(errorDict)

    email = userData.get('email',False)
    password = userData.get('password',False)

    if not email or not password:

      errorDict = {
          'status': 400,
          'detail': 'To authenticate you need email and password',
          'title': 'Incomplete Data',
          'source': getResourcePath(request.urlparts[:3])
      }
      response.status = 400
      return computeErrorObject(errorDict)
      
    else:

      try:
        query = (User.select().where(User.email == email))
        user = query.get()

      except pw.DoesNotExist:
        
        errorDict = {
            'status': 404,
            'detail': 'User not found in database',
            'title': 'User not found',
            'source': getResourcePath(request.urlparts[:3])
        }
        response.status = 404
        return computeErrorObject(errorDict)

      if user:

        password = password.encode('utf-8')

        # Validate password with hash
        if bcrypt.checkpw(password, user.password):

          exp = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
          payload = {
            'user_id': user.id,
            'exp': exp
          }


          # Setting jwt token
          jwtToken = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

          if jwtToken:

            user.update({'tokenExpiration': exp , 'activeToken': True }).execute()
          
            response.body = json.dumps({'token': jwtToken.decode('utf-8')})
            response.status = 200
            return response

          else:

            errorDict = {
                'status': 500,
                'detail': 'Error Generating JWT token',
                'title': 'Error Token Generation',
                'source': getResourcePath(request.urlparts[:3])
            }

            response.status = 500
            return computeErrorObject(errorDict)

        else:

          errorDict = {
              'status': 403,
              'detail': 'User not found in database',
              'title': 'User not found',
              'source': getResourcePath(request.urlparts[:3])
          }
          response.status = 403
          return computeErrorObject(errorDict)

@get('/api/v1/users')
def get_all_users():

  users = User.select()
  userSchema = UserSchema(many=True)
  jsonUser = userSchema.dumps(User)

  return jsonUser.data


def getToken(request):

  jwtToken = request.headers.get("Authorization", False)
  return jwtToken
  

def auth_required(fn):
  
  def jwtValidation(*args, **kwargs):

    jwtToken = getToken(request)
    if jwtToken:

      #Remove Bearer string part "Beares <token>"
      headerParts = jwtToken.split()

      try:
        token = jwt.decode(headerParts[1], JWT_SECRET)
        request['user_id'] = token['user_id']
      except jwt.ExpiredSignature:
        errorDict = {
          'status': 401, 
          'detail': 'JWT token expired',
          'title': 'token Expiration',
          'source': getResourcePath(request.urlparts[:3])
        }
        return computeErrorObject(errorDict)

      except jwt.DecodeError:

        errorDict = {
            'status': 401,
            'detail': 'Invalid Token',
            'title': 'Your token is not valid',
            'source': getResourcePath(request.urlparts[:3])
        }

        return computeErrorObject(errorDict)
        # abort(401, {'code': 'token_invalid', 'description': "Some message "})

    else:

      errorDict = {
            'status': 403,
            'detail': 'Not authenticated',
            'title': 'There is no token on request header',
            'source': getResourcePath(request.urlparts[:3])
      }
      return computeErrorObject(errorDict)
      # abort(403, {'code': "Not token find on header"})
    
    return fn(*args, **kwargs)

  return jwtValidation


@get("/api/v1/profile")
@auth_required
def get_profile():

  """ Get current user profile"""

  if request['user_id']:

    user = User.select().where(User.id == request['user_id']).get()
    uSchema = UserSchema()
    jsonUser = uSchema.dumps(user)

    del request['user_id']
    return jsonUser.data

  return


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

  User(name="Cristhian", email="test@gmail.com",
       password=b'$2b$12$U/QjtHt/j0xRT4r8Hx3fOe93EssM6M0iiUaQJOrTd64RXbxvhw6Ii').save()

if __name__ == "__main__":
  
  print("Removing database")
  os.remove('notes.db')

  set_initial_data(sql_database, [Note,User])
  
  run( reloader=True, host='localhost', port=8000)

  
  

 




  
