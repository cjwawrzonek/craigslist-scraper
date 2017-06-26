# Many thanks to github user narfman0 for providing the basis of this code
# in his project https://github.com/narfman0/craigslist-scraper

import re, requests
import math

from bs4 import BeautifulSoup

class CLSearch(object):
    """ Scrape of a search """
    def __init__(self, url, config=None):
        if 'craigslist.org/search/' not in url:
            raise ValueError('Not a valid craigslist search url: ' + url)

        self.soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        self.area = url.split('.craigslist.org')[0].split('://')[-1]
        self.search_type = url.split('.org/search/')[1].split('?')[0]
        self.listings = []

        self.filter_options = {}
        if 'filter_options' in config:
            self.filter_options = config['filter_options']

        # When scraping a search, don't go beyond 'max_pages'
        if 'max_pages' in self.filter_options:
            self.max_pages = int(self.filter_options['max_pages'])
        else:
            self.max_pages = 10

        page_num = 0
        page_size = to_int(self.tag_text(self.get_tag('.rangeTo')))
        total_entries = to_int(self.tag_text(self.get_tag('.totalcount')))
        total_pages = int(math.ceil(float(total_entries) / float(page_size)))
        while page_num < total_pages:
            page_num += 1
            if page_num > self.max_pages:
                return
            print "Scraping search page {} of {}".format(page_num, total_pages)
            self.parse_soup()
            next_button_tag = self.get_tag('a.button.next')
            if 'href' in next_button_tag.attrs:
                next_url = 'https://' + self.area + '.craigslist.org' + next_button_tag.attrs['href']
                self.soup = BeautifulSoup(requests.get(next_url).text, 'html.parser')
            else:
                break

    def parse_soup(self):
        results = self.get_tags('ul.rows li.result-row')

        for result in results:
            listing = {}

            img = result.select_one('a.result-image')
            img_ids = None
            if 'data-ids' in img.attrs:
                img_ids = img.attrs['data-ids']
                first_id = img_ids.split(',')[0].split(':')[1]
                listing['img_url'] = 'https://images.craigslist.org/{}_300x300.jpg'.format(first_id)
            else:
                listing['img_url'] = ''            

            info = result.select_one('.result-info')
            result_title = info.select_one('.result-title')
            listing['title'] = result_title.find(text=True)
            listing['url'] = 'https://' + self.area + '.craigslist.org' + result_title.attrs['href']
            listing['id'] = result_title.attrs['href'].split('/')[-1].split('.')[0]

            try:
                listing['price'] = to_int(info.select_one('.result-price').find(text=True))
            except:
                listing['price'] = 'n/a'

            # Housing specific listings, will have to work on generalization
            if self.search_type == 'apa':
                try:
                    housing = info.select_one('.housing')
                    listing['bdr'] = to_int(housing.find(text=True).split('-')[0].strip(' \n'))
                except:
                    listing['bdr'] = 'n/a'

            self.listings.append(listing)

    def load_page(self, url):
        """ Load and parese another html page, and reset the soup """
        self.soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    def listings(self):
        return self.listings

    def get_tag(self, selector):
        return self.soup.select(selector)[0]

    def get_tags(self, selector):
        return self.soup.select(selector)

    def tag_text(self, tag):
        """ Non-recursively extract text from a tag """
        return tag.find(text=True, recursive=False).strip()

    def get_strings(self, selector):
        """ Extract all tag strings matching selector """
        tags = self.get_tags(selector)
        return [ self.tag_text(tag) for tag in tags ]


def to_int(val):
    return int(re.sub('[^0-9]', '', val))
