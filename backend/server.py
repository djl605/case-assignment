import os
import json
from datetime import datetime
from api_functions import *
from helper_functions import *
from printing_functions import debug
from nocache import nocache

from flask import Flask, request, send_from_directory, jsonify
from flask_api import status
from flask import request
app = Flask(__name__, static_url_path='')



@app.route("/")
def hello():
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  return send_from_directory('../views', 'index.html')



@app.route('/<path:path>.js')
def sendJSFile(path):
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  return send_from_directory('../public', path + '.js')



@app.route('/<path:path>.css')
def sendCSSFile(path):
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  return send_from_directory('../public', path + '.css')



@app.route('/<path:path>.html')
def sendHTMLFile(path):
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  return send_from_directory('../public', path + '.html')



@app.route("/userShares", methods=["GET"])
@nocache
def getUserShares():
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  userToken = request.args.get("token")
  isAdmin, error = validateToken(userToken)
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  return send_from_directory('../.data', 'user_shares.json')



@app.route("/updateShares", methods=["POST"])
def updateShares():
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  data = request.get_json()
  userToken = data['token']
  isAdmin, error = validateToken(userToken)
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN

  
  shares = data['data']
  for item in shares:
    debug(item['name'])
    if not validateUser(item['name']):
      return item['name'] + " is not a valid FogBugz user. If this user has been entered recently, you may need to hit the updateStoredUsers page.", status.HTTP_400_BAD_REQUEST
  
  with open('.data/user_shares.json', 'w') as f:
    f.write(json.dumps(shares))
    
  return "OK", status.HTTP_200_OK



@app.route("/fogbugzUsers", methods=["GET"])
@nocache
def fogbugzUsers():
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  userToken = request.args.get("token")
  isAdmin, error = validateToken(userToken)
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN

  
  users = getFBUsers()
  
  return jsonify(users), status.HTTP_200_OK



@app.route("/hooks")
def handleHook():
  isAdmin, error = validateMainToken()
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  bug = request.args.get('ixBug')
  ixPersonAssignedTo, sDtDue = findCaseDetails(bug)
  if ixPersonAssignedTo == None:
    return 'Invalid ixBug provided', status.HTTP_400_BAD_REQUEST
  if ixPersonAssignedTo != os.environ["UFG_USER"]:
    return "Case is not assigned to " + os.environ["UFG_USER"], status.HTTP_200_OK
  
  try:
    dtDue = datetime.strptime(sDtDue, '%Y-%m-%dT%H:%M:%SZ')
  except:
    return "No due date set", status.HTTP_200_OK
  assignee = getRandomAssignment(bug, dtDue)
  
  if not assignee:
    return "Nobody available to receive the case", status.HTTP_200_OK
  
  debug("Assigning case " + str(bug) + " to " + str(assignee))
  assignCase(bug, assignee, ixPersonAssignedTo)
  return "OK", status.HTTP_200_OK
  
  
  




if __name__ == "__main__":
  app.run()
