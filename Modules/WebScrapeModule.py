import requests
from urllib.request import urlopen
from typing import List, Dict
from bs4 import BeautifulSoup

import pandas as pd
import re

def scrape_wikipedia(month:str, date:str, category:str):
	""" Scrapes Wikipedia's page on events, deaths, holidays on the current date.
	
	## Arguments:
	- `month`: e.g. 'March';
	- `date`: e.g. '06'
	- `category` - which category would you like to print from the daily events? Available choices: `['events', 'births', 'deaths', 'holidays']`.
	
	## Function: 
	Web scrapes https://en.wikipedia.org/wiki/{month}_{date}, 
	
	where {month} and {date} - automatically-determined date of the current day.
	
	For example, if you run this function on May 12th, the following link will be scraped:
	
	https://en.wikipedia.org/wiki/May_12
	
	## Returns:
	a string"""
	#
	# month, date = pd.to_datetime('today').strftime('%B %d').split(' ')
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
	# print('totalText2:\n' + '-'*50)
	# print(totalText2)
	#
	try:
		totalText3 = totalText2.split('Events[edit]')[1]
		# print('totalText3:\n' + '-'*50)
		# print(totalText3)
		events, births_deaths_holidays_references = totalText3.split('Births[edit]')
		births, deaths_holidays_references        = births_deaths_holidays_references.split('Deaths[edit]')
		deaths, holidays_references               = deaths_holidays_references.split('Holidays and observances[edit]')
		holidays                                  = holidays_references.split('References[edit]')[0]
	except IndexError:
		totalText3 = totalText2.split('\nEvents\n')[1]
		# print('totalText3:\n' + '-'*50)
		events, births_deaths_holidays_references = totalText3.split('Births')
		births, deaths_holidays_references        = births_deaths_holidays_references.split('Deaths')
		deaths, holidays_references               = deaths_holidays_references.split('Holidays and observances')
		holidays                                  = holidays_references.split('References')[0]
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




# WEb scrape the newspaper webpage
def scrape_thetelegraph():
	""" Scrapes the "world news" section of The Telegraph newspaper. 
	
	## Arguments: 
	none
	
	## Function:
	Scrapes the "world news" section of the telegraph newspaper.

	https://www.theguardian.com/world

	## Returns
	returns a Pandas DataFrame"""
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
	# Remove '' values, or rather, replace them with a ' ' space
	df.replace('', ' ', inplace=True)
	df.fillna(' ', inplace=True)
	return df


