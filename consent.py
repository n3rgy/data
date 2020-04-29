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

import json, cgi, requests
import base64, urllib


def n3rgyGetConsentSession(apiKey, mpxn, consentType):
	#surl="https://consentsandbox.data.n3rgy.com/consents/sessions?consentType=" + consentType
	surl="https://consent.data.n3rgy.com/consents/sessions?consentType=" + consentType
	# uncomment for live

	spostdata={}
	spostdata['mpxn'] = mpxn
	spostdata['apiKey'] = apiKey
	headers=''

	rdata = requests.post( url=surl, data=json.dumps(spostdata), headers=headers)
	sessionId = rdata.json()["sessionId"]

	return(sessionId);

def n3rgyGetConsentURL(sessionId, mpxn, consentType, returnUrl, errorUrl):
	#burl = "https://portal-consent-sandbox.data.n3rgy.com/consent/"
	burl = "https://portal-consent.data.n3rgy.com/consent/"
	# uncomment for live

	qs = "sessionId=" + sessionId + "&mpxn=" + mpxn + "&consentType=" + consentType + "&returnUrl=" + returnUrl + "&errorUrl=" + errorUrl
	eqs = urllib.quote_plus(base64.b64encode(qs))

	return(burl + eqs);
	
def n3rgyWithdrawConsent(apiKey, mpxn):
	wurl = "https://consent.data.n3rgy.com/consents/withdraw-consent"

	wurl=wurl + "?mpxn=" + mpxn

	headers= {'Authorization': apiKey}

	rdata = requests.put( url=wurl, headers=headers)

	try:
		rdata.json()['errors']
	except:
		yay = { 'code' : 204, 'message' : 'Success! Sorry to see you go'} 
		return(yay)
	else:
		return(rdata.json()['errors'])

#
# Set up consent parameters to get session key
#
# consent type (ct): ihdmac_4, ihdmac_full or cin; ihdmac_4 is recommended
# returnUrl (ru): Return URL if successful
# errorUrl (eu): Return URL if failure
#
ct = "ihdmac_4"
ru = "http://flatpi/sm"
eu = "https://flatpi/sm"
AUTH="<<sign up at data.n3rgy.com for your license>>"


print "Content-type: text/html\n\n"
form = cgi.FieldStorage()


if form.getvalue('action') == "Consent":
	# Get Session Id
	#
	sid = n3rgyGetConsentSession(AUTH, form.getvalue('mpxn'), ct)

	print "Got sessionId: " + sid + "<p>\n"

	# Get Consent URL
	#
	consentURL = n3rgyGetConsentURL(sid, form.getvalue('mpxn'), ct, ru, eu)

	print "\n<p>Got consentURL: \n" + consentURL

	print '<h2><a href=' + consentURL + '>click here to go</a></h2>'
else:

	print "Withdrawing consent for: " + form.getvalue('mpxn') + "<p>\n"
	result = n3rgyWithdrawConsent(AUTH, form.getvalue('mpxn'))

	print json.dumps(result)

	print "<p><a href='/sm'>back</a>"
