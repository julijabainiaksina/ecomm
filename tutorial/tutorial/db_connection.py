import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from datetime import datetime
import json


try:
    Client = MongoClient('localhost', 27017)
    # Create database mydb
    db = Client["mydb"]
    # Create collection
    collection = db["farFetch"]
    print("Successfully connected to database")

except(RuntimeError, TypeError, NameError):
    print("Connection failed")


propertyList = ["no_product_on_sale", "product_category", "product_description", "designer_name", "product_style_id", "product_colour", "Discount", "product_original_price", "product_stock_volume", "date", "product_name", "product_type", "ffetch_id", "availability", "product_price"]
count = 0
mongoList = []
check = "designer_name"
try:
    f = file("../lol.json")
    non_blank_lines = (line.strip() for line in f if line.strip())
    for line in non_blank_lines:
        print("reading")
        s = json.loads(json.dumps(line))
    #     change format
    #     for item in propertyList:
    #         if item in s:
    #             s[item] = s[item][0]
    #             print("convert")
    #                 break
        if check in s:
            count += 1
            mongoList.append(s)
except(RuntimeError, TypeError, NameError):
    print("Reading json file error", count)

    # Insert into db
print(mongoList)
collection.insert_many(mongoList)
# test = [{"author": "Mike",
#                "text": "Another post!",
#                "tags": ["bulk", "insert"]},
#               {"author": "Eliot",
#                "title": "MongoDB is fun",
#                "text": "and pretty easy too!"}]
# collection.insert_many(test)

Client.close()