from flask import Flask, render_template, request, redirect, url_for
import urllib
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        print(request.form)
        state = request.form["state"]
        city = request.form["city"]
        return redirect(url_for("results", state=state, city=city))
    else:
        return render_template("search.html")


@app.route("/results/<state>_<city>", methods=["POST", "GET"])
def results(state, city):
    city = city
    state = state
    if request.method == "POST":
        url_temp = request.form["url"]
        print(request.form)
        print(url_temp)
        if url_temp[0] == "/":
            print("ahhhhhhhhhhhhhhh")
            url_temp = url_temp[1:]

        return redirect(url_for("activity", url=url_temp, city=city, state=state))
    else:
        url = get_url(state, city)
        dct = get_things_to_do(url)
        return render_template("results.html", dct=dct)


@app.route("/activity/<state>/<city>/<url>")
def activity(url, city, state):
    new_url = "https://www.tripadvisor.com/" + url
    dct = get_activity_page(new_url, city)
    return render_template("activity.html", dct=dct, city=city, state=state)


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``"""


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


def get_url(state, city):
    links = []
    query = "tripadvisor " + state + " " + city
    subquery = city + " " + state

    search_results = scrape_google(query)
    for link in search_results:
        if "https://www.tripadvisor.com/Attractions" in link:
            links.append(link)
    valid_url = str(min(links, key=len))
    index = valid_url.find(subquery.replace(" ", "_"))
    final_url = valid_url[:index] + "a_allAttractions.true-" + valid_url[index:]
    return final_url


def get_things_to_do(url):
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
    for x in soup.body.find_all(class_="bUshh o csemS"):
        lst.append(slicer(x.text, " "))
        print(x.text.replace(" ", "+"))
        lst3.append(x.text.replace(" ", "+"))
        if len(lst) == 5:
            break
    for x in soup.body.find_all(target="_blank", class_="FmrIP _R w _Z P0 M0 Gm ddFHE"):
        lst2.append(x['href'])
        if len(lst2) == 5:
            break
    dct = {lst[i]: lst2[i] for i in range(len(lst))}
    dct["hidden"] = lst3
    print(dct)
    return dct


def get_activity_page(url, city):
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
    dct["description"] = soup.body.find(class_="pIRBV _T KRIav").text
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
    try:
        dct["title"] = soup.find(class_="Xewee").text
    except:
        print("couldnt add title")
    t = soup.find_all(class_="bfQwA _G B- _S _T c G_ P0 ddFHE cnvzr")
    for i in t:
        if "now" in i.text:
            dct["open/close"] = i.text
        print(i.text)
    return dct


def slicer(strr, substr):
    index = strr.find(substr)
    if index != -1:
        return strr[index+1:]


if __name__ == "__main__":
    app.run(debug=True)




"""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
       <h1>Home Page! </h1>
        {% for x in range(10) %}
            {% if x % 2 == 1 %}
                <p>{{x}}</p>
            {% endif %}
        {% endfor %}
    </body>
</html>

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
       <h1>Home Page! </h1>
        {% for x in content %}
            <p>{{x}}</p>
            {% if x == "tim" %}

            {% else %}

            {% endif %}
        {% endfor %}
    </body>
</html>
"""

"""
<head>
<title></title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript">
var citiesByState = {
Alabama: ["Huntsville", "Birmingham", "Montgomery"],
Alaska: ["Anchorage", "Juneau", "Fairbanks"],
Arizona: ["Phoenix", "Tucson", "Mesa"],
Arkansas: ["Little Rock", "Fort Smith", "Fayetteville"],
California: ["Los Angeles", "San Diego", "San Jose"],
Colorado: ["Denver", "Colorado Springs", "Aurora"],
Connecticut: ["Bridgeport", "Stamford", "New Haven"],
Delaware: ["Wilmington", "Dover", "Newark"],
Florida: ["Jacksonville", "Miami", "Tampa"],
Georgia: ["Atlanta", "Columbus", "Augusta"],
Hawaii: ["Honolulu", "East Honolulu", "Pearl City"],
Idaho: ["boise", "meridian", "Nampa"],
Illinois: ["Chicago", "Aurora", "Naperville"],
Indiana: ["Indianapolis", "Fort Wayne", "Evansville"],
Iowa: ["Des Moines", "Cedar Rapids", "Davenport"],
Kansas: ["Wichita", "Overland Park", "Kansas City"],
Kentucky: ["Louisville", "Lexington", "Bowling Green"],
Louisiana: ["New Orleans", "Baton Rouge", "Shreveport"],
Maine: ["Portland", "Lewiston", "Bangor"],
Maryland: ["Baltimore", "Columbia", "Germantown"],
Massachusetts: ["Boston", "Worcester", "Springfield"],
Michigan: ["Detroit", "Grand Rapids", "Warren"],
Minnesota: ["Minneapolis", "Saint Paul", "Rochester"],
Mississippi: ["Jackson", "Gulfport", "Southaven"],
Missouri: ["Kansas City", "Saint Louis", "Springfield"],
Montana: ["Billings", "Missoula", "Great Falls"],
Nebraska: ["Omaha", "Lincoln", "Bellevue"],
Nevada: ["Las Vegas", "Henderson", "Reno"],

}
function makeSubmenu(value) {
if(value.length==0) document.getElementById("citySelect").innerHTML = "<option></option>";
else {
var citiesOptions = "";
for(cityId in citiesByState[value]) {
citiesOptions+="<option>"+citiesByState[value][cityId]+"</option>";
}
document.getElementById("citySelect").innerHTML = citiesOptions;
}
}
function displaySelected() { var country = document.getElementById("countrySelect").value;
var city = document.getElementById("citySelect").value;
alert(country+"\n"+city);
}
function resetSelection() {
document.getElementById("countrySelect").selectedIndex = 0;
document.getElementById("citySelect").selectedIndex = 0;
}
</script>
</head>
<body onload="resetSelection()">
<select id="countrySelect" size="1" onchange="makeSubmenu(this.value)">
<option value="" disabled selected>Choose State</option>
<option>Odisha</option>
<option>Maharashtra</option>
<option>Kerala</option>
</select>
<select id="citySelect" size="1" >
<option value="" disabled selected>Choose City</option>
<option></option>
</select>
<button onclick="displaySelected()">show selected</button>
"""