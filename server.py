# Run with "python server.py"

import peewee as pw
import os
import json
import operator
import bcrypt


from bottle import get, post, run, static_file, route, template, hook, request, response, abort
from datetime import date, datetime , timedelta

### My own modules
from database.database import sql_database
from serializers.noteSerializer import NoteSchema
from serializers.linkSerializer import LinkSchema
from serializers.userSerializer import UserSchema
from models.note import Note
from models.links import Links
from models.user import User
from utils.helpers import addSerializerParameters, getResourcePath
from utils.querycomposer import QueryComposer

import jwt

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

@hook('before_request')
def db_connect():
    sql_database.connect()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
      'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
            'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'


@hook('after_request')
def db_close():
    if not sql_database.is_closed():
      sql_database.close()

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'

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
  
@route('/api/v1/notes', method=["OPTIONS","GET"])
@route('/api/v1/notes/<id:int>')
def get_all_notes(id=None):

  response.headers['Content-Type'] = 'application/json'
  if request.method == "OPTIONS":

    return 

  else:
    print("TODO EL REQUEST")
    print(request.headers.get('Authorization'))
    ## TODO : Check documentation to find another way, maybe use keys instead of len
    queries = ""

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

@post('/api/v1/register')
def registerUser():

  userParams = request.json
  if userParams:

    password = userParams.get('password', False)
    email = userParams.get('email',False)
    name = userParams.get('name',False)

    if not password or not email or not name:
      response.status = 400
      return

    else:
      
      password= password.encode('utf-8')
      hashed = bcrypt.hashpw(password, bcrypt.gensalt())
      
      userCount = User.select().where(User.email == email).count()

      if userCount > 0:

        response.status = 402
        return 

      else:

        User(name=name,email=email,password=hashed).save()
        response.status = 201
        return 

@route('/api/v1/login', method=["POST","OPTIONS"])
def log_user():

  if request.method == "OPTIONS":
     return response
  else:

    userData = request.json

    email = userData.get('email',False)
    password = userData.get('password',False)

    if not email or not password:
      
      response.status = 400
      

    else:

      try:
        query = (User.select().where(User.email == email))
        user = query.get()


      except pw.DoesNotExist:
        
        response.status = 400
        return

      if user:
        password = password.encode('utf-8')
        if bcrypt.checkpw(password, user.password):

          print("I dit it the user is authenticated")

          exp = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
          payload = {
            'user_id': user.id,
            'exp': exp
          }

          jwtToken = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

          if jwtToken:
            user.update({'tokenExpiration': exp , 'activeToken': True }).execute()
          
            response.status = 200
            response.body = json.dumps({'token': jwtToken.decode('utf-8')})
            return response

          else:

            response.status = 403
            return {'error': "Error generating active token"}

        else:

          response.status = 404
          print("Invalid credentials")
          return

      else :
        response.status = 400
        return {"error": "Not valid user"}



@get('/api/v1/users')
def get_all_users():

  print(request.headers.get("Authorization"))
  
  users = User.select()

  userSchema = UserSchema(many=True)
  jsonUser = userSchema.dumps(User)

  return jsonUser.data


def getToken(request):

  jwtToken = request.headers.get("Authorization", False)
  return jwtToken
  

def auth_required(fn):
  print("estoy entrando en la funcion decorador")
  def decorated(*args, **kwargs):

    jwtToken = getToken(request)

    if jwtToken:

      headerParts = jwtToken.split()

      try:
        token = jwt.decode(headerParts[1], JWT_SECRET)
      except jwt.ExpiredSignature:
        abort(401, {'code': 'token_expired',
                    'description': 'token is expired'})
      except jwt.DecodeError:
        abort(401, {'code': 'token_invalid', 'description': "Some message "})

    else:
      abort(403, {'code': "Not token find on header"})
    print("Previo a entrar en la funcion real")
    return fn(*args, **kwargs)

  return decorated


@get("/api/v1/profile")
@auth_required
def get_profile():

  usertoken = getToken(request)
  if usertoken:

    parts = usertoken.split()
    jwtT = jwt.decode(parts[1],JWT_SECRET)

    print(jwtT)
    uid = jwtT['user_id']
    print(uid)

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

  
  

 




  
