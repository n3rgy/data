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

def n3rgyGetConsentSession(apiKey, mpxn, consentType, apiSrv):

	if (apiSrv == 'live' ):
		surl = "https://consent.data.n3rgy.com/consents/sessions?consentType=" + consentType
	else:
		surl = "https://consentsandbox.data.n3rgy.com/consents/sessions?consentType=" + consentType

	spostdata={}
	spostdata['mpxn'] = mpxn
	spostdata['apiKey'] = apiKey
	headers=''

	rdata = requests.post( url=surl, data=json.dumps(spostdata), headers=headers)
	sessionId = rdata.json()["sessionId"]

	return(sessionId);

def n3rgyGetConsentURL(sessionId, mpxn, consentType, returnUrl, errorUrl, apiSrv):

	if (apiSrv == 'live' ):
		burl = "https://portal-consent.data.n3rgy.com/consent/"
	else:
		burl = "https://portal-consent-sandbox.data.n3rgy.com/consent/"

	qs = "sessionId=" + sessionId + "&mpxn=" + mpxn + "&consentType=" + consentType + "&returnUrl=" + returnUrl + "&errorUrl=" + errorUrl
	eqs = urllib.quote_plus(base64.b64encode(qs))

	return(burl + eqs);
	
def n3rgyWithdrawConsent(apiKey, mpxn, apiSrv):

	if (apiSrv == 'live' ):
		wurl = "https://consent.data.n3rgy.com/consents/withdraw-consent"
	else:
		wurl = "https://consentsandbox.data.n3rgy.com/consents/withdraw-consent"

	#wurl = url + "/consents/withdraw-consent"
	wurl = wurl + "?mpxn=" + mpxn

	headers= {'Authorization': apiKey}

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
		turl = "https://consent.data.n3rgy.com/consents/add-trusted-consent"
	else:
		turl = "https://consentsandbox.data.n3rgy.com/consents/add-trusted-consent"

        tpostdata={}
        tpostdata['mpxn'] = mpxn
        tpostdata['evidence'] = evidence
        tpostdata['moveInDate'] = moveInDate
        tpostdata['apiKey'] = apiKey
        tpostdata['highPriority'] = "True"

        headers=''

        headers= {'Authorization': apiKey}

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
ru = "http://homebrew.n3rgy.com"
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

if handler['n3rgyAuthorization']:
        (apiSrv,AUTH) = handler['n3rgyAuthorization'].split(':')


form = cgi.FieldStorage()


if form.getvalue('action') == "Consent":
	# Get Session Id
	#
	sid = n3rgyGetConsentSession(AUTH, form.getvalue('mpxn'), ct, apiSrv)

	print "Got sessionId so we can start the process: " + sid + "<p>\n"

	# Get Consent URL
	#
	consentURL = n3rgyGetConsentURL(sid, form.getvalue('mpxn'), ct, ru, eu, apiSrv)

	print "\n<p>Got consentURL on " + apiSrv + " that would normally redirect: \n" + consentURL

	print '<h2><a href=' + consentURL + '>click here to go</a></h2>'

elif form.getvalue('action') == "TConsent":

	if apiSrv == "live":
		print "Live Trusted Consents not supported<p>\n"
	else:
        	print "Adding Trusted consent on " + apiSrv + " for: " + form.getvalue('mpxn') + " on " + apiSrv + "<p>\n"
        	result = n3rgyAddTrustedConsent(AUTH, form.getvalue('mpxn'), "Simon Smith Salford 30-04-2020 email", "2017-01-01", apiSrv)

        print json.dumps(result)

else:

	print "Withdrawing consent on " + apiSrv + " for: " + form.getvalue('mpxn') + "<p>\n"
	result = n3rgyWithdrawConsent(AUTH, form.getvalue('mpxn'), apiSrv)

	print json.dumps(result)

print "<p><a href='/sm'>back</a></body></html>"
