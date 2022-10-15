import requests
import json
from yaml import safe_load, YAMLError
import os
import sys

ATTRIBUTES_TO_FIND = ['Energy', 'Fat', 'Carbohydrate', 'Protein', 'Fiber', 'Sugars', 'Sodium']
EDAMAM_ENABLE = 1
USDA_ENABLE = 0


def getTokenUSDA():
    key = "oUTySrnEG332ww7FR2ipLViCaweEdlmHyuA1BEeO"
    return key


def getTokenEDAMAM():
    appID = "102c8bfd"
    key = "99592847788baf7f50ef45b209df4e84"
    return appID, key


def from_EDAMAM_id_to_attributes(EDAMAM_attribute_ids):
    try:
        current_location = os.path.abspath(__file__).split("\\")
    except NameError:
        current_location = sys.executable.split("\\")[0:-3] + ["Django-Auth-And-Perms-main", "main", "sourceCode", "pythonScrapper.py"]

    if len(current_location) > 1:
        current_location = current_location[:-1]
    else:
        try:
            current_location = os.path.abspath(__file__).split("/")[:-1]
        except NameError:
            current_location = sys.executable.split("/")[0:-3] + ["Django-Auth-And-Perms-main", "main", "sourceCode"]

    path = os.path.join(current_location[0], os.sep, *current_location[1:], "data", "edamam_attributes.yml")
    try:
        attr = safe_load(open(path))
    except (YAMLError, FileNotFoundError) as error:
        print("Could not open ", path, "\n", error)
        return []

    output = []
    for i in EDAMAM_attribute_ids:
        output.append(attr["NTRcode_to_attributes"][i])


def from_attributed_to_EDAMAM_id(attributes=ATTRIBUTES_TO_FIND):
    try:
        current_location = os.path.abspath(__file__).split("\\")
    except NameError:
        current_location = sys.executable.split("\\")[0:-3] + ["Django-Auth-And-Perms-main", "main", "sourceCode", "pythonScrapper.py"]

    if len(current_location) > 1:
        current_location = current_location[:-1]
    else:
        try:
            current_location = os.path.abspath(__file__).split("/")[:-1]
        except NameError:
            current_location = sys.executable.split("/")[0:-3] + ["Django-Auth-And-Perms-main", "main", "sourceCode"]

    path = os.path.join(current_location[0], os.sep, *current_location[1:], "data", "edamam_attributes.yml")
    try:
        attr = safe_load(open(path, 'r'))
    except (YAMLError, FileNotFoundError) as error:
        print("Could not open ", path, "\n", error)
        return []

    output = []
    for i in attributes:
        output.append(attr["attributes_to_NTRcode"][i])

    return output


def getUSDA_attribute_ids(attributes=ATTRIBUTES_TO_FIND):
    USDA_attribute_ids = []
    for i in attributes:
        if i == "calories":
            #USDA_attribute_ids.append("1062")
            USDA_attribute_ids.append("1008")
        if i == "fat":
            USDA_attribute_ids.append("204")
            USDA_attribute_ids.append("1292")
            USDA_attribute_ids.append("1293")
        if i == "carbohydrates":
            USDA_attribute_ids.append("1005")
        if i == "protein":
            USDA_attribute_ids.append("1003")
        if i == "fiber":
            USDA_attribute_ids.append("1079")
        if i == "sugar":
            USDA_attribute_ids.append("2000")
        if i == "sodium":
            USDA_attribute_ids.append("307")
            USDA_attribute_ids.append("1093")
    return USDA_attribute_ids


def getValuesFromEDAMAM(foodId, quantity=100):
    output = {}
    # Nutrition's name ids
    nutrition_ids = from_attributed_to_EDAMAM_id()
    # HEADERS option
    my_headers = {"Accept": "application/json",
                  "Content-Type": "application/json"}
    # URLS
    url = "https://api.edamam.com/api/food-database/v2/"
    postURL = url + "nutrients"
    # Token
    appID, key = getTokenEDAMAM()
    # POST options
    postParam = {
        'app_id': appID,
        'app_key': key
    }
    measure = "gram"  # Lowercase
    measure = "http://www.edamam.com/ontologies/edamam.owl#Measure_" + measure

    data = {
        "ingredients": [{"quantity": quantity, "measureURI": measure, "foodId": foodId}]
    }
    # POST request
    postRequest = requests.post(postURL, params=postParam, json=data, headers=my_headers)
    if postRequest.status_code != 200:
        print("EDAMAM: ", "post: ", postRequest.status_code, postURL)
    else:
        # POST Succeeded
        json_parsed = json.loads(postRequest.content)
        nut_values = json_parsed["totalNutrients"]
        for i in range(len(nutrition_ids)):
            try:
                output[ATTRIBUTES_TO_FIND[i]] = str(nut_values[nutrition_ids[i]]["quantity"])
            except KeyError:
                pass
    return output


def getHintsFromEDAMAM(jsonFile):
    if jsonFile["hints"]:
        return [[i["food"]["label"], i["food"]["foodId"], [{"label": k["label"], "weight": k["weight"]} for k in i["measures"]]] for i in jsonFile["hints"]]
    elif jsonFile["parsed"]:
        # Add foodId to json post data
        try:
            single = [jsonFile["parsed"][0]["food"]["label"], jsonFile["parsed"][0]["food"]["foodId"], [{"label": k["label"], "weight": k["weight"]} for k in jsonFile["parsed"][0]["measures"]]]
        except KeyError:
            return []
        return [single]
    else:
        return []


