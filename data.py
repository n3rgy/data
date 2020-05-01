#!/usr/bin/python

# Copyright 2020 by Matthew Roderick, n3rgy data ltd.
# All rights reserved.
#
# Sample script to interact with https://data.n3rgy.com service
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OF ANY KIND, either express or implied.
#

import json, cgi, requests, os
import base64, urllib

print "Content-type: text/html\n\n"
form = cgi.FieldStorage()

AUTH="<<go to data.n3rgy.com to register>>"
#url = "https://api.data.n3rgy.com"
url = "https://sandboxapi.data.n3rgy.com"
durl = "/cgi-bin/data.py"
headers = {'Authorization': AUTH}


path_info = os.environ.get("PATH_INFO")
if path_info is None:
	path_info = ""

apiurl = url + path_info

print '<html><body bgcolor="#aaaaaa"><img src="https://data.n3rgy.com/assets/img/logo/logo-light.png"><h1>Smart Meter Data</h1><pre>'
print "<b>n3rgy data API Call: </b> " + apiurl + "<p>"
print "<b>n3rgy data API Response: </b><br>"

# Fetch API data
#
rdata = requests.get( url=apiurl, headers=headers )

# Get JSON from response
#
r = rdata.json()

# Copy JSON to add HTML links
#
h = r.copy()

# convert entries into HTML links (if there are any)
#
i=0
try:
	while i < len(r['entries']):
		h['entries'][i] = "<a href='" + durl + path_info + '/' + r['entries'][i] + "'>" + r['entries'][i] + "</a>"
		i=i+1
except:
	try:
		h['entries'] = "<a href='" + durl + path_info + '/' + str(r['entries'][0]) + "'>" + str(r['entries'][0]) + "</a>"
	except:
		x=1

print json.dumps(h, indent=2)

print "</pre><p>"
print "<h3><a href='..'>back</a></h3></body></html>"