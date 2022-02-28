from flask import Flask, render_template, request, redirect, url_for
from flask_fontawesome import FontAwesome   # used delete font
from datetime import date, datetime  # used to grab the current date if user submits review
import os   # used to grab images from static
import mysql.connector  # used to connect to MYSQL DB
import backend as b


# to do: if user enters invalid input in support, make bot say "could not find
# attraction, try again"
# grabs teammate service when loading activity page which results in saving/reviewing to have to call
# teammate service which makes loading slow, add when user save/review, return the imgs in url
# default=None at first


app = Flask(__name__)
fa = FontAwesome(app)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rtruong3990",
    database="361_project"
)


@app.route("/", methods=["POST", "GET"])
def home():
    """Home Page"""
    supquery = user = bot_name = bot_query = url = state = city = toggle = ""
    start_support = "False"
    if request.method == "POST":
        if request.form["support_submit"] != "":
            supquery = " : " + request.form["support_submit"]
            user = "User"
            bot_name = "Support Bot"
            bot_query = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
            url, state, city = b.get_url_activity(request.form["support_submit"])
            start_support = "True"
            print("yes ",url)
            toggle = "True"
    return render_template("index.html", supquery=supquery, user=user, bot_name=bot_name, bot_query=bot_query, url=url, state=state, city=city, start_support=start_support, toggle=toggle)


@app.route("/owned_activities", methods=["POST", "GET"])
def owned_activities():
    """Page that dynamically displays user saved activities from mysqldb and lets users delete activity from table"""
    supquery = user = bot_name = bot_query = url = state = city = toggle = ""
    start_support = "False"
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
            mycursor.close()
            return redirect(url_for("activity", city=city, state=state, url=url))
        elif request.form["support_submit"] != "":
            supquery = " : " + request.form["support_submit"]
            user = "User"
            bot_name = "Support Bot"
            bot_query = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
            url, state, city = b.get_url_activity(request.form["support_submit"])
            start_support = "True"
            toggle = "True"
    mycursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM activities"
    mycursor.execute(query)
    result = mycursor.fetchall()
    mycursor.close()
    return render_template("owned_activities.html", database=result, supquery=supquery, user=user, bot_name=bot_name, bot_query=bot_query, url=url, state=state, city=city, start_support=start_support, toggle=toggle)


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
    supquery = user = bot_name = bot_query = url = toggle = ""
    start_support = "False"
    data = (state, city, sort, "results")
    data2 = (supquery, user, bot_name, bot_query, url, toggle, start_support)
    if request.method == "POST":
        print(request.form)
        if request.form["next_page"] == "True":
            return next_page(data, "2")
        if request.form["sort_by"] == "True":
            return sort_page(data)
        elif request.form["support_submit"] != "":
            if request.form["support_submit"] == "False":
                return loading_page(data)
            else:
                supquery = " : " + request.form["support_submit"]
                user = "User"
                bot_name = "Support Bot"
                bot_query = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
                url, state, city = b.get_url_activity(request.form["support_submit"])
                print("@@@@@@@@@@@ ", url)
                start_support = "True"
                toggle = "True"
                data3 = (supquery, user, bot_name, bot_query, url, toggle, start_support)
                return result_page(data, data3)
    return result_page(data, data2)


@app.route("/results/Page_2/<state>_<city>_<sort>", methods=["POST", "GET"])
def results2(state, city, sort):
    supquery = user = bot_name = bot_query = url = toggle = ""
    start_support = "False"
    data = (state, city, sort, "results2")
    data2 = (supquery, user, bot_name, bot_query, url, toggle, start_support)
    if request.method == "POST":
        print(request.form)
        if request.form["next_page"] == "True":
            return next_page(data, "3")
        if request.form["sort_by"] == "True":
            return sort_page(data)
        elif request.form["support_submit"] != "":
            if request.form["support_submit"] == "False":
                return loading_page(data)
            else:
                supquery = " : " + request.form["support_submit"]
                user = "User"
                bot_name = "Support Bot"
                bot_query = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
                url, state, city = b.get_url_activity(request.form["support_submit"])
                print("@@@@@@@@@@@ ", url)
                start_support = "True"
                toggle = "True"
                data3 = (supquery, user, bot_name, bot_query, url, toggle, start_support)
                return result_page(data, data3)
    return result_page(data, data2)


@app.route("/results/Page_3/<state>_<city>_<sort>", methods=["POST", "GET"])
def results3(state, city, sort):
    supquery = user = bot_name = bot_query = url = toggle = ""
    start_support = "False"
    data = (state, city, sort, "results3")
    data2 = (supquery, user, bot_name, bot_query, url, toggle, start_support)
    if request.method == "POST":
        print(request.form)
        if request.form["sort_by"] == "True":
            return sort_page(data)
        elif request.form["support_submit"] != "":
            if request.form["support_submit"] == "False":
                return loading_page(data)
            else:
                supquery = " : " + request.form["support_submit"]
                user = "User"
                bot_name = "Support Bot"
                bot_query = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
                url, state, city = b.get_url_activity(request.form["support_submit"])
                print("@@@@@@@@@@@ ", url)
                start_support = "True"
                toggle = "True"
                data3 = (supquery, user, bot_name, bot_query, url, toggle, start_support)
                return result_page(data, data3)
    return result_page(data, data2)


