from marshmallow import Schema, fields, pprint, post_load, pre_dump, post_dump
from bottle import request
from datetime import datetime


# modules import
from models.note import Note
from utils.helpers import getResourcePath



class NoteSchema(Schema):

  title = fields.Str()
  content = fields.Str()
  created_by = fields.Str()
  edited_at = fields.Date()
  created_at = fields.Date()
  active = fields.Boolean()
  links = fields.Str(dump_only=True)

  @post_load
  def create_note(self, data, **kwargs):

    data.update({
        'created_at': datetime.now().date(),
        'edited_at': datetime.now().date(),
        'created_by': "Cristhian"
    })

    return Note(**data)

  @pre_dump(pass_many=True)
  def addLink(self, data, many, **kwargs):
    if  isinstance(data,type([])):
      for record in data:
        record.setLink(getResourcePath(request.urlparts[:3]), str(record.id))
    else:
      data.setLink(getResourcePath(request.urlparts[:3]), str(data.id))

    return data

  @post_dump(pass_many=True)
  def create_envelope(self, data, many, **kwargs):
    
    return({'data': data})
