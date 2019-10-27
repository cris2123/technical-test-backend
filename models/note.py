
from models.base import BaseModel
import peewee as pw

class Note(BaseModel):

  title = pw.CharField()
  content = pw.CharField()
  created_by = pw.CharField()
  edited_at = pw.DateField()
  created_at = pw.DateField()
  active = pw.BooleanField()

  def __init__(self, *args, **kwargs):

    super().__init__(self, *args, **kwargs)
    self.links = ""

  def setLink(self, rootPath, id):

    self.links = rootPath + '/' + id
