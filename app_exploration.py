# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response
import pdb

# Flask app should start in global layout
app = Flask(__name__)


# activity = ""
# duration = ""
# date = ""

@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)

	print("Request:")
	print(json.dumps(req, indent=4))

	res = processRequest_health(req)

	res = json.dumps(res, indent=4)
	
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r


def processRequest_health(req):

	## TODO: exception handling...
	## 
	# process activity-filling intent
	if req.get("result").get("action") == "activity-filling":
		# ask for duration
		if req.get("result").get("parameters")["duration"] == "":
			activity = req.get("result").get("parameters")["activity_type"]
			res = {
				 "messages": [
        			{
          				"type": 0,
          				"speech": "How long did you " + activity + "? You can say, 10 minutes, an hour etc\n"
        			}
      			]
			}
		# ask for intensity
		elif req.get("result").get("parameters")["activity_intensity"] == "":
			res = {
				"messages": [
					{
						"type": 2,
						"platform": "slack",
						"title": "Great. How intense was the activity? ",
						"replies": [
							"Low",
							"Medium",
							"High"
						]
					}
				]
			}
		elif req.get("result").get("parameters")["date"] == "":
			res = {
				"messages": [
        			{
          				"type": 0,
          				"speech": "Awesome! When was it, yesterday, today, a week ago\n"
        			}
      			]
			}
		# print out all logged information
		else:
			activity = req.get("result").get("parameters")["activity_type"]
			duration = str(req.get("result").get("parameters")["duration"]["amount"]) + \
					   req.get("result").get("parameters")["duration"]["unit"]
			intensity = req.get("result").get("parameters")["activity_intensity"]
			date = req.get("result").get("parameters")["date"]
			res = {
				"messages": [
        			{
          				"type" : 0,
          				"speech" : "Congrats, we logged the details of your " + activity + \
          					" for " + duration + " with " + intensity + " on " + date + ". Your coach is notified." 
          			}
          		]
        	}
	else: 
		res = {} 
	return res

if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	print("Starting app on port %d" % port)

	app.run(debug=True, port=port, host='0.0.0.0')
