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