from flask import Flask, render_template, request, redirect, url_for
from flask_fontawesome import FontAwesome
import urllib
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
import os
import mysql.connector

app = Flask(__name__)
fa = FontAwesome(app)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rtruong3990",
    database="361_project"
)


@app.route("/")
def home():
    """Home Page"""
    return render_template("index.html")


@app.route("/owned_activities", methods=["POST", "GET"])
def owned_activities():
    """Page that dynamically displays user saved activities from mysqldb and lets users delete activity from table"""
    if request.method == "POST":
        print(request.form)
        if request.form["action"] == "delete":
            ID = request.form["ID"]
            mycursor = mydb.cursor()
            sql = f"DELETE FROM activities WHERE ID = '{ID}'"
            mycursor.execute(sql)
            mydb.commit()
            print(mycursor.rowcount, "record(s) deleted")
            mycursor.close()
        elif request.form["action"] == "go_to_activity":
            ID = request.form["ID"]
            mycursor = mydb.cursor()
            sql = f"SELECT city, state, url FROM activities WHERE ID = '{ID}'"
            mycursor.execute(sql)
            city, state, url = mycursor.fetchone()
            return redirect(url_for("activity", city=city, state=state, url=url))

            pass
    mycursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM activities"
    mycursor.execute(query)
    result = mycursor.fetchall()
    mycursor.close()
    return render_template("owned_activities.html", database=result)


@app.route("/search", methods=["POST", "GET"])
def search():
    """Search Page"""
    # if receive POST, redirects to result page with state,city
    if request.method == "POST":
        print("the request form:", request.form)
        state = request.form["state"]
        city = request.form["city"]
        return redirect(url_for("results", state=state, city=city, sort="False"))
    else:
        return render_template("search.html")


@app.route("/results/Page_1/<state>_<city>_<sort>", methods=["POST", "GET"])
def results(state, city, sort):
    """Results Page after selecting State/City"""
    # if receive POST, redirect to activity page the url,city,state
    data = (state, city, sort, "results")
    if request.method == "POST":
        print(request.form)
        if request.form["next_page"] == "True":
            return next_page(data, "2")
        if request.form["sort_by"] == "True":
            return sort_page(data)
        else:
            return loading_page(data)
    else:
        return result_page(data)


@app.route("/results/Page_2/<state>_<city>_<sort>", methods=["POST", "GET"])
def results2(state, city, sort):
    data = (state, city, sort, "results2")
    if request.method == "POST":
        print(request.form)
        if request.form["next_page"] == "True":
            return next_page(data, "3")
        if request.form["sort_by"] == "True":
            return sort_page(data)
        else:
            return loading_page(data)
    else:
        return result_page(data)


@app.route("/results/Page_3/<state>_<city>_<sort>", methods=["POST", "GET"])
def results3(state, city, sort):
    data = (state, city, sort, "results3")
    if request.method == "POST":
        print(request.form)
        if request.form["sort_by"] == "True":
            return sort_page(data)
        else:
            return loading_page(data)
    else:
        return result_page(data)


@app.route("/loading/<state>/<city>/<url>")
def loading(url, city, state):
    """Loading page for ad placement"""
    return render_template("loading_screen.html", url=url, city=city, state=state)


@app.route("/activity/<state>/<city>/<url>", methods=["POST", "GET"])
def activity(url, city, state):
    """Activity Page after selecting an activity from the list"""
    # calls scraper on tripadvisor and grabs all relevant info to put into dct
    new_url = "https://www.tripadvisor.com/" + url
    dct = get_activity_page(new_url, city)
    if request.method == "POST":
        if request.form["save_activity"] == "True":
            mycursor = mydb.cursor()
            sql = "INSERT IGNORE INTO activities (title, address, reviewAmount, rating, description, city, state, url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            val = save_activity_data(dct, city, state, url)
            mycursor.execute(sql, val)
            print(val)
            print(mycursor.rowcount, "was inserted.")
            mydb.commit()
            mycursor.close()
    try:
        calc_ratings(dct)
    except:
        print("couldnt calc_ratings")
    image = [i for i in os.listdir('static/images') if i.endswith('.jpeg')][0]
    image2 = [i for i in os.listdir('static/images') if i.endswith('.jpg')][0]
    image3 = [i for i in os.listdir('static/images') if i.endswith('.jpg')][1]
    return render_template("activity.html", dct=dct, city=city, state=state,
                           user_image=image, user_image2=image2, user_image3=image3)
                            # YOU CAN PROBABLY DELETE CITY AND STATE NOT USED IN HTML. TOO TIRED TO DO IT RN

