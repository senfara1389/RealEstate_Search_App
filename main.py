import requests
import json
from bs4 import BeautifulSoup as bs


def get_data():
    realestate_dictionary = {}
    page = 1
    id = 1

    while True:
        url = "https://www.nekretnine.rs/stambeni-objekti/lista/po-stranici/10/stranica/{page}/".format(page=page)

        req = requests.get(url)
        if not req:
            break
        if req.status_code != 200:
            print("Couldn't retrieve data")
            break

        doc = bs(req.text, "html.parser")

        ad_list = doc.find_all("div", {"class": "row offer"})

#       Looking for details on every ad on the page and parsing them into a dictionary
        for ad in ad_list:
            link = ad.find("a")["href"]  # Finding the link to the ad inside the current node
            try:
                ad_url = "https://www.nekretnine.rs{link}".format(link=link)
                detailed_ad_req = requests.get(ad_url)
                if detailed_ad_req.status_code != 200:
                    print("Couldn't retrieve data")
                    continue
            except Exception as e:
                print(e)
            detailed_ad_html = bs(detailed_ad_req.text, "html.parser")
            new_obj = extract_details(detailed_ad_html, ad_url)
            if new_obj is None:
                continue
            realestate_dictionary[id] = new_obj
            id += 1
        page += 1
        to_json(realestate_dictionary)


def extract_details(ad_html, ad_url):
    new_obj = {}

#   Assigning intial values to these keys because we may never encounter actual values
#   inside the webpage, but the object needs to have these properties to fulfill the
#   conditions of the database schema
    new_obj["bathroom_count"] = None
    new_obj["land"] = None
    new_obj["level"] = None
    new_obj["building_year"] = None
    new_obj["registered"] = None
    new_obj["additional_info"] = ""

    try:
    #   Finding the residence type
        detail = ad_html.find("h2", {"class": "detail-seo-subtitle"}).string
        if "stan" or "Garsonjera" in detail:
            new_obj["residence_type"] = "stan"
        elif "kuća" in detail:
            new_obj["residence_type"] = "kuća"
        else:
            return None

    #   Finding if the house is on lease or for sale
        if "Prodaja" in detail:
            new_obj["transaction_type"] = "prodaja"
        elif "Izdavanje" in detail:
            new_obj["transaction_type"] = "izdavanje"

    #   Finding the house's location
        detail = ad_html.find("h3", {"class": "stickyBox__Location"}).string.strip()
        new_obj["location"] = detail

    #   Finding the house's size
        detail = ad_html.find("h4", {"class": "stickyBox__size"}).string.strip()
        # Sometimes the size isn't displayed or is displayed in form of a range so we need
        # to transform that into a singular number
        if "---" in detail:
            detail = float(0)
        elif "-" in detail:
            detail = float(detail.split("-")[1].strip()[:-3])
        else:
            detail = float(detail[:-3])
        new_obj["size"] = detail

    #   Finding the room count
        # Since this node is a list of nodes which have child elements
        # "detail" will represent the element in the list we're currently observing
        # while "info" will represent child elements of "detail"
        detail = ad_html.find("div", {"class": "property__main-details"}).find("ul").find("li")
        detail = detail.next_sibling.next_sibling  # We need to skip one sibling because it's a whitespace
        # Since this node has both a child node and a string, we need to use the
        # "contents" property to extract only the text from the node
        info = detail.find("span").contents[2].string.strip()
        if info == "-":
            info = 1
        else:
            info = float(info)
        new_obj["room_count"] = info

    #   Finding the heating type
        detail = detail.next_sibling.next_sibling
        info = detail.find("span").contents[2].string.strip()
        new_obj["heating_type"] = info

    #   Checking if parking is available
        detail = detail.next_sibling.next_sibling
        info = detail.find("span").contents[2].string.strip()
        if info == "Da":
            info = True
        elif info == "Ne":
            info = False
        new_obj["parking"] = info

    #   Checking the house land size or the apartment level
        detail = detail.next_sibling.next_sibling
        info_name = detail.find("span").find("span").string.strip()
        info = detail.find("span").contents[2].string.strip()
        if "Sprat" in info_name:
            new_obj["level"] = info
        elif "Površina zemljišta" in info_name:
            new_obj["land"] = info

    #   Checking if the house is registered
        detail = detail.next_sibling.next_sibling
        info_name = detail.find("span").find("span").string.strip()
        if "Uknjiženo" in info_name:
            info = detail.find("span").contents[2].string.strip()
            if info == "Da":
                info = True
            elif info == "Ne":
                info = False
            new_obj["registered"] = info

    #   Finding the number of bathrooms, year of building and potentially missing registered info
        detail = ad_html.find("div", {"class": "property__amenities"}).find("ul").contents
        for info in detail:
            if info == "\n":
                continue
            if "Broj kupatila" in str(info):
                count = float(info.find("strong").string.strip())
                new_obj["bathroom_count"] = count
                continue
            if "Godina izgradnje" in str(info):
                year = int(info.find("strong").string.strip())
                new_obj["building_year"] = year
                continue
            if "Uknjiženo" in str(info):
                if new_obj["registered"] is None:
                    regis = info.find("strong").string.strip()
                    if regis == "Da":
                        regis = True
                    elif regis == "Ne":
                        regis = False
                    new_obj["registered"] = regis

    #   Finding the additional info
        # Class that pertains to different house info has the same name so we need to use the sibling method
        # to get to the exact node that holds the addidional info
        detail = ad_html.find("div", {"class": "property__amenities"}).next_sibling.next_sibling
        if detail != None:
            detail = detail.find("h3")
            if "Dodatna opremljenost" in detail:
                info = detail.next_sibling.next_sibling.contents
                for entry in info:
                    if entry == "\n":
                        continue
                    new_obj["additional_info"] = new_obj["additional_info"] + entry.string + "\n"

        return new_obj

    except Exception as e:
        print(e)
        print(ad_url)


def to_json(dic):
    json_object = json.dumps(dic, indent=4)
    with open("data.json", "w") as file:
        file.write(json_object)


get_data()

