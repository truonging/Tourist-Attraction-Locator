from flask import Flask, render_template, request, redirect, url_for
from flask_fontawesome import FontAwesome
import os
import mysql.connector
from datetime import date
import backend as b


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
            mycursor.close()
            return redirect(url_for("activity", city=city, state=state, url=url))

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
    dct = b.get_activity_page(new_url, city)
    if request.method == "POST":
        print(request.form)
        if request.form["save_activity"] == "True":
            mycursor = mydb.cursor()
            sql = "INSERT IGNORE INTO activities (title, address, reviewAmount, rating, description, city, state, url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            val = b.save_activity_data(dct, city, state, url)
            mycursor.execute(sql, val)
            print(mycursor.rowcount, "was inserted.")
            mydb.commit()
            mycursor.close()
        elif request.form["write_review"] == "True":
            name = request.form["name"]
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

    image = [i for i in os.listdir('static/images') if i.endswith('.jpeg')][0]
    image2 = [i for i in os.listdir('static/images') if i.endswith('.jpg')][0]
    image3 = [i for i in os.listdir('static/images') if i.endswith('.jpg')][1]
    return render_template("activity.html", dct=dct, city=city, state=state,
                           user_image=image, user_image2=image2, user_image3=image3)
                            # YOU CAN PROBABLY DELETE CITY AND STATE NOT USED IN HTML. TOO TIRED TO DO IT RN


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


def result_page(data):
    # get Tripadvisor url after sending in state/city to google and getting the results, grabs "Things to do" list
    # and return it as a dictionary with activity:url key,value
    state, city, sort, result = data
    url = b.get_url(state, city)
    dct, lst, lst_title = b.get_things_to_do(url)
    result = result + ".html"
    if sort == "False":
        return render_template(result, dct=dct, lst=lst, lst_title=lst_title)
    if sort == "True":
        dct, lst, lst_title = b.reverse_data(dct, lst, lst_title)
        return render_template(result, dct=dct, lst=lst, lst_title=lst_title)


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``"""


if __name__ == "__main__":
    app.run(debug=True)
