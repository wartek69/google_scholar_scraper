import requests
from bs4 import BeautifulSoup
import random
import hashlib
import re
import scholarly
import time
_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
regex_name_extraction = '(DR. )?({0}) ({1}(\w*|\.)) ({2})'
regex_name_extraction_no_middle_name = '(DR. )?({0}) ({1})'
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

class HealthNewsScraper:
    def __init__(self, logger):
        self.search_url = 'https://health.usnews.com/doctors/search?name={}'
        self.logger = logger
    
    def print_to_csv(self, data):
        with open('doc_data_test.csv', 'w') as f:
            self.logger.info('Starting to write to file')
            f.write("name;city;speciality;subspeciality;expyears;languages\n")
            for data_entry in data:
                for data_field in data_entry:
                    f.write(str(data_field) + ';')
                f.write('\n')

    def extract_doc_info(self, doctor_cards, regex, doc_info):
        for doctor_card in doctor_cards:
            card_main_body = doctor_card.contents[0].find(class_='DetailCardDoctor__CardContent-s1mtetnf-1 diabvp Box-s1krs5yn-0 ewBkVU')
            scraped_name = ""
            scraped_name = card_main_body.contents[0].contents[0].contents[0]
            if(not re.match(regex, scraped_name, re.IGNORECASE)):
                continue
            card_side_body = doctor_card.contents[0].contents[2]
            scraped_city_and_state = card_main_body.contents[1].contents[0]
            scraped_speciality= card_main_body.contents[2].contents[0]

            scraped_subspeciality = card_main_body.find(class_='DetailCardDoctor__SubSpecialties-s1mtetnf-2 cvglyM Paragraph-s10q84gy-0 UMIXI')
            if scraped_subspeciality is not None:
                scraped_subspeciality = scraped_subspeciality.contents[0]
            else:
                scraped_speciality = 'unknown'
            scraped_years_of_experience = card_side_body.contents[0].contents[1].contents[0]
            scraped_languages = card_side_body.contents[1].contents[1].contents[0]
            if len(card_side_body.contents) > 2:
                patient_experience_visualisation = card_side_body.contents[2].contents[1]
                scraped_patient_experience_objects = patient_experience_visualisation.find_all(class_= 'MeterChiclet__MeterChicletItem-s36bexq-1 ipczyO')
                doc_info.patient_experience = str(len(scraped_patient_experience_objects))
            doc_info.health_news_name = str(scraped_name)
            doc_info.city_state = str(scraped_city_and_state)
            doc_info.speciality = str(scraped_speciality)
            doc_info.sub_speciality = str(scraped_subspeciality)
            doc_info.experience = str(scraped_years_of_experience)
            doc_info.languages = str(scraped_languages)
            return
            
    def construct_regex_no_full_first_name(self, name_parts):
        self.logger.info('received a name without a full first name, doing a best try')
        regex = '(DR. ?'
        for char in name_parts[0]:
            regex += '(?: {0}\w+| {0}\.?)'.format(char)
        regex += ' ' + name_parts[1] + ')'
        return regex

    def prepare_regex(self, name_parts, doc_info):
        regex = ""
        if len(name_parts) == 3:
            regex = regex_name_extraction.format(name_parts[0], name_parts[1], name_parts[2])
        elif len(name_parts) == 2:
            if len(name_parts[0]) < 3:
                regex = self.construct_regex_no_full_first_name(name_parts)
                doc_info.using_full_name = False
            else:
                regex = regex_name_extraction_no_middle_name.format(name_parts[0], name_parts[1])
        else:
            self.logger.warning('Received an invalid name, returning no regex, name_parts: ' + str(name_parts))
            regex = ''
        self.logger.info('using regex: {}'.format(regex))
        return regex
        
    def prepare_query_url(self, full_name):
        encoded_url = self.search_url.format(requests.utils.quote(full_name))
        #self.logger.info('querying url: {}'.format(encoded_url))
        return encoded_url

    def scrape_data(self, full_name, doc_info):
        session = requests.Session()
        name_parts = full_name.split(' ')
        regex = self.prepare_regex(name_parts, doc_info)
        query_url = self.prepare_query_url(full_name)
        time.sleep(1) # sleep to not overload the server

        page = session.get(query_url, headers=_HEADERS, cookies = _COOKIES).text
        #page = scholarly.get_page(query_url, session)
        soup = BeautifulSoup(page, 'html.parser')
        doctor_cards = soup.find_all(class_='DetailCardDoctor__CustomDetailCard-s1mtetnf-0 dABtuG DetailCardAction__DetailCardContainer-s1aepz1p-0 iTQqDI Box-s1krs5yn-0 kJnoCb')
        self.extract_doc_info(doctor_cards, regex, doc_info)
        pass
    