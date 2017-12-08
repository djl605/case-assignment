
from datetime import datetime, date
from printing_functions import debug
from fogbugz import FogBugz, FogBugzAPIError


def getFogBugzConnection(url, token):
  return FogBugz(url, token)

def findCaseDetails(bug, fb):
  try:
    ixBug = int(bug)
  except:
    return None
  
  case = fb.search(q=ixBug, cols='ixPersonAssignedTo,dtDue')
  if case.cases["count"] != "1":
    return None

  return case.ixPersonAssignedTo.text, case.dtDue.text


# Returns Tuple: (isValid, isAdmin, errorMessage, ixPerson)
def validateToken(fb):
  try:
    me = fb.viewPerson()
  except (FogBugzAPIError) as error:
    return False, False, error.args[0], -1
  if me.fAdministrator.text != "true":
    return True, False, "Not an admin", int(me.ixPerson.text)
  return True, True, "OK", int(me.ixPerson.text)



def getFBUsers(fb):
  response = fb.listPeople(fIncludeVirtual='1', fIncludeNormal='1')
  users = [{
      "name": person.sFullName.text,
      "ixPerson": int(person.ixPerson.text)
    } for person in response.people]
    
  return users



def personAvailableOnDate(ixPerson, dueDate, fb):
  if not timeWithinWorkingSchedule(ixPerson, dueDate, fb):
    debug("person " + str(ixPerson) + " is not available in working schedule")
    return False
  
  holidays = getUpcomingHolidays(ixPerson, fb)
  for holiday in holidays:
    if dueDate > holiday['start'] and dueDate < holiday['end']:
      debug("person " + str(ixPerson) + " has a holiday at this time")
      return False
  return True


# Fun fact: In Python's date.weekday() function, Monday is 0
_daysOfWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
def timeWithinWorkingSchedule(ixPerson, time, fb):
  response = fb.listWorkingSchedule(ixPerson=ixPerson)
  timeAsFraction = time.hour + (time.minute / 60) + (time.second / (60 * 60))
  return (getattr(response, _daysOfWeek[time.weekday()]).text == 'true' and
          timeAsFraction >= float(response.nWorkdayStarts.text) and
          timeAsFraction <= float(response.nWorkdayEnds.text))
  



def getUpcomingHolidays(ixPerson, fb):
  result = fb.listUpcomingHolidays(ixPerson=ixPerson)
  holidays = []
  for holiday in result.holidays:
    holidays.append({
      'start': datetime.strptime(holiday.dtHoliday.text, '%Y-%m-%dT%H:%M:%SZ'),
      'end': datetime.strptime(holiday.dtHolidayEnd.text, '%Y-%m-%dT%H:%M:%SZ')
    })
  return holidays



def assignCase(bug, assignee, fb):
  fb.assign(ixBug=bug, ixPersonAssignedTo=assignee['ixPerson'])
