# doctorscraper
Scraping tool that scrapes author names from google scholar and then tries to extract more information of the authors of the best papers from healthnews.us
Additional information that gets extracted include things like ratings, reviews, speciality, working place, ...
The scraper was embedded in a flask application so that the results could be easily represented in a webserver.
In this project all the results were connected to a wordpress site and displayed there.

## Scraping google
Google scholar does not like to be scraper, to get around this proxies can be used.
An example of a proxy provider that I used is: scraperapi.com
Another alternative is: https://scrapestack.com/

## Scholary
Scholarly is a python interface to scrape google scholar. For this project scholarly was cloned and slightly modified to use proxies described earlier. First the scraperapi proxy is used, if it fails multiple requests a switch is made to scraperstack proxy.
Both of these proxy providers have a free plan.
Once registered there, you can add your api keys to the `__get_page` function in the `scholarly.py` file.


## Run
```python3 scraper.py```
