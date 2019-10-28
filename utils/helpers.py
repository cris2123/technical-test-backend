import json

def addSerializerParameters(systemValues, extraParameters, resourceSchema=None):

  #TODO some validation on extraPArameter to Show if exist on schema
  # _checkSchemaParameters(extraParameter,resourceSchema)
  if isinstance(extraParameters, type([])):
    return tuple(systemValues + extraParameters)

  else:
    return tuple(systemValues + [extraParameters])

def getResourcePath(urlparts):
  "Get urlparts : scheme, host, path"
  return urlparts[0] + '://' + urlparts[1] + urlparts[2]

def getCompleteApiCall(url):

  return url.replace("%2C",',')

def mergeJson(jsonA, jsonB):

  jsonMerged = {**json.loads(jsonA.data), **json.loads(jsonB.data), }
  print(jsonMerged)
  asString = json.dumps(jsonMerged)
  print(asString)

  return asString
  
