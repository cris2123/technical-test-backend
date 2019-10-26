from database.database import sql_database
import peewee as pw

class BaseModel(pw.Model):
  'Set base model where we especify which database are we gonna use'
  class Meta:
    database = sql_database
