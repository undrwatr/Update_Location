#!/usr/bin/env python3

import cred
import requests
import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



#pull down all of the external ip addresses for the networks in the organization
#custom variables for the program imported from the cred.py file located in the same directory
ORGANIZATION = cred.organization
KEY = cred.key
graphuser = cred.graph_user
graphpass = cred.graph_password

email_server = cred.email_server
me = cred.me
you1 = cred.you1


#Regex for APs only - MR26/33/42
REGEX = re.compile('Q2PD')
REGEX1 = re.compile('Q2HD')
REGEX2 = re.compile('Q2KD')

#Main URL for the Meraki Platform
DASHBOARD = "https://api.meraki.com"
#api token and other data that needs to be uploaded in the header
HEADERS = {'X-Cisco-Meraki-API-Key': (KEY), 'Content-Type': 'application/json'}

#Pull back all of the interface stats IDs:
GET_UPLINK_URL = DASHBOARD + '/api/v1/organizations/%s/networks' % ORGANIZATION
GET_UPLINK_RESPONSE = requests.get(GET_UPLINK_URL, headers=HEADERS)
GET_UPLINK_JSON = GET_UPLINK_RESPONSE.json()


#Function for pulling the data from the to be used later on
def get_externalip():
    GET_EXTERNAL_URL = DASHBOARD + '/api/v0/networks/%s/devices/%s/uplink' % (network_id, SERIAL)
    GET_EXTERNAL_RESPONSE = requests.get(GET_EXTERNAL_URL, headers=HEADERS)
    GET_EXTERNAL_JSON = GET_EXTERNAL_RESPONSE.json()
    for x in GET_EXTERNAL_JSON:
        try: 
            IPRANGES.append({'@odata.type' : "#microsoft.graph.iPv4CidrRange", 'cidrAddress' : ((x['publicIp']) + '/32')})
        except KeyError:
            print("")

#Build the JSON for upload

OBJECTS = {}
IPRANGES = []
OBJECTS["@odata.type"] = "#microsoft.graph.ipNamedLocation"
OBJECTS["displayName"] = "STORES"
OBJECTS["isTrusted"] = "True"
OBJECTS["ipRanges"] = IPRANGES

#Iterate through all of the stores and find the ones with Wireless APs and then get the wanip
for i in GET_UPLINK_JSON:
    if i["productTypes"] == ['appliance', 'wireless']:
        network_id = (i["id"])
        GET_DEVICES_URL = DASHBOARD + '/api/v0/networks/%s/devices' % network_id
        GET_DEVICES_RESPONSE = requests.get(GET_DEVICES_URL, headers=HEADERS)
        GET_DEVICES_JSON = GET_DEVICES_RESPONSE.json()
        for x in GET_DEVICES_JSON:
            if REGEX.match(x["serial"]):
                SERIAL = (x["serial"])
                get_externalip()
            if REGEX1.match(x["serial"]):
                SERIAL = (x["serial"])
                get_externalip()
            if REGEX2.match(x["serial"]):
                SERIAL = (x["serial"])
                get_externalip()            


print("This is the data from MS")

#update the MS location with that information

#get locations

#Application Id - on the azure app overview page This generates the token information for the authentication
app_id = cred.app_id

client_secret = cred.client_secret

#Use the redirect URL to create a token url
token_url = cred.token_url
token_data = {
    'grant_type': 'password',
    'client_id': (cred.app_id),
    'client_secret': (cred.client_secret),
    'resource': 'https://graph.microsoft.com',
    'scope': 'https://graph.microsoft.com',
    'username': (graphuser), 
    'password': (graphpass),
}
token_r = requests.post(token_url, data=token_data)
token = token_r.json().get('access_token')

#headers for the update
headers = {'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}

#Upload the data trusted location data to Azure:
locations_update_url = "https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations"

locations_update = requests.post(locations_update_url, headers=headers, data=json.dumps(OBJECTS))

if locations_update.status_code == 201:
    print("Upload successful")
    msg = MIMEMultipart()
    msg['Subject'] = 'Update Location Script ran successfully'
    msg['From'] = me
    msg['To'] = you1
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(email_server)
    s.sendmail(me, you1)
    s.quit()