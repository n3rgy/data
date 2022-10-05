#!/usr/bin/python

# Copyright 2022 by Matthew Roderick, n3rgy data ltd.
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

def n3rgyGetConsentSession(apiKey, mpxn, consentType, apiSrv):

	if (apiSrv == 'live' ):
		surl = "https://consent-v2.data.n3rgy.com/consents/session?consentType=" + consentType
	else:
		surl = "https://consentsandbox-v2.data.n3rgy.com/consents/session?consentType=" + consentType

	spostdata={}
	spostdata['mpxn'] = mpxn
	spostdata['getHistoryData'] = 'true'
	spostdata['moveInDate'] = '2018-01-01'


	headers= {'x-api-key': apiKey, 'Content-type' : 'application/json'}

	rdata = requests.post( url=surl, data=json.dumps(spostdata), headers=headers)
	try:
		sessionId = rdata.json()["sessionId"]
	except:
		print "<pre>"
		print "URL: " + surl
		print "Headers: " + json.dumps(headers)
		print "Body: " + json.dumps(spostdata)
		print "Return status: " + str(rdata.status_code)
		print "Return reason: " + rdata.reason
		print "</pre>"

	return(sessionId);

def n3rgyGetConsentURL(sessionId, mpxn, consentType, returnUrl, errorUrl, apiSrv, hp):

	if (apiSrv == 'live' ):
		burl = "https://portal-consent-v2.data.n3rgy.com/consent/"
	else:
		burl = "https://portal-consent-sandbox-v2.data.n3rgy.com/consent/"

	qs = "sessionId=" + sessionId + "&mpxn=" + mpxn + "&consentType=" + consentType + "&returnUrl=" + returnUrl + "&errorUrl=" + errorUrl + "&highPriority=" + hp 
	eqs = urllib.quote_plus(base64.b64encode(qs))

	return(burl + eqs);
	
def n3rgyWithdrawConsent(apiKey, mpxn, apiSrv):

	if (apiSrv == 'live' ):
		wurl = "https://consent-v2.data.n3rgy.com/consents/withdraw-consent"
	else:
		wurl = "https://consentsandbox-v2.data.n3rgy.com/consents/withdraw-consent"

	#wurl = url + "/consents/withdraw-consent"
	wurl = wurl + "?mpxn=" + mpxn

	#headers= {'x-api-key': apiKey}
	headers= {'x-api-key': apiKey, 'Content-type' : 'application/json'}

	rdata = requests.put( url=wurl, headers=headers)

	try:
		rdata.json()['errors']
	except:
		yay = { 'code' : 204, 'message' : 'Success! Sorry to see you go'} 
		return(yay)
	else:
		return(rdata.json()['errors'])

def n3rgyAddTrustedConsent(apiKey, mpxn, evidence, moveInDate, apiSrv):

	if (apiSrv == 'live' ):
		turl = "https://consent-v2.data.n3rgy.com/consents/add-trusted-consent"
	else:
		turl = "https://consentsandbox-v2.data.n3rgy.com/consents/add-trusted-consent"

        tpostdata={}
        tpostdata['mpxn'] = mpxn
        tpostdata['evidence'] = evidence
        tpostdata['moveInDate'] = moveInDate
        tpostdata['highPriority'] = "True"

        headers=''

	headers= {'x-api-key': apiKey, 'Content-type' : 'application/json'}

        rdata = requests.post( url=turl, data=json.dumps(tpostdata), headers=headers)

	print str(rdata)

        try:
                rdata.json()['errors']
        except:
                yay = { 'code' : 204, 'message' : 'Success! you now have access'}
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
hp = "true"
ru = "http://homebrew.n3rgy.com/data-v2"
eu = "http://errorpage.com"
AUTH=""

print "Content-type: text/html\n\n"
print "<html><head><link rel='stylesheet' href='/n3rgy.css'></head><body>"


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

if handler['n3rgyAuthorizationv2']:
        (apiSrv,AUTH) = handler['n3rgyAuthorizationv2'].split(':')


form = cgi.FieldStorage()


if form.getvalue('action') == "Consent":
	# Get Session Id
	#
	sid = n3rgyGetConsentSession(AUTH, form.getvalue('mpxn'), ct, apiSrv)

	print "<center><h2>Behind the scenes...</h2>\n"
	print "Setting up session key for this consent journey...<p>\n"
	print "Got unique key: <i>" + sid + "</i><p><br><br>\n"

	# Get Consent URL
	#
	consentURL = n3rgyGetConsentURL(sid, form.getvalue('mpxn'), ct, ru, eu, apiSrv, hp)

	print "<p>Clock link below to continue to consent URL<p>"

	print "<pre><i>" + consentURL + "</i></pre>"
	print "<pre>[ " + base64.b64decode(urllib.unquote(consentURL.split("/")[-1])) + " ]</pre>"

	print '<h2><a href=' + consentURL + '>click here to go</a></h2></center>'

elif form.getvalue('action') == "TConsent":

	if apiSrv == "live":
		print "not supported<p>"
        	#print "Adding Trusted consent on " + apiSrv + " for: " + form.getvalue('mpxn') + " on " + apiSrv + "<p>\n"
        	#result = n3rgyAddTrustedConsent(AUTH, form.getvalue('mpxn'), "Test consent", "2013-01-01", apiSrv)
	else:
        	print "Adding Trusted consent on " + apiSrv + " for: " + form.getvalue('mpxn') + " on " + apiSrv + "<p>\n"
        	result = n3rgyAddTrustedConsent(AUTH, form.getvalue('mpxn'), "Sandbox consent", "2013-01-01", apiSrv)

        print json.dumps(result)

else:

	print "Withdrawing consent on " + apiSrv + " for: " + form.getvalue('mpxn') + "<p>\n"
	result = n3rgyWithdrawConsent(AUTH, form.getvalue('mpxn'), apiSrv)

	print json.dumps(result)

print "<p><a href='/data-v2'>back</a></body></html>"
