import requests

def makeRequest(url, params):
  response = None

  try:
    response = requests.get(url, params=params)
  except requests.exceptions.HTTPError as httpErr: 
    errorAlert(httpErr)
    response = None 
  except requests.exceptions.ConnectionError as connErr: 
    errorAlert(connErr)
    response = None 
  except requests.exceptions.Timeout as timeOutErr: 
    errorAlert(timeOutErr)
    response = None 
  except requests.exceptions.RequestException as reqErr: 
    errorAlert(reqErr)
    response = None

  return response 

def errorAlert(message):
  print('Request Error: ', message)