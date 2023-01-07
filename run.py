import os
import time
import datetime
import random
import re
import pandas as pd

import telebot
from telebot import types
from telebot import formatting
import config

from pyowm.owm import OWM

import requests
from urllib.request import urlopen
from typing import List, Dict
from bs4 import BeautifulSoup



telebot_token = os.environ.get('TELEBOT_API')
bot = telebot.TeleBot(telebot_token)
owm_api = os.environ.get('OWM_API')
owm = OWM(owm_api)
mgr = owm.weather_manager()

def profanity_present(message:str):
	profanities_present = sum([ 1 if i in message.lower() else 0 for i in ['fuck', 'cunt', 'bitch', 'slut', 'shit', 'wanker', 'asshole'] ])
	return None if profanities_present == 0 else "Please don't swear ❌🤬"

# /start 
@bot.message_handler(commands=['start'])
def start(message):
	# Send a sticker
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
	bot.send_message(message.chat.id, """ HELP MENU 
	
	Below are some of the commands that you can call:

	/help - print this help message
	/quote - print a randomly-selected motivational quote
	/weather - print a forecast for a specific city
	""")


# Respond to the button commands
@bot.message_handler(commands=['quote'])
def send_quote(message):
	df = pd.read_csv('https://raw.githubusercontent.com/EvgeniiZorin/FILES_DATABASE/main/quotes.csv')
	quote = df.sample(1)
	quote_author, quote_text = list(quote['Author'])[0], list(quote['Quote'])[0]
	bot.send_message(message.chat.id, "Let me send you a quote:")
	bot.send_message(message.chat.id, f'"{quote_text}"\n - {quote_author}')

@bot.message_handler(commands=['weather'])
def send_forecast(message):
	bot.send_message(message.chat.id, "Let's show a forecast!")
	message1 = bot.send_message(message.chat.id, "For which city would you like to know the weather forecast? E.g. `London`, `London, UK`, `London, United Kingdom`")
	bot.register_next_step_handler(message1, process_name_step)
def process_name_step(message):
	# If the message is a profanity, delete it and send a warning
	if profanity_present(message.text) is not None: 
		bot.delete_message(message.chat.id, message.message_id)
		bot.send_message(message.chat.id, profanity_present(message.text))
		return None
	bot.send_message(message.chat.id, f"You have typed: {message.text}")
	from pyowm.owm import OWM
	from geopy.geocoders import Nominatim
	# Example input
	# city_country = 'Toluca, Mexico'
	city_country = message.text
	owm = OWM('245ade4c3a60e993b30476c52868eacc')
	mgr = owm.weather_manager()
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
		failure = 0
		try:
			one_call = mgr.one_call(location.latitude, location.longitude)
		except:
			failure = 1
		output = ''
		# print(f"Weather at location: \n - Current: {temp_dict['temp']}\n - Min today: {temp_dict['temp_min']}\n - Max today: {temp_dict['temp_max']}")
		output += f"Weather in {location}: \n - Current: {temp_dict['temp']}\n"
		if failure == 0:
			for i in range(2, 11, 2):
				output += f" - In {i} hours: {one_call.forecast_hourly[i].temperature('celsius')['temp']}\n"
		else:
			# print(' - Failed to get forecast for this location.')
			output += " - Failed to get hourly forecast for this location"
		bot.send_message(message.chat.id, output)


