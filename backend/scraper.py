from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests
import urllib


def get_source(url):
    """Method to help connect to response"""
    try:
        session = HTMLSession()
        response = session.get(url)
        return response
    except requests.exceptions.RequestException as e:
        print(e)


def scrape_google(query):
    """Google scraper that grabs the tripadvisor url needed based off city/state"""
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


def get_url(state, city):
    """Grabs the right tripadvisor url that leads to "To do page" and not the 2nd page url"""
    links = []
    query = "https://www.tripadvisor.com/Attractions " + state + " " + city
    subquery = city + " " + state

    search_results = scrape_google(query)
    for link in search_results:
        if "https://www.tripadvisor.com/Attractions" in link:
            if state.replace(" ", "_") in link:
                if city.replace(" ", "_") in link:
                    links.append(link)
    valid_url = str(min(links, key=len))
    index = valid_url.find(subquery.replace(" ", "_"))
    final_url = valid_url[:index] + "a_allAttractions.true-" + valid_url[index:]
    print(final_url)
    return final_url


def get_things_to_do(url):
    """Returns a list of activities to do based on user city/state"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

    req = requests.get(url, headers=headers, timeout=5, verify=False)
    print(req.status_code)
    soup = BeautifulSoup(req.content, 'html.parser')
    lst = []
    lst2 = []
    lst3 = []
    fnl_lst = []
    counting = 1
    for x in soup.body.find_all(class_="bUshh o csemS"):
        listed_title = str(counting) + ". " + slicer(x.text, " ")
        counting += 1
        lst.append(listed_title)
        lst3.append(x.text.replace(" ", "+"))
        if len(lst) == 15:
            break
    for x in soup.body.find_all(target="_blank", class_="FmrIP _R w _Z P0 M0 Gm ddFHE"):
        lst2.append(x['href'])
        if len(lst2) == 15:
            break
    dct = {lst[i]: lst2[i] for i in range(len(lst))}
    dct["hidden"] = lst3

    for i in range(len(lst)):
        fnl_lst.append({lst[i]: lst2[i]})
    return dct, fnl_lst, lst


def get_activity_page(url, city):
    """Scrapes tripadvisor for title, open hours, open/close, address, description, ratings, reviews"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,mr;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    req = requests.get(url, headers=headers, timeout=5, verify=False)
    soup = BeautifulSoup(req.content, 'html.parser')
    dct = {}
    try:
        dct["description"] = soup.body.find(class_="pIRBV _T KRIav").text
    except:
        dct["description"] = "No Description Available"
    x = soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr bTBvn")
    for i in x:
        if city in str(i.text):
            dct["address"] = i.text

    xxx = soup.find_all(class_="dIDBU MJ")
    for i in xxx:
        if city in str(i.text):
            txt = i.text
            if "Address" in txt:
                dct["address"] = txt[7:]
            else:
                dct["address"] = i.text
    xx = soup.find_all(class_="WlYyy diXIH brhTq bQCoY")
    for i in xx:
        if "/" in i.text:
            try:
                dct["rating"] = slicer(slicer(str(i.text), ":"), ":")
            except:
                print("couldnt add ratings")
    try:
        dct["hours"] = soup.find(class_="cOXcJ").text
    except:
        print("couldnt add hours")
        dct["hours"] = "Not Available"
    try:
        dct["title"] = soup.find(class_="Xewee").text
    except:
        print("couldnt add title")

    t = soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr")
    for i in t:
        if "now" in i.text:
            dct["open/close"] = i.text
    try:
        dct["reviewamount"] = soup.find(class_="WlYyy diXIH bGusc dDKKM").text
    except:
        print("coudlnt add reviewamount")

    ratings = soup.find_all(class_="cLUvi")
    try:
        dct["rating5"] = slicer_chars(ratings[0].text)
        dct["rating4"] = slicer_chars(ratings[1].text)
        dct["rating3"] = slicer_chars(ratings[2].text)
        dct["rating2"] = slicer_chars(ratings[3].text)
        dct["rating1"] = slicer_chars(ratings[4].text)
    except:
        print("couldnt add ratings 1-5")

    for num in range(1, 4):
        user_num = "user" + str(num)
        count = 0
        user = {}
        try:
            userinfo = soup.find_all(class_="ffbzW _c")[num-1]
        except:
            user["review"] = "None"
            user["date"] = "None"
            count += 1
            dct[user_num] = user
            continue
        user["name"] = userinfo.find(class_="WlYyy cPsXC dTqpp").text
        for i in userinfo:
            #(print(count, i.text))
            if count == 4 and len(i.text) >= 30:
                user["review"] = i.text[:-9]
            if count == 5 and len(i.text) >= 30:
                user["review"] = i.text[:-9]
            if count == 6 and "Written" in i.text:
                user["date"] = slicer_after(i.text, "This")
            if count == 7 and "Written" in i.text and i.text != "" :
                user["date"] = slicer_after(i.text, "This")
            if count == 8 and "Written" in i.text:
                user["date"] = slicer_after(i.text, "This")
            count += 1
        dct[user_num] = user
    return dct


def slicer(s, substr):
    index = s.find(substr)
    if index != -1:
        return s[index+1:]


def slicer_chars(s):
    for i, c in enumerate(s):
        if c.isdigit():
            new_str = s[i:]
            return new_str
    return s


def slicer_after(s, substr):
    index = s.find(substr)
    if index != -1:
        return s[:index]


