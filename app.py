from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_fontawesome import FontAwesome
from datetime import date
import requests
import sys
sys.path.append('backend')
from sql_operations import sql_SELECT, sql_INSERT, sql_UPDATE, sql_DELETE
from scraper import get_url, get_things_to_do, get_activity_page
from the_rest_of_backend import tuple_from_data, calc_ratings, reverse_data, call_teammate_service, get_image_from_form, update_dct_reviews, get_support_variables, update_support_variables


app = Flask(__name__)
fa = FontAwesome(app)


@app.route("/activities/", methods=["GET", "POST"])
@app.route("/activities/<activity_id>", methods=["GET", "DELETE"])
@app.route("/activities/post/<title>/<address>/<reviewAmount>/<rating>/<description>/<city>/<state>/<url>", methods=["POST"])
@app.route("/activities/patch/<activity_id>/<title>/<address>/<reviewAmount>/<rating>/<description>/<city>/<state>/<url>", methods=["PATCH"])
def activities_API(activity_id=None, rating=None, title=None, address=None, reviewAmount=None, description=None, city=None, state=None, url=None):
    """REST API for activities data"""
    if request.method == "GET":
        if not activity_id:  # READ all activities
            sql = "SELECT * FROM activities"
            return jsonify(sql_SELECT(sql)), 200
        else:  # READ single activity
            sql = f"SELECT * FROM activities WHERE ID={activity_id}"
            return jsonify(sql_SELECT(sql, single=True)), 200

    elif request.method == "POST":  # CREATE new single activity
        sql = "INSERT IGNORE INTO activities (title, address, reviewAmount, rating, description, city, state, url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        sql2 = "SELECT * FROM activities ORDER BY ID DESC LIMIT 1;"
        if title is None:
            title, address, reviewAmount, rating, description, city, state, url = "Uhhhhh", "Uhhhhh", "Uhhhhh", "Uhhhhh", "Uhhhhh", "Uhhhhh", "Uhhhhh", "Uhhhhh"
        sql_INSERT(sql, (title, address, reviewAmount, rating, description, city, state, url))
        return jsonify(sql_SELECT(sql2, single=True)), 201

    elif request.method == "PATCH":  # UPDATE single activity
        sql = f"UPDATE activities SET title='{title}', address='{address}', reviewAmount='{reviewAmount}', rating='{rating}', description='{description}', city='{city}', state='{state}', url='{url}' WHERE ID={activity_id}"
        sql2 = f"SELECT * FROM activities WHERE ID={activity_id}"
        sql_UPDATE(sql)
        return jsonify(sql_SELECT(sql2, single=True)), 200

    elif request.method == "DELETE":  # DELETE single activity
        sql = f"DELETE FROM activities WHERE ID = '{activity_id}'"
        sql2 = f"SELECT * FROM activities WHERE ID={activity_id}"
        result = sql_SELECT(sql2, single=True)
        sql_DELETE(sql)
        return jsonify(result), 200


@app.route("/reviews/", methods=["GET", "POST"])
@app.route("/reviews/<review_id>", methods=["GET", "DELETE"])
@app.route("/reviews/post/<name>/<review_date>/<review>/<url>", methods=["POST"])
@app.route("/reviews/patch/<review_id>/<name>/<review_date>/<review>/<url>", methods=["PATCH"])
def reviews_API(review_id=None, name=None, review_date=None, review=None, url=None):
    """REST API for reviews data"""
    if request.method == "GET":
        if not review_id:  # READ all user_reviews
            sql = "SELECT * FROM user_reviews"
            return jsonify(sql_SELECT(sql)), 200
        else:  # READ single user_review
            sql = f"SELECT * FROM user_reviews WHERE ID={review_id}"
            return jsonify(sql_SELECT(sql, single=True)), 200

    elif request.method == "POST":  # CREATE single user_review
        sql = "INSERT INTO user_reviews (name, review_date, review, url) VALUES (%s,%s,%s,%s)"
        sql2 = "SELECT * FROM user_reviews ORDER BY ID DESC LIMIT 1;"
        if name is None:
            name = review_date = review = url = "yahhh"
        if url[0] == "A":
            url = "https://www.tripadvisor.com/" + url
        sql_INSERT(sql, (name, review_date, review, url))
        return jsonify(sql_SELECT(sql2, single=True)), 201

    elif request.method == "PATCH":  # UPDATE single user_review
        sql = f"UPDATE user_reviews SET name='{name}', review_date='{review_date}', review='{review}', url='{url}' WHERE ID={review_id}"
        sql2 = f"SELECT * FROM user_reviews WHERE ID={review_id}"
        sql_UPDATE(sql)
        return jsonify(sql_SELECT(sql2, single=True)), 200

    elif request.method == "DELETE":  # DELETE single user_review
        sql = f"DELETE FROM user_reviews WHERE ID = '{review_id}'"
        sql2 = f"SELECT * FROM user_reviews WHERE ID={review_id}"
        result = sql_SELECT(sql2, single=True)
        sql_DELETE(sql)
        return jsonify(result), 200


