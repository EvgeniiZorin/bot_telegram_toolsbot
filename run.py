import telebot
import config
import random
from telebot import types
from pyowm.owm import OWM
import requests
import time
import datetime
import csv
from typing import List, Dict
import time
import pandas as pd
import os


telebot_token = os.environ.get('TELEBOT_API')
bot = telebot.TeleBot(telebot_token)
owm_api = os.environ.get('OWM_API')
owm = OWM(owm_api)
mgr = owm.weather_manager()

# /start 
@bot.message_handler(commands=['start'])
def start(message):

	# bot.send_message(message.chat.id, 'Welcome, dear user! Commands:', reply_markup=markup)
	# Send a sticker
	## Can i send an animated sticker???
	sti = open('Sticker_jojo.webp', 'rb')
	bot.send_sticker(message.chat.id, sti)
	#
	bot.send_message(message.chat.id, """Welcome to my bot!
	Here, I will write some description...

	Below are some of the commands that you can call:

	/help - print this help message
	/quote - print a randomly-selected motivational quote
	/weather - print a forecast for a specific city
	"""
	)

# Handle incoming /start, /help messages
@bot.message_handler(commands=['help'])
def welcome(message):
	# bot.send_message(message.chat.id, 'Welcome, dear user! Commands:', reply_markup=markup)
	bot.send_message(message.chat.id, """ HELP MENU 
	
	Below are some of the commands that you can call:

	/help - print this help message
	/quote - print a randomly-selected motivational quote
	/weather - print a forecast for a specific city
	""")


# Respond to the button commands
@bot.message_handler(commands=['quote'])
def send_quote(message):
	# bot.send_message(message.chat.id, 'here is a quote for you')
	df = pd.read_csv('https://raw.githubusercontent.com/EvgeniiZorin/FILES_DATABASE/main/quotes.csv')
	quote = df.sample(1)
	quote_author, quote_text = list(quote['Author'])[0], list(quote['Quote'])[0]
	# print(f"{quote_text} -by- {quote_author}")
	bot.send_message(message.chat.id, "Let me send you a quote:")
	bot.send_message(message.chat.id, f'"{quote_text}"\n - {quote_author}')

@bot.message_handler(commands=['weather'])
def send_forecast(message):
	bot.send_message(message.chat.id, "Let's show a forecast!")
	message1 = bot.send_message(message.chat.id, "For which city would you like to know the weather forecast? E.g. `London`, `London, UK`, `London, United Kingdom`")
	bot.register_next_step_handler(message1, process_name_step)
def process_name_step(message):
	bot.send_message(message.chat.id, f"You have typed: {message.text}")
	from pyowm.owm import OWM
	from geopy.geocoders import Nominatim
	# Example input
	# city_country = 'Toluca, Mexico'
	# Example exception (doesn't work for some reason)
	# city_country = 'Moscow, Russia'
	city_country = message.text
	owm = OWM('245ade4c3a60e993b30476c52868eacc')
	mgr = owm.weather_manager()
	# dir(mgr)

	try:
		observation = mgr.weather_at_place(city_country)
	except:
		bot.reply_to(message, "City unrecognised. Please use the `/weather` command again with a valid input!")
	else:
		observation = mgr.weather_at_place(city_country)
		temp_dict = observation.weather.temperature('celsius')
		# Initialize Nominatim API
		geolocator = Nominatim(user_agent="MyApp")
		location = geolocator.geocode(city_country)
		# print(location)
		# print(f"{location.latitude}, {location.longitude}")
		failure = 0
		try:
			one_call = mgr.one_call(location.latitude, location.longitude)
		except:
			failure = 1
		output = ''
		# print(f"Weather at location: \n - Current: {temp_dict['temp']}\n - Min today: {temp_dict['temp_min']}\n - Max today: {temp_dict['temp_max']}")
		# print(f"Weather in {location}: \n - Current: {temp_dict['temp']}")
		output += f"Weather in {location}: \n - Current: {temp_dict['temp']}\n"
		if failure == 0:
			for i in range(2, 11, 2):
				# print(f" - In {i} hours: {one_call.forecast_hourly[i].temperature('celsius')['temp']}")
				output += f" - In {i} hours: {one_call.forecast_hourly[i].temperature('celsius')['temp']}\n"
		else:
			# print(' - Failed to get forecast for this location.')
			output += " - Failed to get hourly forecast for this location"
		bot.send_message(message.chat.id, output)


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message):
	bot.reply_to(message, "Thanks for the sticker! Here's my favourite sticker:")
	# print(message.sticker) # To print info, e.g. ID, about the sticker
	bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAICG2N8HI-dzXnLfuYHqvIgNZ9aUaaPAAMBAAIWfGgD-lJ5LW5TPaYrBA')

# Handle all unknown messages
@bot.message_handler(func = lambda message: True)
# @bot.edited_message_handler(content_types=['text']) ## This decorator is useful if you also want to handle edited messages, i.e. someone edited message
# and you handle it again, but the edited version this time
def unknown_msg(message):
	smile = '😕'
	bot.reply_to(message, f'Unknown command {smile}; please try again or enter /help to check available commands.')
	# ### Print user info to terminal
	print(f"Info about the user: {message.from_user}")
	if message.from_user.id == 1202179392:
		bot.reply_to(message, 'I know its Evgenii, whats up, master?')
	else:
		bot.reply_to(message, 'I dont know who you are yet ')
	# Below is a trial API requests printing into terminal
	# Later, can try to use it to do something else
	token = os.environ.get('TELEBOT_API')
	link = f'https://api.telegram.org/bot{token}'
	r = requests.get(f"{link}/getMe")
	print(f"Info about me (getMe): {r.json()}")
	print('-'*50)
	r = requests.get(f'{link}/getUpdates')
	print(f"Updates (getUpdates): {r.json()}")
	print('-'*50)
	payload = {'chat_id': message.from_user.id, 'text': 'Ok, i see you now'}
	r = requests.post(f"{link}/sendMessage", data=payload)
	print(r.json())



def run():
	bot.polling(none_stop=True)
	# bot.infinity_polling()

# To run the program
if __name__ == '__main__':
	run()

