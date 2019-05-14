const tagContainer = document.getElementsByClassName('added-tags-container')[0]
const attendantPanel = document.getElementById('attendantPanel')
const simplePanel = document.getElementById('simplePanel')
const loadingSymbol = document.getElementById('loader')
const resultPanel = document.getElementById('resultPanel')

function presentResult(result) {
  resultPanel.getElementsByClassName('call-result')[0].innerText = result
  resultPanel.style.display = ''
}

function ajaxRequest(url, data, success, failure) {
  $.ajax({
    url: url,
    data: data,
    type: 'GET',
    success: success,
    error: failure
  })
}

// big panel
const ADD_ATTENDANT_KEY = 'ADD ATTENDANT'
const REMOVE_ATTENDANT_KEY = 'REMOVE ATTENDANT'
// small panel
const TOGGLE_SOURCE_KEY = 'TOGGLE SOURCE'
const DELETE_EVENT_KEY = 'DELETE EVENT'
const UPDATE_DATABASE = 'UPDATE DATABASE'
// require loading
const CLEAN_DATABASE = 'CLEAN DATABASE'
const GENERATE_CLIENT = 'GENERATE CLIENT'

function closePanel(panel) {
  panel.style.display = 'none'
}

// attendant variables
var isAddingAttendant = false
var addedTags = []

function openAttendantPanel(button) {
  if(button.innerText === ADD_ATTENDANT_KEY) {
    isAddingAttendant = true
  } else if (button.innerText === REMOVE_ATTENDANT_KEY){
    isAddingAttendant = false
  }

  attendantPanel.style.display = ""
}

function addTag(tag) {
  if(tag.value !== '') {
    addedTags.push(tag.value)
    newTag = document.getElementById('tagTemplate').cloneNode(true)
    newTag.style.display = ''
    newTag.getElementsByClassName('added-tag-text')[0].innerText = tag.value
    tag.value = ''
    tagContainer.appendChild(newTag)
  }
}

function removeTag(tag) {
  tag.remove()
  addedTags = addedTags.filter((value, index, arr) => {
    return value !== tag.getElementsByClassName('added-tag-text')[0].innerText
  })
}

function postEventAndTags(attendantEventid, uuidOne) {
  if(attendantEventid.value === '' || uuidOne.value === '') {
    return
  }

  eventId = attendantEventid.value
  uuid = uuidOne.value
  url = isAddingAttendant ? '/addAttendant' : '/removeAttendant'
  data = {
    'clientid': 'e3cf8466-c726-4c2c-9f5d-a95e097902da',
    'uuid' : uuid,
    'eventid' : eventId,
    'tags' : addedTags
  }

  loadingSymbol.style.display = ''
  ajaxRequest(
    url,
    data,
    (response) => {
      presentResult(JSON.stringify(response))
      attendantEventid.value = ''
      uuidOne.value = ''
      loadingSymbol.style.display = 'none'
    },
    (xhr, status, error) => {
      presentResult(status + " " + xhr.responseText)
      loadingSymbol.style.display = 'none'
    }
  )
}

var isDeletingOverToggling = false
var isUpdatingDatabase = false

function openShorterPanel(button) {
  title = 'Title'
  if(button.innerText === TOGGLE_SOURCE_KEY) {
    isDeletingOverToggling = false
    title = 'Source ID'
  } else if(button.innerText === DELETE_EVENT_KEY) {
    isDeletingOverToggling = true
    title = 'Event ID'
  }

  if(button.innerText === UPDATE_DATABASE) {
    isUpdatingDatabase = true
    title = 'City Update'
  } else {
    isUpdatingDatabase = false
  }

  simplePanel.style.display = ''
  simplePanel.getElementsByClassName('panelTitle')[0].innerText = title
}

function postEventActionOrSourceChange(uuidElement) {
  if(uuidElement.value !== '') {
    uuid = uuidElement.value
    uuidElement.value = ''
    loadingSymbol.style.display = ''
    url = ''
    data = {
      'clientid': 'e3cf8466-c726-4c2c-9f5d-a95e097902da'
    }

    if(isDeletingOverToggling) {
      url = '/delete'
      data['eventid'] = uuid
    } else {
      url = '/toggleDatabase'
      data['switch'] = uuid
    }

    if(isUpdatingDatabase) {
      url = '/update'
      data['city'] = uuid
    }

    ajaxRequest(
      url,
      data, 
      (response) => {
        presentResult(response)
        loadingSymbol.style.display = 'none'
      },
      (xhr, status, error) => {
        presentResult(status + " " + xhr.responseText)
        loadingSymbol.style.display = 'none'
      }
    )
  }
}

function postInstantChanges(button) {
  url = button.innerText === CLEAN_DATABASE ? '/clean' : '/newclient'
  data = {
    'clientid': 'e3cf8466-c726-4c2c-9f5d-a95e097902da'
  }

  if(button.innerText === GENERATE_CLIENT) {
    data['password'] = '72cd8eef-d8da-4b97-9334-8e35af0a6fbd'
  }

  ajaxRequest(
    url,
    data, 
    (response) => {
      presentResult(response)
      loadingSymbol.style.display = 'none'
    },
    (xhr, status, error) => {
      presentResult(status + " " + xhr.responseText)
      loadingSymbol.style.display = 'none'
    }
  )
}