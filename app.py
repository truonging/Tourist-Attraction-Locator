from flask import Flask, render_template, request, redirect, url_for
import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

# https://www.tripadvisor.com/Attractions-g53449-Activities-a_allAttractions.true-Pittsburgh_Pennsylvania.html
# https://www.tripadvisor.com/Attractions-g50207-Activities-a_allAttractions.true-Cleveland_Ohio.html


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        print(request.form)
        state = request.form["state"]
        city = request.form["city"]

        return redirect(url_for("results", state=state, city=city))
    else:
        return render_template("search.html")


@app.route("/search/<state>_<city>", methods=["POST", "GET"])
def results(state, city):
    url = get_url(state, city)
    return render_template("results.html", url=url)


@app.route("/activity")
def activity():
    return render_template("activity.html")


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
    return final_url


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