from marshmallow import Schema, fields, pprint, post_load, pre_dump, post_dump
from bottle import request
from datetime import datetime

class UserSchema(Schema):

  name = fields.Str()
  email = fields.Email()
  activeToken = fields.Boolean()
  tokenExpiration = fields.DateTime()
  

  