@app.route("/loading/<state>/<city>/<url>")
def loading(url, city, state):
    """Loading page for ad placement"""
    return render_template("loading_screen.html", url=url, city=city, state=state)


@app.route("/activity/<state>/<city>/<url>", methods=["POST", "GET"])
def activity(url, city, state):
    """Activity Page after selecting an activity from the list"""
    # calls scraper on tripadvisor and grabs all relevant info to put into dct
    supquery = user = bot_name = bot_query = toggle = "" #i think i can remove city/state
    mateservice = False
    start_support = "False"
    new_url = "https://www.tripadvisor.com/" + url
    dct = b.get_activity_page(new_url, city)
    if request.method == "POST":
        print(request.form)
        if request.form["save_activity"] == "True":
            img1 = request.form["img1"]
            img2 = request.form["img2"]
            img3 = request.form["img3"]
            mateservice = True
            mycursor = mydb.cursor()
            sql = "INSERT IGNORE INTO activities (title, address, reviewAmount, rating, description, city, state, url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            val = b.save_activity_data(dct, city, state, url)
            mycursor.execute(sql, val)
            print(mycursor.rowcount, "was inserted.")
            mydb.commit()
            mycursor.close()
        elif request.form["write_review"] == "True":
            img1 = request.form["img1"]
            img2 = request.form["img2"]
            img3 = request.form["img3"]
            mateservice = True
            name = request.form["name"]
            if name == "":
                name = "Anonymous"
            review = request.form["review"]
            today = date.today()
            review_date = today.strftime("%B %d, %Y")
            review_date = "Written " + review_date
            mycursor = mydb.cursor()
            sql = "INSERT INTO user_reviews (name, review_date, review, url) VALUES (%s,%s,%s,%s)"
            mycursor.execute(sql, (name, review_date, review, new_url))
            print(mycursor.rowcount, "was inserted.")
            mydb.commit()
            mycursor.close()
        elif request.form["support_submit"] != "":
            if request.form["support_submit"] != "False":
                img1 = request.form["img1"]
                img2 = request.form["img2"]
                img3 = request.form["img3"]
                mateservice = True
                supquery = " : " + request.form["support_submit"]
                user = "User"
                bot_name = "Support Bot"
                bot_query = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
                url, state, city = b.get_url_activity(request.form["support_submit"])
                start_support = "True"
                toggle = "True"
    try:
        b.calc_ratings(dct)
    except:
        print("couldnt calc_ratings")

    # check if new_url in mysql url
    mycursor = mydb.cursor(dictionary=True)
    sql = f"SELECT * FROM user_reviews WHERE url = '{new_url}'"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    if len(result) >= 1:
        dct["user3"] = dct["user2"]
        dct["user2"] = dct["user1"]
        count = 1
        for x in result:
            if count == 4:
                break
            if count == 1:
                dct["user1"] = {"name": x["name"], "review": x["review"], "date": x["review_date"]}
            elif count >= 2:
                dct["user3"] = dct["user2"]
                dct["user2"] = dct["user1"]
                dct["user1"] = {"name": x["name"], "review": x["review"], "date": x["review_date"]}
            count += 1
    if not mateservice:
        img1, img2, img3 = b.call_teammate_service(dct["title"])

    return render_template("activity.html", dct=dct, city=city, state=state,
                           user_image1=img1, user_image2=img2, user_image3=img3, supquery=supquery, user=user,
                           bot_name=bot_name, bot_query=bot_query, url=url, start_support=start_support, toggle=toggle)


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``"""


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


def result_page(data, data2):
    # get Tripadvisor url after sending in state/city to google and getting the results, grabs "Things to do" list
    # and return it as a dictionary with activity:url key,value
    state, city, sort, result = data
    supquery, user, bot_name, bot_query, url, toggle, start_support = data2
    if start_support == "False":
        url = b.get_url(state, city)
        dct, lst, lst_title = b.get_things_to_do(url)
    else:
        dct, lst, lst_title = b.get_things_to_do(b.get_url(state, city))
    result = result + ".html"
    if sort == "False":
        return render_template(result, dct=dct, lst=lst, lst_title=lst_title, supquery=supquery, user=user, bot_name=bot_name, bot_query=bot_query, url=url, state=state, city=city, start_support=start_support, toggle=toggle)
    if sort == "True":
        dct, lst, lst_title = b.reverse_data(dct, lst, lst_title)
        return render_template(result, dct=dct, lst=lst, lst_title=lst_title, supquery=supquery, user=user, bot_name=bot_name, bot_query=bot_query, url=url, state=state, city=city, start_support=start_support, toggle=toggle)


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``"""


if __name__ == "__main__":
    app.run(debug=True)


