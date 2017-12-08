import json
from datetime import datetime
from api_functions import *
from helper_functions import *
from printing_functions import debug
from nocache import nocache
from schema import *

from flask import Flask, request, send_from_directory, jsonify
from flask_api import status
from flask import request
app = Flask(__name__, static_url_path='')



@app.route("/")
def hello():
  return send_from_directory('../views', 'index.html')



@app.route('/<path:path>.js')
def sendJSFile(path):
  return send_from_directory('../public', path + '.js')



@app.route('/<path:path>.css')
def sendCSSFile(path):
  return send_from_directory('../public', path + '.css')



@app.route('/<path:path>.html')
def sendHTMLFile(path):
  return send_from_directory('../public', path + '.html')



@app.route("/userShares", methods=["GET"])
@nocache
def getUserShares():
  userToken = request.args.get("token")
  url = request.args.get('protocol') + request.args.get('url')
  isValid, isAdmin, error, ixPerson = validateToken(getFogBugzConnection(url, userToken))
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  url = request.args.get("url")
  siteData = SiteData.objects(url=url)
  if len(siteData) == 1:
    return jsonify(siteData[0].serialize())

  protocol = request.args.get('protocol')
  #token = request.args.get('ufg_token')
  new_site = SiteData(url=url, is_https = (True if protocol == 'https://' else False), unique_id=generate_uid())
  new_site.save()
  
  return jsonify(new_site.serialize())



@app.route("/updateShares", methods=["POST"])
def updateShares():
  data = request.get_json()
  userToken = data['token']
  url = data['protocol'] + data['url']
  fb = getFogBugzConnection(url, userToken)
  isValid, isAdmin, error, ixPerson = validateToken(fb)
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN

  
  shares = data['data']
  new_user_shares = []
  for item in shares:
    debug(item)
    
    share = UserShare(shares = item['shares'], ixPerson = item['ixPerson'])
    share.save()
    new_user_shares.append(share)
  
  site_data = SiteData.objects(url=data['url'])[0]
  for old_share in site_data.shares:
      old_share.delete()
      
  site_data.shares = new_user_shares
  site_data.save()

  return "OK", status.HTTP_200_OK


@app.route("/updateToken", methods=["POST"])
@nocache
def verifyToken():
  request_data = request.get_json()
  userToken = request_data['token']
  url = request_data['protocol'] + request_data['url']
  isValid, isAdmin, error, ixPerson = validateToken(getFogBugzConnection(url, userToken))
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN
  
  ufg_token = request_data['ufgToken']
  site_data = SiteData.objects(url=request_data['url'])[0]
  site_data.token = ufg_token
  site_data.save()
  
  isValid, isAdmin, error, ixPerson = validateToken(getFogBugzConnection(url, ufg_token))
  return jsonify({'ixPerson': ixPerson}), status.HTTP_200_OK


@app.route("/fogbugzUsers", methods=["GET"])
@nocache
def fogbugzUsers():
  userToken = request.args.get("token")
  url = request.args.get('protocol') + request.args.get('url')
  fb = getFogBugzConnection(url, userToken)
  isValid, isAdmin, error, ixPerson = validateToken(fb)
  if not isAdmin:
    return error, status.HTTP_403_FORBIDDEN

  users = getFBUsers(fb)
  return jsonify(users), status.HTTP_200_OK
  

@app.route('/<path:uid>/case-edit', methods=["POST"])
def hook(uid):
  site_data = SiteData.objects(unique_id=uid)
  if len(site_data) != 1:
    return 'Site token ' + uid + ' not found', status.HTTP_404_NOT_FOUND
  
  site_data = site_data[0]
  url = ('https://' if site_data.is_https else 'http://') + site_data.url
  token = site_data.token
  shares = site_data.shares
  debug(url)
  fb = getFogBugzConnection(url, token)
  is_valid, is_admin, error, ufg_person = validateToken(fb)
  if not is_valid:
    return 'The case assignment API token is invalid. Please update it at https://case-assignment.glitch.me', status.HTTP_403_FORBIDDEN
  events = request.get_json()
  try:
    process_event(events, shares, ufg_person, fb)
    return 'Assigned 1 case'
  except TypeError:
    count = 0
    for event in events:
      if process_event(event, shares, ufg_person, fb):
        count += 1
        
    return 'Assigned ' + str(count) + ' case' + ('s' if count > 1 else '')



if __name__ == "__main__":
  app.run()
