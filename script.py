from xml.etree import cElementTree as ET
import urllib.request
import json
import datetime
import twilio.rest
from twilio.rest import TwilioRestClient

account_sid = "REDACTED"
auth_token  = "REDACTED"
base_folder = "/home/matthew/Development/Python/e3-duty-notifier/"

refresh = True
store = open(base_folder + 'access_token.txt', 'w')

if refresh:
	refresh_token = 'REDACTED'
	params = urllib.parse.urlencode({
		'client_id':'REDACTED',
		'client_secret':'REDACTED',
		'refresh_token':refresh_token,
		'grant_type':'refresh_token'
		})

	access_token_request = urllib.request.Request("https://accounts.google.com/o/oauth2/token")
	access_token_reply = urllib.request.urlopen(access_token_request, params.encode('utf-8'))
	access_token = json.loads(access_token_reply.read().decode('utf-8'))["access_token"]

	store.write(access_token)
else:
	access_token = store.read()

request = urllib.request.Request('REDACTED')
request.add_header("Authorization", "Bearer " + access_token)
response = urllib.request.urlopen(request)
xml = ET.fromstring(response.read().decode('utf-8'))

ns = '{http://www.w3.org/2005/Atom}'

contents = []
duties = []

for entry in xml.findall(ns+'entry'):
	title = entry.find(ns+'title').text
	content = entry.find(ns+'content').text
	contents.append(content)

for i in range(0, 5):
	duties.append(contents[i*3:i*3+3])
	
client = TwilioRestClient(account_sid, auth_token)

success = 0
number = "+13204293611"

for duty in duties:
	if duty[0] == "Scripture Reader":
		text = "Hi, this is a reminder that you're doing Scripture Reading for tomorrow's service. :)"
	elif duty[0] == "Multimedia Lead":
		text = "Hi, this is a reminder that you're Multimedia lead for tomorrow's service. Please be in by 9:45 :)"
	else:
		text = "Hi, this is a reminder that you're doing " + duty[0] + " duty for tomorrow's service. Please be in by 9:45 :)"
	text+= " (P.S. this is automated. Please don't reply!)"
	#if duty[2] == "91509283" and success == 0:
	message = client.messages.create(body=text, to="+65" + duty[2], from_=number)
	success += 1

text = str(success) + " messages successfully delivered to "
for duty in duties[:-1]:
	text += duty[1] + ', '
text+=duties[-1][1] + '.'

message = client.messages.create(body=text, to="REDACTED", from_=number)
msg_log = open(base_folder + 'messages.log', 'a')
msg_log.write('['+datetime.datetime.now().strftime("%H:%M %d%m%y")+'] '+ text + '\n')
