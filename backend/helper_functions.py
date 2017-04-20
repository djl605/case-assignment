from datetime import datetime
from api_functions import *
from urllib.parse import unquote_plus
from printing_functions import debug
import json
import random
import string


def validateUser(sFullName, fb):
  users = getFBUsers(fb)
  
  for person in users:
    if person['name'].lower() == unquote_plus(sFullName.lower()):
      return True
  return False



def getRandomAssignment(bug, dtDue, userShares, fb):
  now = datetime.utcnow()
  if dtDue < now:
    dtDue = now
  availableUsers = [user.serialize() for user in userShares if personAvailableOnDate(user['ixPerson'], dtDue, fb)]
  debug('available users are ' + str(availableUsers))
  sum = sumShares(availableUsers)
  if sum == 0:
    return None
  selection = random.randrange(sum)
  for user in availableUsers:
    if user['shares'] > selection:
      return user
    selection -= user['shares']
  
  

  
def sumShares(userShares):
  sum = 0
  for user in userShares:
    sum += user['shares']
    
  return sum
  
  
def generate_uid():
  choices = string.ascii_lowercase + string.digits
  uid = ''
  for i in range(16):
    uid += random.choice(choices)
    
  return uid

  
def process_event(event, shares, fb):
  if not event['eventtype'].lower().startswith('case'):
    return
  
  bug = event['casenumber']
  
  ufg_person = getUfgUser(fb)
  ixPersonAssignedTo, sDtDue = findCaseDetails(bug, fb)
  debug('ufg_person = ' + str(ufg_person) + ' ixPersonAssignedTo = ' + str(ixPersonAssignedTo))
  if ixPersonAssignedTo == None:
    return False
  if int(ixPersonAssignedTo) != ufg_person:
    return False
  
  try:
    dtDue = datetime.strptime(sDtDue, '%Y-%m-%dT%H:%M:%SZ')
  except:
    # No due date set for this case so don't assign.
    return False

  assignee = getRandomAssignment(bug, dtDue, shares, fb)
  
  if not assignee:
    # Nobody available to receive case
    return False
  
  debug("Assigning case " + str(bug) + " to " + str(assignee))
  assignCase(bug, assignee, fb)
  return True