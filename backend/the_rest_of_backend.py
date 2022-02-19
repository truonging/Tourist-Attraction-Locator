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