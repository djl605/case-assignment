
import os
from datetime import datetime, date
from printing_functions import debug
from fogbugz import FogBugz, FogBugzAPIError
_url = os.environ['FOGBUGZ_URL']
_token = os.environ['FOGBUGZ_ADMIN_TOKEN']
_holidayToken = os.environ['FOGBUGZ_HOLIDAY_TOKEN']
_fb = FogBugz(_url, _token)
_fbHoliday = FogBugz(_url, _holidayToken)



def findCaseDetails(bug):
  try:
    ixBug = int(bug)
  except:
    return None
  
  case = _fb.search(q=ixBug, cols='ixPersonAssignedTo,dtDue')
  if case.cases["count"] != "1":
    return None

  return case.ixPersonAssignedTo.text, case.dtDue.text



def validateMainToken():
  return validateToken(_token)


def validateToken(token):
  fb = FogBugz(_url, token)
  try:
    me = fb.viewPerson()
  except (FogBugzAPIError) as error:
    return False, error.args[0]
  if me.fAdministrator.text != "true":
    return False, "Not an admin"
  return True, "OK"



def getFBUsers():
  users = []
  response = _fb.listPeople()
  for person in response.people:
    users.append({
      "name": person.sFullName.text,
      "ixPerson": int(person.ixPerson.text)
    })
    
  return users



def personAvailableOnDate(ixPerson, dueDate):
  if not timeWithinWorkingSchedule(ixPerson, dueDate):
    debug("person " + str(ixPerson) + " is not available in working schedule")
    return False
  
  holidays = getUpcomingHolidays(ixPerson)
  for holiday in holidays:
    if dueDate > holiday['start'] and dueDate < holiday['end']:
      debug("person " + str(ixPerson) + " has a holiday at this time")
      return False
  return True


_daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
def timeWithinWorkingSchedule(ixPerson, time):
  response = _fb.listWorkingSchedule(ixPerson=ixPerson)
  timeAsFraction = time.hour + (time.minute / 60) + (time.second / (60 * 60))
  return (getattr(response, _daysOfWeek[time.weekday()]).text == 'true' and
          timeAsFraction >= float(response.nWorkdayStarts.text) and
          timeAsFraction <= float(response.nWorkdayEnds.text))
  



def getUpcomingHolidays(ixPerson):
  result = _fbHoliday.listUpcomingHolidays(ixPerson=ixPerson)
  holidays = []
  for holiday in result.holidays:
    holidays.append({
      'start': datetime.strptime(holiday.dtHoliday.text, '%Y-%m-%dT%H:%M:%SZ'),
      'end': datetime.strptime(holiday.dtHolidayEnd.text, '%Y-%m-%dT%H:%M:%SZ')
    })
  return holidays



def assignCase(bug, assignee, ufgUser):
  _fb.assign(ixBug=bug, ixPersonAssignedTo=assignee['ixPerson'], ixPersonEditedBy=ufgUser)
