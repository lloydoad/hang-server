import math

EARTH_RADIUS = 6371.01
KEY_MINIMUM = 'minimum'
KEY_MAXIMUM = 'maximum'
KEY_LAT = 'lat'
KEY_LON = 'lon'

class Geolocation:
  radLat = None
  radLon = None

  degLat = None
  degLon = None

  isValidGeodesic = True

  MIN_LAT = math.radians(-90)
  MAX_LAT = math.radians(90)
  MIN_LON = math.radians(-180)
  MAX_LON = math.radians(180)

  def __init__(self, latitude, longitude):
    '''
    @param latitude in degrees float
    @param longitude in degrees float
    '''
    self.radLat = math.radians(latitude)
    self.radLon = math.radians(longitude)
    self.degLat = latitude
    self.degLon = longitude

    self.isValidGeodesic = self.checkBounds()

  def checkBounds(self):
    if (
      self.radLat < self.MIN_LAT or
      self.radLat > self.MAX_LAT or
      self.radLon < self.MIN_LON or 
      self.radLon > self.MAX_LON
    ):
      return False
    return True
  
  def distanceTo(self, lat, lon, radius=EARTH_RADIUS):
    '''
    Computes the great circle distance between this GeoLocation instance
	  and the location argument.
    '''
    if not self.isValidGeodesic:
      return None

    return (
        math.acos
        (
          math.sin(self.radLat) * math.sin(lat) +
          math.cos(self.radLat) * math.cos(radLat) * math.cos(self.radLon - radLon)
        ) 
        * 
        radius
    )

  def boundingCoordinates(self, distance, radius=EARTH_RADIUS):
    '''
    @param distance: range measured in the same unit as radius
    @param radius: radius of big circle, defaults as Earth radius
    measured in km
    '''
    if radius < 0 or distance < 0 or not self.isValidGeodesic:
      return None
    
    # angular distance
    radDist = distance / radius

    minLat = self.radLat - radDist
    maxLat = self.radLat + radDist
    minLon = None
    maxLon = None

    if minLat > self.MIN_LAT and maxLat < self.MAX_LAT:
      delLon = math.asin(math.sin(radDist) / math.cos(self.radLat))

      minLon = self.radLon - delLon
      if minLon < self.MIN_LON:
        minLon += 2 * math.pi
      
      maxLon = self.radLon + delLon
      if maxLon > self.MAX_LON:
        maxLon -= 2 * math.pi
    else:
      minLat = max(minLat, self.MIN_LAT)
      maxLat = max(maxLat, self.MAX_LAT)
      minLon = self.MIN_LON
      maxLon = self.MAX_LAT

    return {
      KEY_MINIMUM : {
        KEY_LAT: math.degrees(minLat),
        KEY_LON: math.degrees(minLon)
      },
      KEY_MAXIMUM : {
        KEY_LAT: math.degrees(maxLat),
        KEY_LON: math.degrees(maxLon)
      }
    }