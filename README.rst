==================
craigslist-scraper
==================

.. image:: https://badge.fury.io/py/craigslist-scraper.png
    :target: https://badge.fury.io/py/craigslist-scraper

.. image:: https://travis-ci.org/narfman0/craigslist-scraper.png?branch=master
    :target: https://travis-ci.org/narfman0/craigslist-scraper


A simple library for scraping custom craigslist searches.

Usage
-----

usage: scraper.py [-h] [-c CONFIG] [-e EMAIL]

Scrape a craigslist housing search and return appealing deals.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        json file name for your craigslist search
                        configuration. See configurations/config.json for
                        examples.
  -e EMAIL, --email EMAIL
                        Use this flag if you would like the results to be
                        emailed. This flag should point to a configuration
                        file with email credentials. See
                        configurations/email.config for examples.
	
Example:

	| ~$ python scraper.py -c configurations/config.json -e configurations/email.config  
	| ~$ Scraping search page 1 of 2  
	| ~$ Scraping search page 2 of 2  
	| ~$ Email Sent!  

License
-------

Copyright (c) 2015-2017 Jon Robison

Copyright (c) 2017 Christian Wawrzonek

See included LICENSE for licensing information
