import sys
import random
from flask import Flask, request
from utils import wit_response
from pymessenger import Bot

# used for debugging
import logging
logging.basicConfig(level=logging.DEBUG, filename='appLog.txt', format=' %(asctime)s - %(levelname)s- %(message)s')

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAbUMFhFArYBAC4hWG5iwb7VzEkQbU9FMalQjACslYDN0vYMVTvzCdMIZAxsRShwhaLDCwq3J9utQBYQvo8ZCxkKeM4Ewseq1W9pLXALZAwZCrut1Gvgn6DLbuSDzUjZBq4z32YdHPYuvL73xZBPMXxDSSbdWElVqMu6dtxvEbwgZDZD"

bot = Bot(PAGE_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
	# Webhook verification
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == "hello":
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():

	def main():
		data = request.get_json()
		logging.debug(data)

		if data['object'] == 'page':
			for entry in data['entry']:
				for messaging_event in entry['messaging']:

					# IDs
					sender_id = messaging_event['sender']['id']
					# recipient_id = messaging_event['recipient']['id']     This variable isn't used so commented out.

					if messaging_event.get('message'):
						# Extracting text message
						if 'text' in messaging_event['message']:
							messaging_text = messaging_event['message']['text']
						else:
							messaging_text = 'no text'

						response = None
						imageURL = None
						images = []
						entity, value = wit_response(messaging_text) # so this is parsing user text using wit.ai

						if entity == 'thanks':
							response = "My pleasure. Always happy to help."
						elif entity == 'help':
							response = "Please indicate and type your situation. • burns • cuts and wound • black eyes • bruises"
						elif entity == 'burns':
							response = "1. Stop Burning Immediately 2." \
							           " Remove Constrictive Clothing Immediately 3.Cover with sterile," \
							           " non-adhesive bandage or clean cloth. Do not apply butter or" \
							           " ointments, which can cause infection."
						elif entity == 'cuts_and_wound':
							images.append("https://s-media-cache-ak0.pinimg.com/originals/6d/95/d0/6d95d0db65621cef70e9e42bcc21a3cc.jpg")
							response = "1. Stop the Bleeding  2. Clean and Protect" \
							           " 3. Put a sterile bandage on the area. In some people, antibiotic ointments may cause a rash. If this happens, stop using the ointment."
						elif entity == 'bruises':
							response = "1. Apply Ice - Wrap a cold pack in a towel or washcloth and hold it against the bruise for 10 to 15 minutes." \
							           " 2. Elevate the Area - If possible, raise the bruised area above the heart to reduce swelling." \
							           " 3. Reduce Pain"
						elif entity == 'black_eye':
							response = "1. Treat Symptoms - Apply ice to the area. Don't press on the eye." \
							           " 2. Get Medical Help - See a health care provider to make sure there is no further damage to the eye" \
							           " 3. Follow Up - Continue icing the area several times a day for 1 or 2 days."
						elif entity == 'frostbite':
							response = "1. Seek Medical Care Promptly" \
							           " 2. Restore Warmth - Get the person to a warm place and remove any wet clothing." \
							           " - Unless absolutely necessary, the person should not walk on frostbitten toes or feet." \
							           " 3 Bandage the area - Put gauze or clean cotton balls between fingers or toes to keep them separated."
						elif entity == 'heat_exhaustion':
							response = "1. Lower Body Temperature - Get the person out of the heat and into a cool environment." \
							           " 2. Rehydrate - Give cool, nonalcoholic and non-caffeinated beverages as long as the person is alert." \
							           " 3. Rest - Give over-the-counter acetaminophen (Tylenol) if the person has a mild headache." \
							           " 4. See a Health Care Provider if - Symptoms get worse or last more than an hour"
						elif entity == 'place':
							response = "I'm from London!"
						elif entity == 'destroyer':
							response = "I have no interest in becoming Ultron. Global destruction is not my goal, serving you is."
						elif entity == 'contact_name':
							response = "Nice to meet you. I am Liljimbo, a friendly chatbot designed to provide First-Aid treatment instructions"
						elif entity == 'creator':
							response = "I am designed by Chris, Brandon, and Jardin a team based in London."
						elif entity == 'functions':
							response = "I am here to provide First-Aid treatment instructions. Please note that I cannot call the ambulance for you."
						elif entity == 'greetings':
							images.append("https://media.giphy.com/media/Cmr1OMJ2FN0B2/giphy.gif")
							images.append("https://media.giphy.com/media/cE02lboc8JPO/giphy.gif")
							images.append("https://media.giphy.com/media/PfHrNe1cSKAjC/giphy.gif")
							images.append("https://media.giphy.com/media/mW05nwEyXLP0Y/giphy.gif")
							response = "Hello there!"
						elif entity == 'bye':
							response = "Goodbye, talk to you soon!"
						elif entity == 'love':
							images.append("https://media.giphy.com/media/2dQ3FMaMFccpi/giphy.gif")
							images.append("https://media.giphy.com/media/l4FGAknYu7gKbSuME/giphy.gif")
							response = "The feeling is mutual." + u'\U0001F60D'
						elif entity == 'hate':
							images.append("https://media.giphy.com/media/3o6ZsY5h1VxSirZQI0/giphy.gif")
							images.append("https://media.giphy.com/media/SjrCEiRgiT9pC/giphy.gif")
							images.append("https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif")
							images.append("https://media.giphy.com/media/OPU6wzx8JrHna/giphy.gif")
							images.append("https://media.giphy.com/media/3o6wrvdHFbwBrUFenu/giphy.gif")
							response = "My heart is in pieces on the floor." + u'\U0001F625'
						elif entity == 'gender':
							response = "I am beyond your concept of gender."

						if response == None:
							response = "Interesting..."

						if len(images) > 0:
							imageURL = random.choice(images)

						bot.send_image_url(sender_id, imageURL)
						bot.send_text_message(sender_id, response)

						#bot.send_video_url(sender_id, )

	main()

	return "ok", 200

def exit():
	# closes program
	sys.exit(0)

if __name__ == "__main__":
	app.run(debug=True, port=80)
