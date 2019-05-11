from os import environ
from pymongo import MongoClient
from datetime import datetime, timedelta
from routers.seatgeek import getSeatGeekData
import modules.event as EVENT
import modules.geolocation as GEO

KEY_ENV_MONGO = 'MONGO_URI'
COLLECTION_NAME = 'HangEventCollection'

STATUS_KEY = 'status'
RESULT_KEY = 'result'
USERID_KEY = 'uuid'
USERTAGS_KEY = 'tags'
ERROR_INVALID_SEARCH = {
  STATUS_KEY : 602,
  RESULT_KEY : 'Not Found'
}
ERROR_INVALID_OBJECT = {
  STATUS_KEY : 601,
  RESULT_KEY : 'Invalid Object'
}
ERROR_DUPLICATE_OBJECT = {
  STATUS_KEY : 600,
  RESULT_KEY : 'Duplicate Object'
}
SUCCESS = {
  STATUS_KEY : 200,
  RESULT_KEY : 'Success'
}

MILE_TO_KM_RATE = 1.60934
DATABASE_FILL_COUNT = 1000
SEAT_GEEK_IS_ACTIVATED = True

mongoLink = environ.get(KEY_ENV_MONGO)
client = MongoClient() if mongoLink == None else MongoClient(mongoLink)
database = client.get_database()
collection = database[COLLECTION_NAME]

def fillDatabase(city):
  yesterday = datetime.utcnow() - timedelta(days=1)
  results = []

  if SEAT_GEEK_IS_ACTIVATED:
    results += getSeatGeekData(city, DATABASE_FILL_COUNT)
  
  for event in results:
    event = event.dictionary
    times = event[EVENT.Key_Times]
    startTimeStr = times[EVENT.Key_StartTimeStr]
    parser = times[EVENT.Key_Date_Parsing]

    if startTimeStr == None or parser == None:
      continue

    startDateObj = datetime.strptime(startTimeStr, parser)
    if (yesterday - startDateObj).days > 0:
      continue
    
    safe_insert(event)

def safe_insert(event):
  if EVENT.Key_ID not in event:
    return ERROR_INVALID_OBJECT
  
  if contains(event[EVENT.Key_ID]):
    return ERROR_INVALID_SEARCH
  
  collection.insert(event)
  success = dict(SUCCESS)
  success[RESULT_KEY] = event
  return success

def safe_createAndInsert(event):
  if not isValidPreset(event):
    return ERROR_INVALID_OBJECT

  if (
    EVENT.Key_Name not in event or
    EVENT.Key_Description not in event
  ):
    return ERROR_INVALID_OBJECT
  
  name = event[EVENT.Key_Name]
  desc = event[EVENT.Key_Description]
  attendanceKey = EVENT.Key_AttendanceList
  attendants = []
  if attendanceKey in event and type(event[attendanceKey]) == list:
    attendants = event[attendanceKey]

  eventInstance = EVENT.Event(name, desc, attendants=attendants, preset=event)
  
  response = safe_insert(eventInstance.dictionary)
  if not response[STATUS_KEY] == 200:
    return response
  
  success = dict(SUCCESS)
  success[RESULT_KEY] = eventInstance.dictionary
  return success

def contains(uid):
  return collection.find_one( {EVENT.Key_ID : uid} )

def safe_delete(uid):
  if contains(uid) == None:
    return ERROR_INVALID_SEARCH

  if not collection.delete_one( {EVENT.Key_ID:uid} ).acknowledged:
    return ERROR_INVALID_SEARCH

  return SUCCESS

def safe_clean():
  lessThan = '$lte'
  yesterday = datetime.utcnow() - timedelta(days=2)
  dateString = datetime.strftime(yesterday, EVENT.DEFAULT_PARSING_STRING)
  
  result = collection.delete_many({
    EVENT.Key_Times + "." + EVENT.Key_StartTimeStr:{
      lessThan:dateString
    }
  })

  return result.deleted_count

def safe_addAttendant(eventId, attendantObj):
  if (
    USERID_KEY not in attendantObj or
    USERTAGS_KEY not in attendantObj or
    not isinstance(attendantObj[USERTAGS_KEY], list)
  ):
    return ERROR_INVALID_OBJECT
  
  event = contains(eventId)
  if event == None:
    return ERROR_INVALID_SEARCH

  if attendantObj[USERID_KEY] in event[EVENT.Key_AttendanceList]:
    return ERROR_DUPLICATE_OBJECT
  
  name = event[EVENT.Key_Name]
  desc = event[EVENT.Key_Description]
  attendants = event[EVENT.Key_AttendanceList]
  eventInstance = EVENT.Event(name, desc, attendants=attendants, preset=event)

  eventInstance.addAttendant(attendantObj[USERID_KEY])
  for tag in attendantObj[USERTAGS_KEY]:
    eventInstance.addTag(tag)

  result = collection.find_one_and_update(
    {EVENT.Key_ID: eventInstance.dictionary[EVENT.Key_ID]},
    {
      '$set': {
        EVENT.Key_Tags : eventInstance.dictionary[EVENT.Key_Tags],
        EVENT.Key_AttendanceList: eventInstance.dictionary[EVENT.Key_AttendanceList],
        EVENT.Key_AttendanceCount: eventInstance.dictionary[EVENT.Key_AttendanceCount],
        EVENT.Key_Statistics : eventInstance.dictionary[EVENT.Key_Statistics]
      }
    }
  )

  if result == None:
    return ERROR_INVALID_SEARCH
  
  success = dict(SUCCESS)
  success[RESULT_KEY] = eventInstance.dictionary
  return success

