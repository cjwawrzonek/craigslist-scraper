import argparse
import clsearch as cls
import jinja2
import json
import os
import pickle
import re
import sys
import emailer

from datetime import datetime
from datetime import timedelta

from pprint import pprint as pp

required_search_params = ['area', 'search_type']

optional_search_params = ['search_distance', 'postal', 'max_bedrooms', 'min_bedrooms',
						  'pets_cats', 'pets_dogs', 'min_bathrooms', 'max_bathrooms',
						  'minSqft', 'maxSqft', 'postedToday']

## Configure and return the command line args ##
def getargs():
	parser = argparse.ArgumentParser(description='Scrape a craigslist housing search and return appealing deals.')
	parser.add_argument('-c', '--config', dest='config', help='json file name for your craigslist '
						'search configuration. See configurations/config.json for examples.')
	parser.add_argument('-e', '--email', dest='email', help='Use this flag if you would like the results to '
						'be emailed. This flag should point to a configuration file with email credentials. '
						'See configurations/email.config for examples.')

	return parser.parse_args()

## A simple scrape of housing that prints the listings with good price : room ratio ##
def simple_scrape(url):
	data = cls.CLSearch(url)

	results = []
	for ls in data.listings:
		try:
			rooms = float(ls['bdr'])
			price = float(ls['price'])
			ratio = price / rooms
			ls['ratio'] = ratio
			if ratio < 1500 and ratio > 600:
				results.append(ls)
		except:
			pass

	for result in results:
		print str(result['ratio']) + ' - ' + result['url']

## A custom cl search scrape using a config file ##
def custom_scrape(args):
	with open(args.config) as config_file:
		config = json.load(config_file)

	search_opts = config['search_options']
	if 'filter_options' in config:
		filter_opts = config['filter_options']
	else:
		filter_opts = {}
	if 'script_options' in config:
		script_opts = config['script_options']
	else:
		script_opts = {}

	url = 'https://{}.craigslist.org/search/{}?availabilityMode=0&'.format(search_opts['area'], search_opts['search_type'])

	for param in optional_search_params:
		if param in search_opts:
			url = '{}{}={}&'.format(url, param, search_opts[param])

	data = cls.CLSearch(url, config=config)

	results = []
	for ls in data.listings:
		if search_opts['search_type'] == 'apa':
			try:
				rooms = float(ls['bdr'])
				price = float(ls['price'])
				ratio = price / rooms
				ls['ratio'] = ratio
				if 'max_ratio' in filter_opts:
					max_r = filter_opts['max_ratio']
				else:
					max_r = 1000
				if 'min_ratio' in filter_opts:
					min_r = filter_opts['min_ratio']
				else:
					min_r = 0
				if ratio <= max_r and ratio >= min_r:
					results.append(ls)
			except:
				pass

	# This means we are tracking listings between different searches
	if 'log_file' in script_opts:
		now = datetime.now()
		filename = script_opts['log_file']

		if os.path.isfile(filename):
			listings = pickle.load(open(script_opts['log_file'], 'rb'))

			for result in list(results):
				# If this listing exists in the master list, we've already seen it
				if result['id'] in listings:
					results.remove(result)
					post_date = listings[result['id']]
					delta_t = now - post_date
					# If a listing is more than 30 days old, remove it
					if delta_t.days > 30:
						del listings[result['id']]
				# Add it to the master list
				else:
					listings[result['id']] = now
			# Dump the updated list of search results
			pickle.dump(listings, open(script_opts['log_file'], 'wb'))

		# This is the first time this search is being run
		else:
			listings = {}
			for result in results:
				listings[result['id']] = now
			# Dump the new list of search results
			pickle.dump(listings, open(script_opts['log_file'], 'wb'))

	if len(results) == 0:
		print "No new listings that fit your search."

	elif args.email is not None:
		email_results(args.email, results, search_opts, script_opts.get('template_file'))

	else:
		# No email option, so print by default
		for result in results:
			print str(result['title']) + ' - ' + result['url']

def email_results(config, results, params=None, template_file=None):
	if template_file == None:
		template_file = 'default.html'

	with open(config) as email_config:
		pvt_config = json.load(email_config)

	user = pvt_config['user']
	key = pvt_config['key']
	to = pvt_config['to']

	for recipient in to: 
		html_text = get_html(params, results, template_file)
		emailer.send_gmail(user, key, recipient, 'CL Listings', 'Could not load html.', html_text)
		print "Email Sent to: " + recipient

def get_html(params, results, template_file):
	templateLoader = jinja2.FileSystemLoader( searchpath="templates/" )
	templateEnv = jinja2.Environment( loader=templateLoader )
	template = templateEnv.get_template( template_file )
	context = {'params': params, 'results': results}
	return template.render(context)

def main():
	args = getargs()
	if args.config is None:
		print "##################################\nShowing a simple scrape of SF housing.\n##################################"
		url = 'https://sfbay.craigslist.org/search/apa?search_distance=3&postal=94115&min_bedrooms=3&availabilityMode=0'
		simple_scrape(url)
	else:
		custom_scrape(args)

if __name__ == "__main__":
    main()