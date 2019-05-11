from flask import Flask, render_template, request, Response, json, jsonify
from modules.event import Event
import modules.auth as Auth
import routers.mongo as Database

app = Flask(__name__)
app.config['DEBUG'] = True

STATUS_KEY = 'status'
RESULT_KEY = 'result'
CITY_KEY = 'city'
CLIENT_ID_KEY = 'clientid'
USER_PASSWORD = 'password'
EVENT_ID_KEY = 'eventid'
SWITCH_KEY = 'switch'
USERID_KEY = 'uuid'
USERTAGS_KEY = 'tags'

SUCCESS_STATUS = 200
INVALID_SEARCH_STATUS = 404
INVALID_PASSWORD = 405
INVALID_QUERY = 406
INVALID_PASSWORD_MESSAGE = 'Invalid Password'
INVALID_ClIENT_MESSAGE = 'Invalid Client'
INVALID_SEARCH_MESSAGE = 'Search Error: Not Found'

def getJsonResponse(code, message):
  response = jsonify(message)
  response.status_code = code
  return response

def searchResults(result):
  if result == None:
    return getJsonResponse(INVALID_SEARCH_STATUS, INVALID_SEARCH_MESSAGE)
  return getJsonResponse(SUCCESS_STATUS, result)

def validateAttendant(eventid, userid, tags):
  if (
    eventid == None or
    userid == None or
    tags == None or
    not isinstance(tags, list)
  ):
    return False
  
  return True

def getAttendantObject(userid, tags):
  return {
    USERID_KEY: str(userid),
    USERTAGS_KEY: tags
  }

# GET REQUESTS
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/events/id/<string:eventid>', methods=['GET'])
def getEventByID(eventid):
  return searchResults(Database.getEventFromID(eventid))

@app.route('/events/dayof/<int:year>/<int:month>/<int:day>', methods=['GET'])
def getEventByDay(year, month, day):
  return searchResults(Database.eventsFromDay(year, month, day))

@app.route('/events/weekof/<int:year>/<int:month>/<int:day>', methods=['GET'])
def getEventByWeek(year, month, day):
  return searchResults(Database.eventsFromWeek(year, month, day))

@app.route('/events/range/<latitude>,<longitude>,<radius>')
def getEventByMapRadius(latitude, longitude, radius):
  try:
    lat = float(latitude)
    lon = float(longitude)
    rad = float(radius)
    return searchResults(Database.eventsFromRange(lat, lon, rad))
  except TypeError as err:
    return getJsonResponse(INVALID_SEARCH_STATUS, 'Search Error: Wrong Format')

# POST REQUESTS
@app.route('/newclient')
def createNewClientID():
  password = request.args.get(USER_PASSWORD)
  result  = Auth.addNewClient(password)

  if result == None:
    return getJsonResponse(INVALID_PASSWORD, INVALID_PASSWORD_MESSAGE)
  return getJsonResponse(SUCCESS_STATUS, result)

@app.route('/toggleDatabase')
def toggleRoute():
  clientID = request.args.get(CLIENT_ID_KEY)
  datasourceId = request.args.get(SWITCH_KEY)

  if Auth.validateClient(clientID) == False:
    return getJsonResponse(INVALID_PASSWORD, INVALID_ClIENT_MESSAGE)
  elif datasourceId == None or not isinstance(datasourceId, str):
    return getJsonResponse(INVALID_QUERY, 'Invalid Query Type') 
  elif datasourceId not in Database.DATABASE_SWITCHES:
    return getJsonResponse(INVALID_QUERY, 'Invalid DB Name')
  
  previous = Database.DATABASE_SWITCHES[datasourceId]
  Database.DATABASE_SWITCHES[datasourceId] = not previous
  result = str(Database.DATABASE_SWITCHES[datasourceId])
  return getJsonResponse(SUCCESS_STATUS, result)

@app.route('/update')
def updateDatabase():
  clientID = request.args.get(CLIENT_ID_KEY)
  city = request.args.get(CITY_KEY)

  if Auth.validateClient(clientID) == False:
    return getJsonResponse(INVALID_PASSWORD, INVALID_ClIENT_MESSAGE)
  elif city == None:
    return getJsonResponse(INVALID_QUERY, 'Invalid City Query')

  Database.fillDatabase(str(city))
  return getJsonResponse(SUCCESS_STATUS, 'Updated')

@app.route('/delete')
def deleteOne():
  clientID = request.args.get(CLIENT_ID_KEY)
  eventId = request.args.get(EVENT_ID_KEY)

  if Auth.validateClient(clientID) == False:
    return getJsonResponse(INVALID_PASSWORD, INVALID_ClIENT_MESSAGE)
  elif eventId == None:
    return getJsonResponse(INVALID_QUERY, 'Invalid Event ID')
  
  results = Database.safe_delete(str(eventId))
  return getJsonResponse(results[STATUS_KEY], results[RESULT_KEY])

@app.route('/clean')
def cleanDatabase():
  clientID = request.args.get(CLIENT_ID_KEY)

  if Auth.validateClient(clientID) == False:
    return getJsonResponse(INVALID_PASSWORD, INVALID_ClIENT_MESSAGE)

  result = Database.safe_clean()
  return getJsonResponse(SUCCESS_STATUS, ("%d Deleted" % result))

# Passing arrays = tags[]=car&tags[]=radio
@app.route('/addAttendant')
def addAttendant():
  clientID = request.args.get(CLIENT_ID_KEY)
  eventId = request.args.get(EVENT_ID_KEY)
  userID = request.args.get(USERID_KEY)
  tags = request.args.getlist(USERTAGS_KEY + '[]')

  if validateAttendant(eventId, userID, tags) == False:
    return getJsonResponse(INVALID_QUERY, 'Invalid Query')

  results = Database.safe_addAttendant(str(eventId), getAttendantObject(userID, tags))
  return getJsonResponse(results[STATUS_KEY], results[RESULT_KEY])

@app.route('/removeAttendant')
def removeAttendant():
  clientID = request.args.get(CLIENT_ID_KEY)
  eventId = request.args.get(EVENT_ID_KEY)
  userID = request.args.get(USERID_KEY)
  tags = request.args.getlist(USERTAGS_KEY + '[]')

  if validateAttendant(eventId, userID, tags) == False:
    return getJsonResponse(INVALID_QUERY, 'Invalid Query')

  results = Database.safe_removeAttendant(str(eventId), getAttendantObject(userID, tags))
  return getJsonResponse(results[STATUS_KEY], results[RESULT_KEY])

# INIT
if __name__ == '__main__':
  app.run()