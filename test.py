
import re
import requests
import random
import hashlib

_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
request_session = requests.Session()

def construct_regex(first_name, last_name):
    regex = '('
    for char in first_name:
        regex += char + '(?:\w*|\.) '
    regex += last_name + ')'
    return regex

def extract_full_names(url, author_names_list):
    try:
        extracted_full_names = []
        for name in author_names_list:
            lol = name.strip()
            # 8230 is an ellipse ..., three dots but in one char
            test = lol.replace('.', '').replace(chr(8230), '')
            name_parts = test.split(' ')
            regex = construct_regex(name_parts[0], name_parts[1])
            page = request_session.get(url, headers=_HEADERS, cookies = _COOKIES)
            results = re.search(regex, page.text, re.IGNORECASE)
            extracted_full_names.append(results.groups(0)[0])
        return extracted_full_names
    except Exception: 
        print('Failed to extract the full name')
        test = ord(name[-1])
        return ['unknown'] * len(author_names_list)

if __name__ == '__main__':
    authors = ['ID Rosado', 'S Bhalla', 'LA Sanchez', 'RC Fields…']
    test = extract_full_names('https://link.springer.com/article/10.1007/s11605-016-3325-6', authors)