#!/usr/bin/python


# Copyright 2020 by Matthew Roderick, n3rgy data ltd.
# All rights reserved.
#
# Sample script to interact with https://data.n3rgy.com service
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES ANY KIND, either express or implied.
#

import requests, json, time, csv, cgi, os
import argparse, sys

# CGI
#
print "Content-type: text/plan\n\n"
form = cgi.FieldStorage()

#
# fetch cookies for apiKey and service type
#
url = "https://sandboxapi.data.n3rgy.com"
AUTH = ""
handler = {}
if 'HTTP_COOKIE' in os.environ:
        cookies = os.environ['HTTP_COOKIE']
        cookies = cookies.split('; ')
        for cookie in cookies:
                cookie = cookie.split('=')
                handler[cookie[0]] = cookie[1]

try:
	if handler['n3rgyAuthorization']:
		(apiSrv,AUTH) = handler['n3rgyAuthorization'].split(':')
except:
	print "no apiKey\n"
	exit


#
url="https://api.data.n3rgy.com/read-inventory"
headers= {'Authorization':AUTH}
postdata={}
outputfile=''
privacy="true"


if apiSrv == "sandbox":
	print "Sandbox inventory queries are not supported\n"
	exit



# CGI
#

try:
	form["mpxn"].value
except:
	x=1
else:
	postdata['mpxns'] = [ form["mpxn"].value, "" ]

try:
	form["device"].value
except:
	x=1
else:
	postdata['deviceIds'] = [ form["device"].value, "" ]

try:
	form["urpn"].value
except:
	x=1
else:
	postdata['uprns'] = [ form["urpn"].value, "" ]


privacy = form['privacy'].value
	

#
# Read CPL 
#
#


#
# Loads cpl english description (processed from CPL change log)
#
reader = csv.reader(open('CPL/CPL-descriptions.csv'))
cpldesc = {}
for row in reader:
	key = row[0]
	cpldesc[key] = row[1]
#	print key + " cpldesc " + cpldesc[key]

#
# Load CPL from CSV export (download from https://smartenergycodecompany.co.uk/central-products-list/)
#
cplreader = csv.reader(open('CPL/CPL-1-1.189.csv'))
cpl = {}
for row in cplreader:
	key = row[8]
#	print row[8] + " cpl " + row[1]
	cpl[key] = { "deviceEntry" : row[1], "deviceDesc" : row[3], "deviceModelHwVersion" : row[8], "deviceModelFwVersion" : row[9] }
#	print key + " cpl " + str(cpl[key])



#print json.dumps(postdata, indent=2)
#
# real work, submit request
#
rdata = requests.post( url, data=json.dumps(postdata), headers=headers )

#print str(rdata)

fetchurl = rdata.json()["uri"]

#
# keep requesting until file is available
#
sys.stderr.write(".")
time.sleep(5)
seconds=5
sys.stderr.write(".")

while 1:
	rrdata = requests.get ( url=fetchurl )
	try:
		inv_rep = rrdata.json()
	except Exception:
		time.sleep(5)
		seconds=seconds+5
		if seconds % 60 == 0:  
			sys.stderr.write("+")
		else:
			sys.stderr.write(".")
	else:
		break

print "\nJob duration: " + str(seconds) + " seconds\n"


#for i in inv_rep["devices"]:
#	print i["deviceModel"]


#
# Add CPL descriptions to report output
#
data = rrdata.json()["result"]

for a in data:
	try:
		for b in a["devices"]:
#			print b["deviceModel"] + " - " + cpl[b["deviceModel"]]["deviceEntry"] + " - " + cpldesc[cpl[b["deviceModel"]]["deviceEntry"]]
			b["X-cpl-DeviceDesc"] = cpldesc[cpl[b["deviceModel"]]["deviceEntry"]]

			b["X-cpl-DeviceType"] = cpl[b["deviceModel"]]["deviceDesc"]
			b["X-cpl-ModelHardwardVersion"] = cpl[b["deviceModel"]]["deviceModelHwVersion"]
			b["X-cpl-ModelFirmwareVersion"] = cpl[b["deviceModel"]]["deviceModelFwVersion"]

			if privacy != "false":
				b["propertyFilter"]["addressIdentifier"] = "xxxx"
				b["propertyFilter"]["postCode"] = b["propertyFilter"]["postCode"][0:3]
				b["uprn"] = "xxxx"

			x=1
	except:
		x=1


print json.dumps(data, indent=2)

