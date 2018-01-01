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

def receive_message(message):
    logging.debug(message)
    symptoms = parse_message(message)
    search(symptoms)

def search(symptoms):
    from google import search
    symptoms = ' '.join(symptoms)
    symptoms_search = symptoms + " \"nhs\""
    for url in search(symptoms_search, stop=20):
        print(url)

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

receive_message("I have a headache")

