# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json, pymongo

from scrapy import log
from scrapy.exceptions import DropItem


class TutorialPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    collection_name = 'ffetch_products'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client["mydb"]

    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing data!")
        self.db[self.collection_name].insert_one(dict(item))
        log.msg("Question added to MongoDB database!",
                level=log.DEBUG, spider=spider)
        return item


