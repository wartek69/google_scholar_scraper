import requests
import time 
from threading import Thread
def test_function(i, url, session):
    print('entered function ' + str(i))
    session.get('http://127.0.0.1:'+str(i))
    print('done request ' + str(i))
    session.get('http://api.scraperapi.com?api_key=a6805e53ff13215056f0cfd864eeb760&url='+url+'&keep_headers=true')
    print('done second request ' + str(i))

    time.sleep(1)
    print('done sleeping ' + str(i))
if __name__ == '__main__':
    start = time.time()
    running_processes = []
    pagerequest = []
    sessions = []
    sessions.append(requests.Session())
    sessions.append(requests.Session())
    pagerequest.append('https://scholar.googleusercontent.com/scholar.bib?q=info:JipSOu2dbLsJ:scholar.google.com/&output=citation&scisdr=CgVAB-cUEIXZspeXsk4:AAGBfm0AAAAAXn-Sqk7l2j-ISXaVloTA-PrE3tFs2myh&scisig=AAGBfm0AAAAAXn-SqsckVUuJdmBhGQvPRFW9G1-5NTXo&scisf=4&ct=citation&cd=-1&hl=en')

    pagerequest.append('https://link.springer.com/article/10.1007/s11605-016-3325-6')

    for i in range(0, 2):

        running_processes.append(Thread(target = test_function, args=(6969 + i,pagerequest[i], sessions[i])))
        running_processes[i].start()
    
    for thread in running_processes:
        thread.join()
    stop = time.time()
    print('done, took us {}'.format(stop-start))