import peewee as pw
from models.base import BaseModel

class User(BaseModel):

  name = pw.CharField()
  email = pw.CharField()
  password = pw.CharField()
  token = pw.Charfield()
  tokenExpiration = pw.DateTimeField()
  

  def setLink(self, rootPath, id):

    self.links = rootPath + '/' + id
