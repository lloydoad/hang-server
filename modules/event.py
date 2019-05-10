from random import randrange
from datetime import datetime
from bson import ObjectId
import json, operator

Key_Name = "name"
Key_ID = "_id"
Key_Location = "location"
Key_Description = "description"
Key_Latitude = "latitude"
Key_Longitude = "longitude"
Key_Times = "times"
Key_StartTimeStr = "startTimeString"
Key_EndTimeStr = "endTimeString"
Key_Date_Parsing = "parsingString"
Key_TimeDuration = "duration"
Key_Tags = "tags"
Key_Statistics = "statistics"
Key_ID = "_id"
Key_Color = "color"
Key_Image = "imageUrl"
Key_AttendanceCount = "attendanceTotal"
Key_AttendanceList = "attendanceList"

DEFAULT_PARSING_STRING = '%a, %d %b %Y %H:%M:%S %z'

class Event:
  def __init__(self, name, desc, attendants=[], preset=None):
    self.initInitialDictionaryState(name, desc, attendants=attendants)

    if not preset == None:
      self.initObjectID(preset)
      self.initLocation(preset)
      self.initTime(preset)
      self.initTags(preset)
    
    # generate color if not available
    if Key_Color in preset:
      self.dictionary[Key_Color] = preset[Key_Color]
    else:
      self.dictionary[Key_Color] = self.generateRandomColor()
    
    # add image if available
    if Key_Image in preset:
      self.dictionary[Key_Image] = preset[Key_Image]

  def __repr__(self):
    return "Single Event Instance - %s" % self.dictionary[Key_Name]

  def __str__(self):
    return self.getJsonRepresentation()

  def initInitialDictionaryState(self, name, desc, attendants=[]):
    self.dictionary = {
      Key_ID : str(ObjectId()),
      Key_Name : name,
      Key_Description : desc,
      Key_AttendanceList : list(attendants),
      Key_AttendanceCount : len(attendants),
      Key_Location : {
        Key_Description : None,
        Key_Latitude : None,
        Key_Longitude : None
      },
      Key_Times : {
        Key_StartTimeStr : None,
        Key_EndTimeStr : None,
        Key_TimeDuration : None,
        Key_Date_Parsing : None
      },
      Key_Tags : None,
      Key_Color : None,
      Key_Image : None,
      Key_Statistics : None
    }
  
  def initObjectID(self, preset):
    # Add id if available
    if Key_ID in preset:
      uid = str(preset[Key_ID])
      self.dictionary[Key_ID] = uid 

  def initLocation(self, preset):
    # Add location if available
    if Key_Location in preset:
      locationObj = preset[Key_Location]
      if (
      Key_Description in locationObj and
      Key_Latitude in locationObj and
      Key_Longitude in locationObj
      ):
        self.setLocation(
          locationObj[Key_Description],
          locationObj[Key_Latitude],
          locationObj[Key_Longitude]
        )
  
  def initTime(self, preset):
    # Add time if available
    if Key_Times in preset:
      timesObj = preset[Key_Times]
      if (
      Key_StartTimeStr in timesObj and
      Key_EndTimeStr in timesObj
      ):
        parse = timesObj[Key_Date_Parsing] if Key_Date_Parsing in timesObj else DEFAULT_PARSING_STRING
        self.setTime(
          timesObj[Key_StartTimeStr],
          timesObj[Key_EndTimeStr],
          parser=parse
        )
  
  def initTags(self, preset):
    # Add tags if available
    if Key_Tags in preset and isinstance(preset[Key_Tags], list):
      tagList = list(preset[Key_Tags])
      for tag in tagList:
        self.addTag(str(tag))
    elif Key_Tags in preset and isinstance(preset[Key_Tags], dict):
      self.dictionary[Key_Tags] = preset[Key_Tags]
    else:
      self.dictionary[Key_Tags] = {}
      self.calculateStats()

  def addAttendant(self, uuid):
    if uuid in self.dictionary[Key_AttendanceList]:
      return
    
    self.dictionary[Key_AttendanceList].append(uuid)
    self.dictionary[Key_AttendanceCount] += 1

  def removeAttendant(self, uuid):
    if uuid not in self.dictionary[Key_AttendanceList]:
      return
    
    self.dictionary[Key_AttendanceList].remove(uuid)
    self.dictionary[Key_AttendanceCount] -= 1
  
  def addTag(self, tagString):
    if self.dictionary[Key_Tags] == None:
      self.dictionary[Key_Tags] = {}

    tagString = str(tagString).lower().strip()
    tags = dict(self.dictionary[Key_Tags])
    if tagString in tags:
      tags[tagString] = tags[tagString] + 1
    else:
      tags[tagString] = 1

    self.dictionary[Key_Tags] = tags
    self.calculateStats()

  def removeTag(self, tagString):
    if self.dictionary[Key_Tags] == None or len(self.dictionary[Key_Tags]) == 0:
      return
    
    tagString = str(tagString).lower().strip()
    tags = dict(self.dictionary[Key_Tags])
    if tagString not in tags:
      return
    
    try:
      del tags[tagString]
    except KeyError:
      print('Key Delete Error')
    
    self.dictionary[Key_Tags] = tags
    self.calculateStats()
    return

  def getJsonRepresentation(self):
    return json.dumps(self.dictionary)

  def generateRandomColor(self):
    return [
      randrange(0,255,1) / 255,
      randrange(0,255,1) / 255,
      randrange(0,255,1) / 255
    ]

  def calculateStats(self):
    if self.dictionary[Key_Tags] == None:
      return

    totalBias = 0
    sortedTags = sorted(self.dictionary[Key_Tags].items(), key=operator.itemgetter(1))[-6:]
    statistics= {}

    for tag in sortedTags:
      totalBias += int(tag[1])
    
    for tag in sortedTags:
      statistics[tag[0]] = (tag[1] / totalBias) * 100

    self.dictionary[Key_Statistics] = statistics

  def setLocation(self, description, latitude, longitude):
    self.dictionary[Key_Location] = {
      Key_Description: description,
      Key_Latitude: latitude,
      Key_Longitude: longitude
    }

  def setTime(self, startTimeStr, endTimeStr, parser=DEFAULT_PARSING_STRING):
    startDateObj = None
    endDateObj = None
    timeDifference = None

    if not startTimeStr == None and not parser == None:
      startDateObj = datetime.strptime(startTimeStr, parser)

    if not endTimeStr == None and not parser == None:
      endDateObj = datetime.strptime(endTimeStr, parser)
    
    if not (endDateObj == None) and not (startDateObj == None):
      timeDifference = (endDateObj - startDateObj).total_seconds()

    self.dictionary[Key_Times] = {
      Key_StartTimeStr: startTimeStr,
      Key_EndTimeStr: endTimeStr,
      Key_TimeDuration: timeDifference,
      Key_Date_Parsing: parser
    }
