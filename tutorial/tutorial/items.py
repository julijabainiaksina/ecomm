# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy

class FarfetchProductItem(scrapy.Item):
    # define the fields for your item here like:
    designer_name = scrapy.Field()

    product_category = scrapy.Field()

    product_original_price = scrapy.Field()

    designer_style_id = scrapy.Field()

    discount = scrapy.Field()

    product_Price = scrapy.Field()

    product_availability = scrapy.Field()

    date = scrapy.Field()

    product_stock_volume = scrapy.Field()

    product_type = scrapy.Field()

    product_description = scrapy.Field()

    product_colour = scrapy.Field()

    ffetch_id = scrapy.Field()

    product_name = scrapy.Field()

    no_product_on_sale = scrapy.Field()

    pass

class FarfetchDesignerItem(scrapy.Item):
    designer_brands = scrapy.Field()
    date = scrapy.Field()