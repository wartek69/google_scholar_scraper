import scholarly
import requests
import datetime
import hashlib
import random
import re
from HealtNewsScraper import HealthNewsScraper
from DoctorInfo import DoctorInfo
import pickle
_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


class ScholarScraper:
    def __init__(self, logger):
        self.health_news_scraper = HealthNewsScraper(logger)
        self.logger = logger

    def construct_regex_first_last_name(self, first_name, last_name):
        regex = '('
        for char in first_name:
            regex += char + '(?:\w*|\.) '
        regex += last_name + ')'
        return regex

    def construct_regex_last_first_name(self, first_name, last_name):
        regex = '(' + last_name + ','
        for char in first_name:
            regex += ' {0}\w+| {0}\.?$'.format(char)
        regex += last_name + ')'
        return regex

    def extract_full_names(self, page, author_names_list, first_name_first):
        try:
            extracted_full_names = []
            for name in author_names_list:
                # 8230 is an ellipse ..., three dots but in one char
                name_parts = name.strip().replace('.', '').replace(chr(8230), '').split(' ')
                if first_name_first:
                    regex = self.construct_regex_first_last_name(name_parts[0], name_parts[1])
                else:
                    regex = self.construct_regex_last_first_name(name_parts[0], name_parts[1])
                results = re.search(regex, page.text, re.IGNORECASE)
                extracted_full_names.append(results.groups(0)[0])
            return extracted_full_names
        except Exception: 
            self.logger.error('Failed to extract the full name')
            return ['unknown'] * len(author_names_list)

    def change_name_order(self, names):
        changed_names = []
        for name in names:
            name_parts = name.split(',')
            if len(name_parts) < 2:
                self.logger.warning('received an invalid name '+str(name_parts))
                continue
            changed_names.append(name_parts[1].strip() + ' ' + name_parts[0])
        return changed_names
    
    def manually_extract_full_names(self, page, author_names_list):
        full_names = self.extract_full_names(page, author_names_list, True)
        if 'unknown' in full_names:
            self.logger.info('retrying to extract the names using other regex')
            full_names = self.extract_full_names(page, author_names_list, False)
            if not 'unknown' in full_names:
                full_names = self.change_name_order(full_names)
        return full_names

    def scrape_google_scholar(self, query, year, start, results):
        self.logger.info('starting one process')
        request_session = "requests.Session()"
        scraped_data_collection = []
        url = '/scholar?q={0}&as_ylo={1}&hl=en&start={2}'.format(requests.utils.quote(query), year, start)
        #publication_generator = scholarly.search_pubs_custom_url(url, request_session)
        publications = scholarly.search_pubs_custom_url_no_gen(url, request_session)
        i = 0
        for pub_object in publications:
            try:
                #pub_object = next(publication_generator)
                pub_object.fill(request_session) #make sure to use a proxy while filling
                author_names = pub_object.bib['author']
                # delete these lines if using manual name extraction
                author_names_list = author_names.split(' and ')
                full_names = author_names_list
                full_names = self.change_name_order(author_names_list)
                # till here
                article_url = pub_object.bib['url']
                    
                #page = request_session.get(article_url, headers=_HEADERS, cookies = _COOKIES)
                #full_names = self.manually_extract_full_names(page, author_names_list)
                j = 0
                for full_name in full_names:
                    doc_info = DoctorInfo()
                    doc_info.query = query
                    if 'year' in pub_object.bib:
                        doc_info.year = pub_object.bib['year']
                    if 'journal' in pub_object.bib:
                        doc_info.journal = pub_object.bib['journal']

                    doc_info.scraped_name = str(author_names_list[j])
                    doc_info.url = str(article_url)
                    if not 'unknown' in full_names:
                        doc_info.full_name = str(full_name)
                        self.health_news_scraper.scrape_data(full_names[j], doc_info)                            
                    scraped_data_collection.append(doc_info)
                    j += 1

                self.logger.info('Done processing {} item'.format(i + start))
            except Exception as e:
                self.logger.error('failed {0} because {1}'.format(i, str(e)))
            finally:
                i += 1
        self.logger.info('inserting in queue...')
        results.put(scraped_data_collection)
        self.logger.info('Done All!')

