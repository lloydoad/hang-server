from os import environ
from uuid import uuid4
from pymongo import MongoClient
import routers.mongo as Database

HANG_SERVER_URI = 'HANG_SERVER_PASSSWORD'
COLLECTION_NAME = 'HangClients'
Key_ID = "_id"

hangPassword = environ.get(HANG_SERVER_URI)
hangPassword = 'not_set' if hangPassword == None else hangPassword

database = Database.database
collection = database[COLLECTION_NAME]

def addNewClient(password):
  if password == None or hangPassword == 'not_set':
    return None
  
  if not password == hangPassword:
    return None
  
  clientId = str(uuid4())
  collection.insert( {Key_ID:clientId} )
  return clientId

def validateClient(clientid):
  if clientid == None:
    return False
  
  clientid = str(clientid)
  if collection.find_one( {Key_ID:clientid} ) == None:
    return False
  return True

  

