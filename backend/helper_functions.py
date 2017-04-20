from datetime import datetime
from api_functions import getFBUsers, personAvailableOnDate
from urllib.parse import unquote_plus
from printing_functions import debug
import json
import random


def validateUser(sFullName):
  users = getFBUsers()
  
  for person in users:
    if person['name'].lower() == unquote_plus(sFullName.lower()):
      return True
  return False



def getRandomAssignment(bug, dtDue):
  with open('data/user_shares.json', 'r') as f:
    userShares = json.loads(f.read())
  
  now = datetime.utcnow()
  if dtDue < now:
    dtDue = now
  availableUsers = [user for user in userShares if personAvailableOnDate(user['ixPerson'], dtDue)]
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
  