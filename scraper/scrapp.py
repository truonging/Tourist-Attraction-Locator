import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession


def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response
    except requests.exceptions.RequestException as e:
        print(e)


def scrape_google(query):
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)
    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.',
                      'https://google.',
                      'https://webcache.googleusercontent.',
                      'http://webcache.googleusercontent.',
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')
    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)
    return links


links = []
state = "Ohio"
city = "Columbus"
query = "tripadvisor " + state + " " + city
subquery = city + " " + state

search_results = scrape_google(query)
for link in search_results:
    if "https://www.tripadvisor.com/Attractions" in link:
        links.append(link)
valid_url = str(min(links, key=len))
index = valid_url.find(subquery.replace(" ", "_"))
final_url = valid_url[:index] + "a_allAttractions.true-" + valid_url[index:]
print(final_url)