@app.route("/", methods=["POST", "GET"])
def home():
    """Home Page"""
    supBot = get_support_variables()
    if request.method == "POST" and request.form["support_submit"] != "":
        update_support_variables(supBot)
    return render_template("index.html", supBot=supBot)


@app.route("/owned_activities", methods=["POST", "GET"])
def owned_activities():
    """Page that dynamically displays user saved activities from mysqldb and lets users delete activity from table"""
    supBot = get_support_variables()
    if request.method == "POST":
        print(request.form)
        if request.form["action"] == "delete":  # if user presses delete icon
            requests.delete(f"http://127.0.0.1:5000/activities/{request.form['ID']}")
        elif request.form["action"] == "go_to_activity":  # go straight to activity page
            activity = requests.get(f"http://127.0.0.1:5000/activities/{request.form['ID']}").json()
            return redirect(url_for("activity", city=activity["city"], state=activity["state"], url=activity["url"]))
        elif request.form["support_submit"] != "":
            update_support_variables(supBot)
    activities = requests.get("http://127.0.0.1:5000/activities/").json()
    return render_template("owned_activities.html", database=activities, supBot=supBot)


@app.route("/search", methods=["POST"])
def search():
    """Search Page"""
    if request.method == "POST":
        print("the request form:", request.form)
        return redirect(url_for("results", state=request.form["state"], city=request.form["city"], sort="False"))


@app.route("/results/Page_1/<state>_<city>_<sort>", methods=["POST", "GET"])
def results(state, city, sort):
    """Results Page after selecting State/City"""
    supBot = get_support_variables()
    data = (state, city, sort, "results")
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
                update_support_variables(supBot)
                return result_page(data, supBot)
    return result_page(data, supBot)


@app.route("/results/Page_2/<state>_<city>_<sort>", methods=["POST", "GET"])
def results2(state, city, sort):
    supBot = get_support_variables()
    data = (state, city, sort, "results2")
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
                update_support_variables(supBot)
                return result_page(data, supBot)
    return result_page(data, supBot)


@app.route("/results/Page_3/<state>_<city>_<sort>", methods=["POST", "GET"])
def results3(state, city, sort):
    supBot = get_support_variables()
    data = (state, city, sort, "results3")
    if request.method == "POST":
        print(request.form)
        if request.form["sort_by"] == "True":
            return sort_page(data)
        elif request.form["support_submit"] != "":
            if request.form["support_submit"] == "False":
                return loading_page(data)
            else:
                update_support_variables(supBot)
                return result_page(data, supBot)
    return result_page(data, supBot)


@app.route("/loading/<state>/<city>/<url>")
def loading(url, city, state):
    """Loading page for ad placement"""
    return render_template("loading_screen.html", url=url, city=city, state=state)


@app.route("/activity/<state>/<city>/<url>", methods=["POST", "GET"])
def activity(url, city, state):
    """Activity Page after selecting an activity from the list"""
    mateservice = False
    supBot = get_support_variables()
    new_url = "https://www.tripadvisor.com/" + url
    dct = get_activity_page(new_url, city)  # calls scraper on tripadvisor and grabs all relevant info to put into dct
    if request.method == "POST":
        print(request.form)
        mateservice = True
        images = get_image_from_form()
        if request.form["save_activity"] == "True":  # if user wants to save activity
            title, address, reviewAmount, rating, description, city, state, url = tuple_from_data(dct, city, state, url)
            requests.post(f"http://127.0.0.1:5000/activities/post/{title}/{address}/{reviewAmount}/{rating}/{description}/{city}/{state}/{url}")
        elif request.form["write_review"] == "True":  # if user writes a review
            name = "Anonymous" if request.form["name"] == "" else request.form["name"]
            review_date = "Written " + date.today().strftime("%B %d, %Y")
            requests.post(f"http://127.0.0.1:5000/reviews/post/{name}/{review_date}/{request.form['review']}/{url}")
        elif request.form["support_submit"] != "":
            if request.form["support_submit"] != "False":
                update_support_variables(supBot)
    try:
        calc_ratings(dct)
    except:
        print("couldn't calc_ratings")

    sql = f"SELECT * FROM user_reviews WHERE url = '{new_url}'"  # grabs all user_reviews related to the activity
    update_dct_reviews(dct, sql_SELECT(sql))
    if not mateservice:
        # images = call_teammate_service(dct["title"])
        pass
    images = {"img1": None, "img2": None, "img3": None}  # TEMP CODE
    return render_template("activity.html", dct=dct, city=city, state=state, images=images, supBot=supBot)


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


def result_page(data, supBot):
    """ get Tripadvisor url after sending in state/city to google and getting the results, grabs "Things to do" list
    and return it as a dictionary with activity:url key,value"""
    state, city, sort, result = data
    if supBot["start_support"] == "False":
        url = get_url(state, city)
        dct, lst, lst_title = get_things_to_do(url)
    else:
        dct, lst, lst_title = get_things_to_do(get_url(state, city))
    result = result + ".html"
    if sort == "True":
        dct, lst, lst_title = reverse_data(dct, lst, lst_title)
    return render_template(result, dct=dct, lst=lst, lst_title=lst_title, supBot=supBot)


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~``"""


if __name__ == "__main__":
    app.run(debug=True)


