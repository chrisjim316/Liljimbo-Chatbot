""" Lil Jimbo 2.0
No longer works like previous method. Implementation cycle and general to do in flow-chart style:
User enters message to FB bot
fb bot receives
fb bot sends to heroku
heroku runs python app with fb user message as input (or just the python function)
app sends fb message to wit.ai.
	wit.ai contains a new entity, "symptons" which are like "i'm cold", "headache" etc.
	wit.ai returns new entity in JSON format
app receives wit.ai reply
app reads json file, creating a list which contains every item in the "symptons" section of the json response
app then performs a google search with each sympton in the search like so "[SYMPTONS] site:www.nhs.co.uk"
if you google symptons and limit it to the NHS, it'll normally direct you to a page containing the aliment. This is like a badly
implemented version of a "symptom checker". "Symptom checker" api's already exist but they cost money
this may not always work, but we'll deal with that in a second.
Once we have a google search results, we accecpt the first result from google as the "illness".
scrape the nhs webpage (they roughly all have the similar format)

scrape the nhs webpage for 3 things
|name of illness| & |symptoms of illness| & |cure to illness|
once we have these 3 things, make a facebook response and add a disclaimer to the end to say that
this isn't always correct
once we create a facebook response, respond to the user with this response.

Although we can never be "sure" of the users response, we'll get correct results most of the time.

There is an offline build of app2, which makes it faster to test it.
Also, tokens are no longer stored in python files. They are stored in a tokens.txt file with the format
TOKEN_NAME: TOKEN
"""
from wit import Wit
import requests
from bs4 import BeautifulSoup
import os
import sys
import json
from datetime import datetime
from flask import Flask, request


# used for debugging
import logging
logging.basicConfig(level=logging.DEBUG, filename='appLog.txt', format=' %(asctime)s - %(levelname)s- %(message)s')

with open("tokens.txt") as file:
	# gets tokens from token.txt
	file_read = file.read()
	file_read = file_read.split("\n")

	wit_token = file_read[1].split(" ")[1]
	# format to get a single token from the text file

# Clients

client = Wit(wit_token)


app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
	# when the endpoint is registered as a webhook, it must echo back
	# the 'hub.challenge' value it receives in the query arguments
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200

	return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():

	# endpoint for processing incoming messaging events

	data = request.get_json()
	log(data)  # you may not want to log every incoming message in production, but it's good for testing

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:

				if messaging_event.get("message"):  # someone sent us a message

					sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
					recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
					message_text = messaging_event["message"]["text"]  # the message's text

					send_message(sender_id, "roger that!")

				if messaging_event.get("delivery"):  # delivery confirmation
					pass

				if messaging_event.get("optin"):  # optin confirmation
					pass

				if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
					pass

	return "ok", 200

def send_message(recipient_id, message_text):

	log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}
	data = json.dumps({
		"recipient": {
			"id": recipient_id
		},
		"message": {
			"text": message_text
		}
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
	try:
		if type(msg) is dict:
			msg = json.dumps(msg)
		else:
			msg = unicode(msg).format(*args, **kwargs)
		print(u"{}: {}".format(datetime.now(), msg))
	except UnicodeEncodeError:
		pass  # squash logging errors in case of non-ascii text
	sys.stdout.flush()


def receive_message(message):
	logging.debug(message)
	symptoms = parse_message(message)
	search(symptoms)
	
class NHS_api(object):

	def __init__(self, symptoms):
		"""
		self.symptoms is a set of all symptoms
		self.url is a list of all urls relating to those symptoms
		self.website_content is the website content of the first self.url
		self.disease_name is pretty much the entirety of the disease, it was miss-called "disease name
		"""
		self.symptoms = symptoms
		self.urls = list(self.search(self.symptoms))
		self.website_content = self.parse_websites(self.urls)
		#self.disease_name = self.get_info(self.website_content)
		# self.disease name
		# self.disease_symptoms
		# self.description

	def search(self, symptoms):
		# given a list of symptoms, google the symptoms and return top 3 results
		from google import search
		symptoms = ' '.join(symptoms)
		symptoms_search = symptoms + " \"nhs\""
		logging.debug(symptoms_search)
		return (search(symptoms_search, stop=3))

	def parse_websites(self, search):
		logging.debug(search)
		# given an NHS website, parse it for illness name, description, symptoms and cure
		list_of_request_objects = [requests.get(i) for i in search]
		for item in list_of_request_objects:
			if item == "<Response [404]>":
				list_of_request_objects.remove(i)
			else:
				continue
		# if objects are 404 errors, delete them from the list as it'll be useless to us.


		# gets the contents of 3 requests objects and stores them in a list
		list_of_contents = []
		for i in range(3):
			list_of_contents.append(list_of_request_objects[i].content)


		# Beautiful soup section #

		bs_objects = list(map(lambda x: BeautifulSoup(x, 'html.parser'), list_of_contents))
		# makes beautiful soup objects (needed to parse) out of the requests

		# here we begin the distinction between objects. Each article represents a different top-scoring webpage's "article" content.
		article1 = bs_objects[0].find("div", {"class": "article"})
		article2 = bs_objects[1].findAll("div", {"class": "article"})
		article3 = bs_objects[2].findAll("div", {"class": "article"})


		text = list(article1.get_text())
		for i in text:
			if "stock" in i.lower():
				text.pop(i)
		text = "".join(text)
		logging.debug(text)
		return(text)
	# def get_title(self, article)
	def get_info(self, webpage):
		return "a"


def parse_message(message):
	# parses the message through wit.ai
	# when input is "I have a headache"
	# output is
	# {"_text":"I have a headache","entities":{"symptom":[{"confidence":0.98805916237107,"value":"headache","type":"value"}]},"msg_id":"0gFLp4hHKeJKvwspJ"}
	resp = client.message(message)
	confidence = resp["entities"]["symptom"][0]["confidence"]
	symptoms = resp["entities"]["symptom"][0]["value"]
	logging.debug(confidence)
	logging.debug(symptoms)
	if confidence < 0.70:
		logging.debug("not an illness")
		# deal with "hellos" etc in main part, if main doesnt know what they said it'll come here to check if its an illness
		# if its not an illness, we do not know what they said.
		return("Sorry, I do not understand what you said.")
	else:
		# gets rid of puncutation. So "headache." becomes "headache"
		symptoms = set(symptoms.split(" "))
		# turns it into a set of symptoms
		symptoms = remove_articles(symptoms)
		# gers rid of article words
		symptoms = set(map(lambda x: x.strip(",."), symptoms))
		# gets rid of puncuation
		logging.debug(symptoms)
		return symptoms


def remove_articles(message):
	# TODO I can probably turn this into a map / lambda functon. Would be more elegant, so figre this out.
	return_msg = []
	for i in message:
		if i not in ["and", "an", "a"]:
			return_msg.append(i)
	return return_msg

if __name__ == '__main__':
	app.run(debug=True)