def getDataFromEDAMAM(foodName):
    # https://developer.edamam.com/food-database-api-docs
    output = []
    # HEADERS option
    my_headers = {"Accept": "application/json",
                  "Content-Type": "application/json"}
    # URLS
    url = "https://api.edamam.com/api/food-database/v2/"
    getURL = url + "parser"
    # Token
    appID, key = getTokenEDAMAM()
    # GET options
    nutrition_type = "cooking"
    category = "generic-foods"
    getParams = {
        'app_id': appID,
        'app_key': key,
        'ingr': foodName,
        'nutrition-type=': nutrition_type,
        'category': category
    }
    # POST options
    postParam = {
        'app_id': appID,
        'app_key': key
    }

    # Start here
    # GET Request
    getRequest = requests.get(getURL, params=getParams, headers=my_headers)
    if getRequest.status_code != 200:
        print("EDAMAM: ", "get: ", getRequest.status_code, getURL)
        print(foodName)
    else:
        # GET Succeeded
        json_parsed = json.loads(getRequest.content)
        return getHintsFromEDAMAM(json_parsed)

    return []


def getDataFromUSDA(foodName):
    # https://fdc.nal.usda.gov/api-guide.html#bkmk-1
    output = []
    # Nutrition's name ids
    nutrition_ids = getUSDA_attribute_ids()
    # HEADERS option
    my_headers = {"Accept": "application/json",
                  "Content-Type": "application/json"}
    # URL
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    # Token
    params = {
        'api_key': getTokenUSDA()
    }
    # POST options
    data = {
        "query": foodName,
        "dataType": ["Foundation", "SR Legacy"],
        "pageSize": 25
    }

    # Start here
    postRequest = requests.post(url, params=params, json=data, headers=my_headers)
    if postRequest.status_code != 200:
        print("USDA: ", "post: ", postRequest.status_code, url)
    else:
        # POST Succeeded
        k = 0
        json_parsed = json.loads(postRequest.content)
        for i in range(len(json_parsed["foods"])):
            descript = json_parsed["foods"][i]["description"].lower()
            if descript == foodName:
                k = i
                break
            elif len(descript) > len(foodName):
                if descript[:len(foodName)+1] == foodName+",":
                    k = i
                    break
        print("USDA: ", json_parsed["foods"][k]["description"])
        for i in json_parsed["foods"][k]["foodNutrients"]:
            if str(i["nutrientId"]) in nutrition_ids:
                if i["unitName"] == 'kj':
                    output.append(["calories", str(i["value"] *  0.239006)])
                else:
                    output.append([i["nutrientName"], str(i["value"])])
        return output
    return None


def getFoodValues(foodName):
    foodName = foodName.lower()
    output = []
    if EDAMAM_ENABLE:
        edamam = getDataFromEDAMAM(foodName)
        if edamam:
            print(len(edamam), edamam)
            output.append([edamam, "edamam"])
    if USDA_ENABLE:
        usda = getDataFromUSDA(foodName + " raw")
        if usda:
            print(len(usda), usda)
            output.append([usda, "usda"])
        else:
            usda = getDataFromUSDA(foodName)
            if usda:
                print(len(usda), usda)
                output.append([usda, "usda"])



"""
import re
from bs4 import BeautifulSoup

REGEX = re.compile('[^a-zA-Z]')
def cleanName(element, reg=REGEX):
    if element:
        filtered = reg.sub('', element).lower()
        if filtered:
            if len(filtered) >= 3:
                while True:
                    if len(filtered) >= 5:
                        if filtered[-5:] == "grams":
                            filtered = filtered[0:-5]
                            break
                    if filtered[-2:] == "mg":
                        filtered = filtered[0:-2]
                        break
                    elif filtered[-1] == "g":
                        filtered = filtered[0:-1]
                    break
            return filtered
    return None


def attributesAvailable(filteredElement, attributes=ATTRIBUTES_TO_FIND):
    if filteredElement:
        if filteredElement in attributes:
            return [True, attributes.index(filteredElement)]
    return None


def internetFoodItemSearch(foodName):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
    my_headers = {'User-Agent': user_agent}

    google_url = ["google", "https://www.google.com/search?q=" + foodName]
    bing_url = ["bing", "https://www.cn.bing.com/search?q=" + foodName]
    URLS = [bing_url]

    for url in URLS:
        soup_request = requests.get(url[1], headers=my_headers)
        if soup_request.status_code != 200:
            print(soup_request.status_code)
            continue
        else:
            soup_content = BeautifulSoup(soup_request.content, "html.parser")  # .encode("utf-8")

        if url[0] == "google":
            pass

        if url[0] == "bing":
            # Option One
            # some_content = soup_content.find('div', attrs={'class': 'microNutrientsContainer'})

            # Option Two
            some_content = soup_content.find('div', attrs={'class': 'rwrl rwrl_pri rwrl_padref'})
            if some_content:
                table_option = some_content.find(attrs={'class': "b_vList b_divsec b_bullet"})
                if table_option:
                    for t in table_option:
                        element = t.text.strip()
                        filtered = cleanName(element)
                        if filtered:
                            exists = attributesAvailable(filtered)
                            if exists:
                                print(element)
                    continue
    return None
"""