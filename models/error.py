
from serializers.errorSerializer import ErrorSchema
class ErrorBase():

  _error_dict = {

      '1': "Bad query arguments for resource",
      '2': "Cannot find any expected values",
      '3': "Bad pagination offset",
      '4': "Cannot filter queries when searching a record by id",

  }


class ErrorObject(ErrorBase):

  def __init__(self, **kwargs):

     allowed_keys = set(['status', 'title', 'source', 'detail'])
     self.__dict__.update((key, False) for key in allowed_keys)
     self.__dict__.update((key, value)
                          for key, value in kwargs.items() if key in allowed_keys)

  def setSourceError(self, originURI):

    self.source = originURI


def computeErrorObject(errorDict):

  eObj = ErrorObject(**errorDict)
  eschema = ErrorSchema()
  jsonError = eschema.dumps(eObj)
  
  return jsonError.data
  

  
