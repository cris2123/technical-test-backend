import peewee as pw
from models.base import BaseModel

class User(BaseModel):

  name = pw.CharField()
  email = pw.CharField()
  password = pw.BitField()
  activeToken = pw.BooleanField(null = True)
  tokenExpiration = pw.DateTimeField(null = True)
  
  
