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

    for link in scrape_google(query):
        if "https://www.tripadvisor.com/Attractions" in link:
            if state.replace(" ", "_") in link and city.replace(" ", "_") in link:
                links.append(link)
    valid_url = str(min(links, key=len))
    index = valid_url.find(subquery.replace(" ", "_"))
    final_url = valid_url[:index] + "a_allAttractions.true-" + valid_url[index:]
    print(final_url)
    return final_url


def get_url_activity(query):
    """Grabs the right tripadvisor url that leads to exact activity page based on user query"""
    states = ["Alabama",
              "Alaska",
              "Arizona",
              "Arkansas",
              "California",
              "Colorado",
              "Connecticut",
              "Delaware",
              "Florida",
              "Georgia",
              "Hawaii",
              "Idaho",
              "Illinois",
              "Indiana",
              "Iowa",
              "Kansas",
              "Kentucky",
              "Louisiana",
              "Maine",
              "Maryland",
              "Massachusetts",
              "Michigan",
              "Minnesota",
              "Mississippi",
              "Missouri",
              "Montana",
              "Nebraska",
              "Nevada",
              "New Hampshire",
              "New Jersey",
              "New Mexico",
              "New York",
              "North Carolina",
              "North Dakota",
              "Ohio",
              "Oklahoma",
              "Oregon",
              "Pennsylvania",
              "Rhode Island",
              "South Carolina",
              "South Dakota",
              "Tennessee",
              "Texas",
              "Utah",
              "Vermont",
              "Virginia",
              "Washington",
              "West Virginia",
              "Wisconsin",
              "Wyoming"]
    get_state = get_city = single_link = ""
    for link in scrape_google("https://www.tripadvisor.com/Attractions " + query):
        if "https://www.tripadvisor.com/Attraction_" in link:
            single_link = link.replace("https://www.tripadvisor.com/", "")
    url = single_link.split(".")[0].split("-")[-1]
    for state in states:
        state = state.replace(" ", "_")
        if state in url:
            get_state = state
            get_city = url.replace(state, "")[:-1]
    return single_link, get_state, get_city


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
    lst1 = [f"{count+1}. {slicer(x.text, ' ')}" for count, x in enumerate(soup.body.find_all(class_="bUshh o csemS"))]
    lst2 = [x['href'] for x in soup.body.find_all(target="_blank", class_="FmrIP _R w _Z P0 M0 Gm ddFHE")]
    dct = {lst1[i]: lst2[i] for i in range(len(lst1))}
    fnl_lst = [{lst1[i]: lst2[i]} for i in range(len(lst1))]
    return dct, fnl_lst, lst1


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

    addresses = soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr bTBvn")
    for address in addresses:
        if city in str(address.text):
            dct["address"] = address.text

    validate_addresses = soup.find_all(class_="dIDBU MJ")
    for address in validate_addresses:
        address = address.text
        if city in str(address):
            dct["address"] = address[7:] if "Address" in address else address

    try:
        """We only do this because there is possibility dct["address"] !=, so don't overwrite"""
        if dct["address"] == "How the site works":
            dct["address"] = "Not Available"
    except:
        dct["address"] = "Not Available"


    rating_star = soup.find_all(class_="WlYyy diXIH brhTq bQCoY")
    for rating in rating_star:
        if "/" in rating.text:
            try:
                dct["rating"] = slicer(slicer(str(rating.text), ":"), ":")
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
        dct["title"] = "Not Available"
        print("couldnt add title")

    open_hours = soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr")
    for hours in open_hours:
        if "now" in hours.text:
            dct["open/close"] = hours.text
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
            line = i.text
            if count in (4, 5) and len(line) >= 30:
                user["review"] = line[:-9]
            if count in (6, 7, 8) and "Written" in line and line != "":
                user["date"] = slicer_after(i.text, "This")
            count += 1
        dct[user_num] = user
    if dct["description"] == dct["user1"]["review"]:
        dct["description"] = "Not Available"
    return dct


def get_activity_page2(url, city):
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
    scrape_dct = {"description": "pIRBV _T KRIav",
                  "hours": "cOXcJ",
                  "title": "Xewee",
                  "reviewamount": "WlYyy diXIH bGusc dDKKM"}
    dct = {}
    for key, value in scrape_dct.items():
        scraper = soup.body.find(class_=value).text if key == "description" else soup.find(class_=value).text
        try:
            dct[key] = scraper
        except:
            dct[key] = "Not Available"
            print(f"could not find {key}")

    if dct["description"] == dct["user1"]["review"]:
        dct["description"] = "Not Available"

    for address in soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr bTBvn"):
        if city in str(address.text):
            dct["address"] = address.text

    for validate_addresses in soup.find_all(class_="dIDBU MJ"):
        address = validate_addresses.text
        if city in str(address):
            dct["address"] = address[7:] if "Address" in address else address

    try:
        """We only do this because there is possibility dct["address"] !=, so don't overwrite"""
        if dct["address"] == "How the site works":
            dct["address"] = "Not Available"
    except:
        dct["address"] = "Not Available"

    for rating in soup.find_all(class_="WlYyy diXIH brhTq bQCoY"):
        if "/" in rating.text:
            try:
                dct["rating"] = slicer(slicer(str(rating.text), ":"), ":")
            except:
                print("couldnt add ratings")

    for hours in soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr"):
        if "now" in hours.text:
            dct["open/close"] = hours.text

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
        user_num = f"user{num}"
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
            line = i.text
            if count in (4, 5) and len(line) >= 30:
                user["review"] = line[:-9]
            if count in (6, 7, 8) and "Written" in line and line != "":
                user["date"] = slicer_after(i.text, "This")
            count += 1
        dct[user_num] = user
    return dct


def slicer(s, substr):
    """Slice string before given substr"""
    if (index := s.find(substr)) != -1:
        return s[index+1:]


def slicer_after(s, substr):
    """Slice everything after given substr"""
    if (index := s.find(substr)) != -1:
        return s[:index]


def slicer_chars(s):
    """Slice string up to the first number, if no number, return back string"""
    for i, c in enumerate(s):
        if c.isdigit():
            return s[i:]
    return s
