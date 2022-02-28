import requests
import json
from PIL import Image
import io
import base64
import ssl


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


def reverse_data(dct, lst, lst_title):
    """Reverse all the given data"""
    new_dct = dict(reversed(list(dct.items())))
    lst.reverse()
    lst_title.reverse()
    return new_dct, lst, lst_title


def call_teammate_service(title):
    url = f"http://cs-361-image-scraper.herokuapp.com/search?find={title}"
    #url = "https://i.natgeofe.com/n/46b07b5e-1264-42e1-ae4b-8a021226e2d0/domestic-cat_thumb_square.jpg"
    result = requests.get(url).text
    converted_dct = json.loads(result)
    print(converted_dct)
    img1 = get_image(converted_dct["results"][0]["url"], "1")
    #img1 = get_image(url, "1")
    img2 = get_image(converted_dct["results"][1]["url"], "2")
    img3 = get_image(converted_dct["results"][2]["url"], "3")
    return img1, img2, img3


def get_image(img_url, num):
    ssl._create_default_https_context = ssl._create_unverified_context  # DOES NOT CHECK FOR SSL CERT

    path = f"img{num}.jpg"
    response = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'})
    file = open(path, "wb")
    file.write(response.content)
    file.close()

    #urllib.request.urlretrieve(img_url, f"img{num}_big.jpg")
    imm = Image.open(f"img{num}.jpg")
    new_image = imm.resize((190, 190))
    new_image.save(f'img{num}.jpg')
    im = Image.open(f"img{num}.jpg")
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img = base64.b64encode(data.getvalue())
    img = encoded_img.decode('utf-8')
    return img