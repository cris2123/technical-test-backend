from models.base import BaseModel

class Links():

  def __init__(self):

    self.previous = ""
    self.current = ""
    self.following = ""

  def setLinks(self,request, recordNumber):

    self._getPagination(request,recordNumber)

  def _getVisibleFields(self):

    visibles = []

    if self.following:
      visibles.append('following')
    if self.previous:
      visibles.append('previous')
    
    visibles.append('current')

    return tuple(visibles)

  def _getPagination(self,request, recordNumber):

    parameter = request.query.decode()

    completeURL = str(request.url)
    completeURL = completeURL.replace("%2C", ',')

    currentURL = ""
    previousURL = ""
    forwardURL = ""

    if not parameter.get('pagesize', False):

      if not (recordNumber < 5):

        forwardURL = completeURL + "&pagesize=5" + "&continuetoken=2"

    else:

      pagesize = int(parameter.get('pagesize'))
      currentURL = completeURL

      if not parameter.get('continuetoken', False):

        if not (recordNumber < pagesize):
          forwardURL = completeURL + "&continuetoken=2"

      else:
 
        tokenValue = int(parameter.get('continuetoken', False))

        previous = tokenValue - 1
        forward = tokenValue + 1

        if previous > 0:
          previousURL = completeURL.replace(
              "continuetoken=" + str(tokenValue), "continuetoken=" + str(previous))
          
          print("Entre en el previous")
          print(previousURL)

        if not (recordNumber < pagesize):
          
          forwardURL = completeURL.replace(
              "continuetoken=" + str(tokenValue), "continuetoken=" + str(forward))

    self.current = currentURL
    self.previous = previousURL
    self.following = forwardURL

    


