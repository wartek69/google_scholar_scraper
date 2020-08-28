import scholarly
import requests
import datetime
import time
from threading import Thread
from multiprocessing import Process
from ScholarScraper import ScholarScraper
from multiprocessing import Queue
from flask import Flask, render_template, request, jsonify, Response
import logging
import json
from DoctorInfo import DoctorInfo
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
logger = logging.getLogger()
busyScraping = False


@app.route("/scrape/healthnews", methods = ['GET'])
def get_healthnews_info():
    global busyScraping
    args = request.args
    if not 'query' in args:
        logger.error('no query parameters provided, exiting!')
        return json.dumps({'error':'no query parameter provided'})

    if busyScraping:
        logger.warning('already executing a scraping job, wait till the first one is finished...')
        return json.dumps({'error':'server already executing a scraping job, wait till it is finished'})
    busyScraping = True
    response = scrape_data(args['query'])
    busyScraping = False
    #response = response.replace('\\', '')

    response = json.loads(response)
    return Response(json.dumps(response),  mimetype='application/json')



def scrape_data(query):
    start = time.time()
    gs_scraper = ScholarScraper(logger)
    #query = input('Please provide a keyword: ')
    year = datetime.date.today().year - 4
    running_processes = []
    result_queue = Queue()

    for i in range(0, 5):
        running_processes.append(Process(target = gs_scraper.scrape_google_scholar, args=(query, year, i * 10, result_queue)))
        running_processes[i].start()
    results_list = []

    #if you do not empty the queue before joining there is a deadlock
    while 1:
        running = any(p.is_alive() for p in running_processes)
        while not result_queue.empty():
            results_list.append(result_queue.get())
        time.sleep(1)
        if not running:
            break

    for process in running_processes:
        process.join()
    with open('scraped_data.csv', 'w') as f:
        print('Starting to write to file')
        f.write("scraped_name;full_name;health_news_name;year;speciality;sub_speciality;experience;languages;city_state;patient_experience;url;journal;query\n")
        i = 0
        json_object = '['
        for scraped_data in results_list:
            for data_entry in scraped_data:
                f.write(data_entry.to_csv())
                #print('wrote line {}'.format(i))
                json_object += data_entry.to_json() + ','
                i += 1
    json_object = json_object[:-1] + ']'
    stop = time.time()
    logger.info('done execution, {} seconds passed'.format(stop-start))
    logger.info('returning json: {}'.format(json_object))
    return json_object

    


if __name__ == '__main__':    
    app.run(host='0.0.0.0')
