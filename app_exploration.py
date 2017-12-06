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
import time
from flask import Flask
from flask import request
from flask import make_response
import threading
import pdb
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# from thread_test import flag

# from chat_starter import *

# Flask app should start in global layout
app = Flask(__name__)

# scheduler_started = False

curl_cmd = " curl -X POST -H \'Content-type: application/json\' --data \'{\
    \"attachments\": [\
        {\
            \"text\": \"Hi, I am your health agent! Do you need some help?\",\
            \"fallback\": \"welcome\",\
            \"callback_id\": \"welcome\",\
            \"color\": \"#3AA3E3\",\
            \"attachment_type\": \"default\",\
            \"actions\": [\
                {\
                    \"name\": \"button_yes\",\
                    \"text\": \"Continue\",\
                    \"type\": \"button\",\
                    \"value\": \"Hi\"\
                },\
              ]\
             }\
            ]\
}\' https://hooks.slack.com/services/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"


def send_curl():
	os.system(curl_cmd)

@app.route('/webhook', methods=['POST'])
def webhook():
	# if scheduler_started: scheduler.pause()
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
		elif req.get("result").get("parameters")["enjoyability"] == "":
			res = {
				"messages": [
					{
						"type": 2,
						"platform": "slack",
						"title": "Did you enjoy is?",
						"replies": [
							"it was great",
							"meh",
							"I hated it"
						]
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
			enjoyability = req.get("result").get("parameters")["enjoyability"]
			res = {
				"messages": [
					{
						"type" : 0,
						"speech" : "Congrats, we logged the details of your " + activity + \
							" for " + duration + " with " + intensity + " intensity on " + date + "." + \
							" It seems like you did " + enjoyability + " your " + activity + ". " + \
							 "Your coach is notified."
					}
				]
			}
			# reset all parameters. Not sure if this is neccessary, since there is 
			# no output context from log_activity intent
			req.get("result")["parameters"] = {
				"time-period": "", 
				"enjoyability": "", 
				"duration": "",
				"date": "", 
				"activity_intensity": "", 
				"activity_type": ""
			}
			# if not scheduler_started: scheduler.resume()
			# scheduler.pause()
	else: 
		res = {} 
	return res

if __name__ == '__main__':
	# Background scheduler is used to start a chat with a specified user 
	# TODO: Now the scheduler runs every 30 seconds, without considering any other factor.
	scheduler = BackgroundScheduler()
	scheduler.start()
	scheduler.add_job(
    	func=send_curl,
    	trigger=IntervalTrigger(seconds=60),
    	id='printing_job',
    	name='Print date and time every 60 seconds',
    	replace_existing=False)
 	# scheduler.pause()
	port = int(os.getenv('PORT', 5003))
	os.system(curl_cmd)	
	# before the webserver is running, send a CURL request to start the chat
	print("Starting app on port %d" % port)
	app.run(debug=True, port=port, host='0.0.0.0')

 
