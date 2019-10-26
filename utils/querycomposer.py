
from datetime import date, datetime
from functools import reduce
import operator


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class QueryComposer(metaclass=Singleton):

  """ Class to group all common queries handlers used to support request url parameters inside the api"""

  @staticmethod
  def _parseTypeValue(value):
    """ Utility function to get queryParameters type using a naive approach
    
      If paramter is a boolean like true or False function return the equivalent boolean
      If value can be converted to a number base 10 , return number
      If is a simple string and dont need conversio processing happen later
    
    """
    if value == "True":
      return True

    elif value == "False":
      return False

    else:
      result = ""

      try:
        result = int(value)
      except ValueError:
        result = value

      return result

  @staticmethod
  def _getFieldValues(attributes, fields):
    """ Fields is a list of fields separeted by ,
        use to fill selection values
    """

    selectionFields = fields.split(',')
    validFields = []
    invalidFields = []

    print("Debugging selection fields")
    print(fields)
    print(selectionFields)

    for field in selectionFields:

      if field in attributes:
        validFields.append(field)
      else:
        invalidFields.append((field, 'invalid Field'))

    return (validFields, invalidFields)

  @staticmethod
  def _getSortValues(attributes, field):

    sortFields = field.split(',')

    validFields = []
    invalidFields = []

    for data in sortFields:

      operator = data[0]
      field = data[1:]

      if operator not in ['+', '-']:
        invalidFields.append((data, 'operatorError'))
        continue

      if field in attributes:
        validFields.append((operator, field))
      else:
        invalidFields.append((field, 'invalid field'))

    return (validFields, invalidFields)

  # helper function // Maybe create a function named queryManager

  @staticmethod
  def _filterResourceFields(resourceFields, Resource):
    """ Return list of tuples with querystring parameters which are defined in ou resource
        
        input : Resource object 
        input : [(parameter, value), ......]
        output : [(parameter, value), ......]

    """
    attributes = Resource._meta.fields.keys()

    queryFields = {
        'selectionFields': "",
        'sortFields': "",
        'searchFields': "",
    }

    errorQueryFields = {
        'errorSelection': [],
        'errorSort': [],
        'searchSort': [],
    }

    searchValues = []

    fieldCount = 0
    sortCount = 0

    ## TODO search is are more than 2 fields
    for fields in resourceFields:

      if fields[0] == "fields":
        fieldCount += 1

        if fieldCount < 2:
          queryFields['selectionFields'], errorQueryFields['errorSelection'] = QueryComposer._getFieldValues(
              attributes, fields[1])
        else:
          errorQueryFields['errorSelection'].append(
              ('fields', 'More than one fields attribute on api'))

      elif fields[0] == "sort":
        sortCount += 1

        if sortCount < 2:
          queryFields['sortFields'], errorQueryFields['errorSort'] = QueryComposer._getSortValues(
              attributes, fields[1])
        else:
          errorQueryFields['errorSort'].append(
              ('sort', 'More than one fields attribute on api'))

      else:
        searchValues.append(fields)

    queryFields['searchFields'] = searchValues

    return (queryFields, errorQueryFields)

  @staticmethod
  def _prepareQueryParameters(queryParameters, Resource):
    """ Returns a tuple with  a list of queryString variables and values for the system (pagination, metadata, etc)
        and another with filters to get data from resource endpoint
    """
    systemParams = ['pageSize', 'continuationToken', 'limit']

    systemValues = []
    filterValues = []

    for parameter in queryParameters:

      if parameter in systemParams:
        systemValues.append(
            (parameter, QueryComposer._parseTypeValue(queryParameters[parameter])))
      else:
        filterValues.append(
            (parameter, QueryComposer._parseTypeValue(queryParameters[parameter])))

    filterValues, errorValues = QueryComposer._filterResourceFields(
        filterValues, Resource)

    return (filterValues, systemValues, errorValues)

  @staticmethod
  def _getQueryExpression(filterValues, Resource):

    exp = [(getattr(Resource, attribute) == value)
          for attribute, value in filterValues]
    return reduce(operator.and_, exp)

  @staticmethod
  def _getQuerySelectionExpression(selectionValues, Resource):

    exp = [getattr(Resource, attribute) for attribute in selectionValues]

    if 'id' not in selectionValues:
      #append default _id for serializer use
      exp.append(getattr(Resource, 'id'))

    return exp

  @staticmethod
  def _getQuerySortExpression(sortValues, Resource):

    sortExpression = []

    print("Printing sort fields")
    print(sortExpression)

    for operator, attribute in sortValues:
      if operator == "+":
        sortExpression.append(getattr(Resource, attribute).asc())
      else:
        sortExpression.append(getattr(Resource, attribute).desc())

    return sortExpression

  @staticmethod
  def computeRequestQueries(Resource, queryParameters):
    """ 
      Function taht computes a valid queryExpression  to get records with peewee ORM
    """

    expressionData = {
        'search': "",
        'sort': "",
        'selection': "",
        'system': "",
    }

    filterValues, systemValues, errorValues = QueryComposer._prepareQueryParameters(
        queryParameters, Resource)

    if filterValues:

      if filterValues.get('searchFields', False):

        expressionData['search'] = QueryComposer._getQueryExpression(
            filterValues['searchFields'], Resource)

      if filterValues.get('selectionFields', False):

        expressionSelection = QueryComposer._getQuerySelectionExpression(
            filterValues['selectionFields'], Resource)
        expressionData['selection'] = (
            expressionSelection, filterValues['selectionFields'])

      if filterValues.get('sortFields', False):
        expressionData['sort'] = QueryComposer._getQuerySortExpression(
            filterValues['sortFields'], Resource)

    #####TODO: Implement maybe paginationClass to get this data
    if systemValues:
      expressionData["system"] = ""
      # expressionSystem = ""

    if errorValues:
      pass
      ## Check if some error ocurred Create Error Object

    return expressionData


