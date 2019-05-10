from routers.service import makeRequest
from os import environ
import modules.event as EVENT

SEATGEEK_API_RESULT_PER_PAGE = 30
SEATGEEK_API_URL = 'https://api.seatgeek.com/2/events?'
KEY_ENV_SEATGEEK = "SEAT_GEEK_CLIENT_ID"
CLIENT_ID = environ.get(KEY_ENV_SEATGEEK)
SEAT_GEEK_PARAMS = {
  'client_id': '' if CLIENT_ID == None else CLIENT_ID,
  'per_page' : SEATGEEK_API_RESULT_PER_PAGE,
}

KEY_CITY = 'venue.city'
KEY_PAGE = 'page'
KEY_META = 'meta'
KEY_TOTAL = 'total'
KEY_EVENTS = 'events'
KEY_SCORE = 'score'
KEY_TITLE = 'title'
KEY_DATETIME = 'datetime_utc'
KEY_ENDDATETIME = 'enddatetime_utc'
KEY_PARSER = '%Y-%m-%dT%H:%M:%S'
KEY_VENUE = 'venue'
KEY_ID = 'id'
KEY_NAME = 'name'
KEY_LOCATION = 'location'
KEY_LON = 'lon'
KEY_LAT = 'lat'
KEY_TAXONOMIES = 'taxonomies'
KEY_PERFORMERS = 'performers'
KEY_IMAGE = 'image'
KEY_GENRES = 'genres'

def getSeatGeekData(city, targetCount):
  result = []

  page = 1
  SEAT_GEEK_PARAMS[KEY_CITY] = city
  loadedCount = SEATGEEK_API_RESULT_PER_PAGE * page

  while loadedCount <= targetCount:
    SEAT_GEEK_PARAMS[KEY_PAGE] = page
    response = makeRequest(SEATGEEK_API_URL, SEAT_GEEK_PARAMS)

    if response == None or not response.ok:
      return result

    response = response.json()
    totalAvailable = response[KEY_META][KEY_TOTAL]

    eventGroup = response[KEY_EVENTS]
    for event in eventGroup:
      eventInstance = createEventInstance(event)

      if KEY_SCORE in event:
        attendanceCnt = event[KEY_SCORE]
        cnt = int(attendanceCnt * totalAvailable * 2)
        for user in range(0, cnt, 1):
          eventInstance.addAttendant(user)

      result.append(eventInstance)

    page += 1
    loadedCount = SEATGEEK_API_RESULT_PER_PAGE * page
    if loadedCount > totalAvailable:
      break

  return result

def createEventInstance(resp):
  eventDictionary = {
    EVENT.Key_Name : resp[KEY_TITLE],
    EVENT.Key_Description : None,
    EVENT.Key_Times : {
      EVENT.Key_StartTimeStr : resp[KEY_DATETIME],
      EVENT.Key_EndTimeStr : resp[KEY_ENDDATETIME],
      EVENT.Key_Date_Parsing : KEY_PARSER
    },
    EVENT.Key_AttendanceList: [],
    EVENT.Key_ID : resp[KEY_ID],
    EVENT.Key_Location : {
      EVENT.Key_Description : resp[KEY_VENUE][KEY_NAME],
      EVENT.Key_Latitude : resp[KEY_VENUE][KEY_LOCATION][KEY_LAT],
      EVENT.Key_Longitude : resp[KEY_VENUE][KEY_LOCATION][KEY_LON]
    },
    EVENT.Key_Tags : []
  }

  if KEY_TAXONOMIES in resp:
    eventDictionary[EVENT.Key_Tags] = [
      taxonomy[KEY_NAME] for taxonomy in resp[KEY_TAXONOMIES]
    ]

  if KEY_PERFORMERS in resp:
      performers = resp[KEY_PERFORMERS]
      isImageSet = False

      for performer in performers:
        if isImageSet == False and KEY_IMAGE in performer:
          eventDictionary[EVENT.Key_Image] = performer[KEY_IMAGE]
          isImageSet = True

        if not (KEY_GENRES in performer):
          continue

        genres = performer[KEY_GENRES]
        for genre in genres:
          eventDictionary[EVENT.Key_Tags].append(genre[KEY_NAME])
  
  return EVENT.Event(
    eventDictionary[EVENT.Key_Name],
    None,
    attendants=[],
    preset=eventDictionary
  )

  