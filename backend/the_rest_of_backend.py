from flask import request
import requests
import json
from PIL import Image
import io
import base64
import ssl
from scraper import get_url_activity


def tuple_from_data(dct, city, state, url):
    """Turn dictionary data into tuple"""
    calc_ratings(dct)
    title = dct["title"]
    reviewAmount = dct["reviewamount"]
    rating = dct["rating"]
    address = dct["address"] if "address" in dct else "Not Available"
    description = dct["description"] if "description" in dct else "Not Available"
    return title, address, reviewAmount, rating, description, city, state, url


def calc_ratings(dct):
    """calculates the rankings based on reviews because tripadvisor rounds too much"""
    try:
        star5 = int(dct["rating5"].replace(",", ""))
        star4 = int(dct["rating4"].replace(",", ""))
        star3 = int(dct["rating3"].replace(",", ""))
        star2 = int(dct["rating2"].replace(",", ""))
        star1 = int(dct["rating1"].replace(",", ""))
        score_total = (star5*5) + (star4*4) + (star3*3) + (star2*2) + star1
        response_total = star5 + star4 + star3 + star2 + star1
        dct.update({"rating": round(score_total/response_total, 2)})
    except:
        print("couldn't calculate ratings")


def reverse_data(dct, lst, lst_title):
    """Reverse all the given data"""
    new_dct = dict(reversed(list(dct.items())))
    lst.reverse()
    lst_title.reverse()
    return new_dct, lst, lst_title


def call_teammate_service(title):
    """Sends a GET request to teammate service and retrieve images"""
    url = f"http://cs-361-image-scraper.herokuapp.com/search?find={title}"
    result = requests.get(url).text
    converted_dct = json.loads(result)
    images = {}
    images["img1"] = get_image(converted_dct["results"][0]["url"], "1")
    images["img2"] = get_image(converted_dct["results"][1]["url"], "2")
    images["img3"] = get_image(converted_dct["results"][2]["url"], "3")
    return images


def get_image(img_url, num):
    """Download the image based on the given url and save it locally to display on page"""
    ssl._create_default_https_context = ssl._create_unverified_context  # DOES NOT CHECK FOR SSL CERT

    path = f"img{num}.jpg"
    response = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'})
    file = open(path, "wb")
    file.write(response.content)
    file.close()

    imm = Image.open(path)
    new_image = imm.resize((190, 190))
    new_image.save(path)
    im = Image.open(path)
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img = base64.b64encode(data.getvalue())
    img = encoded_img.decode('utf-8')
    return img


def get_image_from_form():
    """If page refreshes, grab the current images rather than sending another request for it"""
    images = {}
    images["img1"] = request.form["img1"]
    images["img2"] = request.form["img2"]
    images["img3"] = request.form["img3"]
    return images


def update_dct_reviews(dct, result):
    """If there are local user reviews, use those over TripAdvisor's reviews"""
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
    return


def get_support_variables():
    """Initializes and returns the variables data needed for supportBot"""
    dct = {"supquery": "",
           "user": "",
           "bot_name": "",
           "bot_query": "",
           "url": "",
           "state": "",
           "city": "",
           "toggle": "",
           "start_support": "False"}
    return dct


def update_support_variables(dct):
    """Updates the variables needed for supportBot"""
    url, state, city = get_url_activity(request.form["support_submit"])
    dct["supquery"] = " : " + request.form["support_submit"]
    dct["user"] = "User"
    dct["bot_name"] = "Support Bot"
    dct["bot_query"] = " : Give me a moment while I redirect you to the correct page. Thankyou for using support, have a good day!"
    dct["url"] = url
    dct["state"] = state
    dct["city"] = city
    dct["start_support"] = "True"
    dct["toggle"] = "True"
    return