# Web scrape Wikipedia
def get_wikipedia_info(category:str):
	#
	month, date = pd.to_datetime('today').strftime('%B %d').split(' ')
	# example: url = 'https://en.wikipedia.org/wiki/May_12'
	url = f'https://en.wikipedia.org/wiki/{month}_{date}'
	print(url)
	page = requests.get(url)
	soup = BeautifulSoup(
		page.content, 
		'html.parser'
	)
	#
	totalText = soup.prettify()
	totalText2 = soup.get_text()
	#
	totalText3 = totalText2.split('Events[edit]')[1]
	events, births_deaths_holidays_references = totalText3.split('Births[edit]')
	births, deaths_holidays_references        = births_deaths_holidays_references.split('Deaths[edit]')
	deaths, holidays_references               = deaths_holidays_references.split('Holidays and observances[edit]')
	holidays                                  = holidays_references.split('References[edit]')[0]
	#
	output_dict = {'events':events, 'births':births, 'deaths':deaths, 'holidays':holidays}
	# Process the strings, replacing unnecessary tags
	for i in output_dict:
		# Remove leading & trailing "\n" and " " characters
		output_dict[i] = output_dict[i].strip()
		# Replace "[edit]" with ":"
		output_dict[i] = output_dict[i].replace('[edit]', ':')
		# then replace pattern like "[1]" with nothing
		output_dict[i] = re.sub('\[[0-9]+\]', '.', output_dict[i])
		# Replace "[citation needed]" with nothing
		output_dict[i] = output_dict[i].replace('[citation needed]', '.')
	#
	return output_dict[category]

@bot.message_handler(commands=['events', 'births', 'deaths', 'holidays'])
def print_births(message):
	output = get_wikipedia_info(message.text[1:])
	if len(output) > 4000:
		output2 = output.split('\n')
		chunk = ''
		while output2:
			if len(chunk) < 3500:
				chunk += output2.pop(0)
				chunk += '\n'
				if len(output2) == 0:
					bot.send_message(message.chat.id, chunk)
			else:
				bot.send_message(message.chat.id, chunk)
				chunk = ''
	else:
		bot.send_message(message.chat.id, output)


# WEb scrape the newspaper webpage
def scrape_newspaper_funct():
	""" returns a Pandas DataFrame"""
	url = 'https://www.theguardian.com/world'
	page = urlopen(url)
	html = page.read().decode("utf-8")
	soup = BeautifulSoup(html, "html.parser")
	stuff = soup.find_all('div',  class_="fc-item__container")
	stuff
	links, headlines, texts = [],[],[]
	for i in stuff:
		### LINKS
		link = i.find('a')['href']
		# print(link)
		links.append(link)
		### HEADLINE
		headline = i.find('span', class_="js-headline-text").contents[0]
		# print(headline)
		headlines.append(headline)
		### TEXT
		text = i.find('div', class_="fc-item__standfirst").contents[0]
		# print(text)
		texts.append(text)
	df = pd.DataFrame([], columns=['Headline', 'Text', 'Link'])
	headlines = [ i.strip() for i in headlines ]
	texts = [ i.strip() for i in texts ]
	df['Headline'] = headlines
	df['Text'] = texts
	df['Link'] = links
	return df


@bot.message_handler(commands=['news'])
def scrape_newspaper(message):
	dataframe = scrape_newspaper_funct()
	# Remove '' values, or rather, replace them with a ' ' space
	dataframe.replace('', ' ', inplace=True)
	dataframe.fillna(' ', inplace=True)
	for index, row in dataframe.iterrows():
		# one_news_piece = f"{row['Headline']}\n{row['Text']}\n{row['Link']}\n\n"
		# bot.send_message(message.chat.id, one_news_piece)
		bot.send_message(
			message.chat.id, 
			formatting.format_text(
				formatting.mbold(row['Headline']), 
				formatting.mitalic(row['Text']),
				formatting.munderline(row['Link']),
				separator='\n'
			),
			parse_mode='MarkdownV2'
		)
		if index >= 5:
			# break
			pass



@bot.message_handler(content_types=['sticker'])
def sticker_handler(message):
	bot.reply_to(message, "Thanks for the sticker! Here's my favourite sticker:")
	# print(message.sticker) # To print info, e.g. ID, about the sticker
	bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAICG2N8HI-dzXnLfuYHqvIgNZ9aUaaPAAMBAAIWfGgD-lJ5LW5TPaYrBA')

# Handle all unknown messages
@bot.message_handler(func = lambda message: True)
def unknown_msg(message):
	# If the message is a profanity, delete it and send a warning
	if profanity_present(message.text) is not None: 
		bot.delete_message(message.chat.id, message.message_id)
		bot.send_message(message.chat.id, profanity_present(message.text))
		return None
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