def next_page(data, num):
    """Loads next page depending on if user clicked sort button or not"""
    state, city, sort, result = data
    result = ''.join([i for i in result if not i.isdigit()])
    result = result + num
    if sort == "False":
        return redirect(url_for(result, city=city, state=state, sort="False"))
    if sort == "True":
        return redirect(url_for(result, city=city, state=state, sort="True"))


def sort_page(data):
    """Loads current page depending if user clicked sort button or not"""
    state, city, sort, result = data
    if sort == "False":
        return redirect(url_for(result, state=state, city=city, sort="True"))
    if sort == "True":
        return redirect(url_for(result, state=state, city=city, sort="False"))


def loading_page(data):
    """Takes user to loading page that waits 5 seconds, passes data to activity page"""
    state, city, sort, result = data
    url_temp = request.form["url"]
    if url_temp[0] == "/":
        url_temp = url_temp[1:]
    return redirect(url_for("loading", url=url_temp, city=city, state=state))


def result_page(data):
    # get Tripadvisor url after sending in state/city to google and getting the results, grabs "Things to do" list
    # and return it as a dictionary with activity:url key,value
    state, city, sort, result = data
    url = get_url(state, city)
    dct, lst, lst_title = get_things_to_do(url)
    result = result + ".html"
    if sort == "False":
        return render_template(result, dct=dct, lst=lst, lst_title=lst_title)
    if sort == "True":
        dct, lst, lst_title = reverse_data(dct, lst, lst_title)
        return render_template(result, dct=dct, lst=lst, lst_title=lst_title)


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``"""


def save_activity_data(dct, city, state, url):
    """Turn dictionary data into tuple"""
    calc_ratings(dct)
    title = dct["title"]
    try:
        address = dct["address"]
    except:
        address = "Not Available"
    reviewAmount = dct["reviewamount"]
    rating = dct["rating"]
    try:
        description = dct["description"]
    except:
        description = "Not Available"
    return title, address, reviewAmount, rating, description, city, state, url


def reverse_data(dct, lst, lst_title):
    """Reverse all the given data"""
    new_dct = dict(reversed(list(dct.items())))
    lst.reverse()
    lst_title.reverse()
    return new_dct, lst, lst_title


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


def slicer_after(s, substr):
    index = s.find(substr)
    if index != -1:
        return s[:index]


def slicer_chars(s):
    for i, c in enumerate(s):
        if c.isdigit():
            new_str = s[i:]
            return new_str
    return s


def slicer_lname(s, substr):
    index = s.find(substr)
    if index != -1:
        return s[:index+2]


def slicer_chars_after(s):
    for i, c in enumerate(s):
        if c.isdigit():
            new_str = s[:i]
            return new_str
    return s


def calc_ratings(dct):
    star5 = int(dct["rating5"].replace(",", ""))
    star4 = int(dct["rating4"].replace(",", ""))
    star3 = int(dct["rating3"].replace(",", ""))
    star2 = int(dct["rating2"].replace(",", ""))
    star1 = int(dct["rating1"].replace(",", ""))

    score_total = (star5*5) + (star4*4) + (star3*3) + (star2*2) + star1
    response_total = star5 + star4 + star3 + star2 + star1
    tmp = {"rating": round(score_total/response_total, 2)}
    dct.update(tmp)
    return


if __name__ == "__main__":
    app.run(debug=True)