def safe_removeAttendant(eventId, attendantObj):
  if (
    USERID_KEY not in attendantObj or
    USERTAGS_KEY not in attendantObj or
    not isinstance(attendantObj[USERTAGS_KEY], list)
  ):
    return ERROR_INVALID_OBJECT
  
  event = contains(eventId)
  if event == None:
    return ERROR_INVALID_SEARCH

  if attendantObj[USERID_KEY] not in event[EVENT.Key_AttendanceList]:
    return ERROR_INVALID_SEARCH

  name = event[EVENT.Key_Name]
  desc = event[EVENT.Key_Description]
  attendants = event[EVENT.Key_AttendanceList]
  eventInstance = EVENT.Event(name, desc, attendants=attendants, preset=event)
  
  eventInstance.removeAttendant(attendantObj[USERID_KEY])
  for tag in attendantObj[USERTAGS_KEY]:
    eventInstance.removeTag(tag)
  
  result = collection.find_one_and_update(
    {EVENT.Key_ID: eventInstance.dictionary[EVENT.Key_ID]},
    {
      '$set': {
        EVENT.Key_Tags : eventInstance.dictionary[EVENT.Key_Tags],
        EVENT.Key_AttendanceList: eventInstance.dictionary[EVENT.Key_AttendanceList],
        EVENT.Key_AttendanceCount: eventInstance.dictionary[EVENT.Key_AttendanceCount],
        EVENT.Key_Statistics : eventInstance.dictionary[EVENT.Key_Statistics]
      }
    }
  )

  if result == None:
    return ERROR_INVALID_SEARCH
  
  success = dict(SUCCESS)
  success[RESULT_KEY] = eventInstance.dictionary
  return success

def isValidPreset(preset):
  if (
    EVENT.Key_Location in preset and
    EVENT.Key_Times in preset
  ):
    location = preset[EVENT.Key_Location]
    if (
      EVENT.Key_Description not in location or
      EVENT.Key_Latitude not in location or 
      EVENT.Key_Longitude not in location
    ):
      return False

    times = preset[EVENT.Key_Times]
    if (
      EVENT.Key_StartTimeStr not in times or 
      EVENT.Key_EndTimeStr not in times or
      EVENT.Key_Date_Parsing not in times
    ):
      return False

    return True
  else:
    return False

def getDateQueryString(year, month, day):
  year = str(year)
  month = str(month)
  day = str(day)

  if len(month) == 1:
    month = '0' + month
  if len(day) == 1:
    day = '0' + day
  
  return "%s-%s-%s*" % (year, month, day)

def getEventFromID(eventID):
  eventIdString = str(eventID)
  result = contains(eventIdString)
  return result

def eventsFromDay(year, month, day):
  dateStr = getDateQueryString(year, month, day)

  results = collection.find({
    "times.startTimeString" : {
      "$regex" : dateStr
    }
  })

  if results == None:
    return None
  
  return list(results)

def eventsFromWeek(year, month, startDay):
  queryDates = []
  orOperator = '$or'
  timeQuery = 'times.startTimeString'
  queryOperator = '$regex'

  for dayOffset in range(7):
    dateObj = datetime(year, month, startDay) + timedelta(days=dayOffset)
    queryDates.append(getDateQueryString(dateObj.year, dateObj.month, dateObj.day))
  
  queryDict = {}
  queryDict[orOperator] = [
    {timeQuery:{queryOperator:date}} for date in queryDates
  ]
  
  results = collection.find(queryDict)

  if results == None:
    return None
  
  return list(results)

def eventsFromRange(centerLat, centerLon, mileRadius):
  andOperator = '$and'
  latitude = 'location.latitude'
  longitude = 'location.longitude'
  greaterThan = '$gte'
  lessThan = '$lte'

  if mileRadius < 0:
    return None
  
  geodosic = GEO.Geolocation(centerLat, centerLon)
  if not geodosic.isValidGeodesic:
    return None

  bounding = geodosic.boundingCoordinates(mileRadius * MILE_TO_KM_RATE)
  minBounds = bounding[GEO.KEY_MINIMUM]
  maxBounds = bounding[GEO.KEY_MAXIMUM]

  queryDict = {
    andOperator : [
      {latitude: { greaterThan:minBounds[GEO.KEY_LAT]} },
      {longitude: { greaterThan:minBounds[GEO.KEY_LON]} },
      {latitude: { lessThan:maxBounds[GEO.KEY_LAT]} },
      {longitude: { lessThan:maxBounds[GEO.KEY_LON]} }
    ]
  }

  results = collection.find(queryDict)
  if results == None:
    return None
  
  return list(results)
