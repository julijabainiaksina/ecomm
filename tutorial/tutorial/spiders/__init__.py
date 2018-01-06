# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy, pymongo, datetime
from pymongo import MongoClient
from bson import json_util
from tutorial.items import FarfetchProductItem, FarfetchDesignerItem

class FarfetchSpider(scrapy.Spider):
    name = "ffetch"

# Define starting urls
    def start_requests(self):
        url = 'https://www.farfetch.com/uk/designers/women'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse_designers)

# Begin with designers and fetch url navigating to each designer
    def parse_designers(self, response):
    # All designer brands
        item = FarfetchDesignerItem()
        time = datetime.datetime.today()

        item['date'] = time,
        item['designer_brands'] = response.css('div.designers-list-item '
                                               'a.open-persistent-tooltip::text').extract()

        yield item

        next_page = response.css('ul.list-regular '
                                 'a.open-persistent-tooltip::attr(href)').extract()
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.check_sales)

                except (RuntimeError, TypeError, NameError):
                    pass


# Get link for each product and call prd_detail func to scrape
    def parse_prd(self, response):
        next_page = response.css('article.listing-item '
                                 'a.listing-item-content::attr(href)').extract()
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.parse_prd_details)
                except (RuntimeError, TypeError, NameError):
                    pass


# Check if this brand has any products on sale, if so, goes into the sale page and scrape, otherwise scrape
    def check_sales(self, response):
        sales_page = response.css('div.listing-bottomBanner '
                                  'a::attr(href)').extract_first()
        # Scrape the sales page if it exist
        if sales_page is not None:
            sales_page_url = response.urljoin(sales_page)
            yield scrapy.Request(sales_page_url, self.parse_prd)


    # Scrape original product page
        next_page = response.css('article.listing-item '
                                 'a.listing-item-content::attr(href)').extract()
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.parse_prd_details)
                except (RuntimeError, TypeError, NameError):
                    pass


    def parse_prd_details(self, response):
        item = FarfetchProductItem()
        time = datetime.datetime.today()

        item['date'] = time,
        item['designer_name'] = response.css('h1.detail-brand '
                                             'a::text').extract_first().strip(),
        item['product_name'] = response.css('h1.detail-brand '
                                            'span.heading-regular::text').extract_first().strip(),
        item['product_Price'] = float(response.css('script::text').re(r'unitSalePrice":(.*?)\,"unit')[0]),
        item['product_original_price'] = float(response.css('script::text').re(r'unitPrice":(.*?)\,"unit')[0]),
        item['discount'] = response.css('div.pdp-price '
                                        'span.discountprice.js-discount-label::text').extract_first()[1:],
        item['product_availability'] = response.css('div.js-detail-price '
                                                    'span.size-lowStock::text').extract_first(),
        item['product_description'] = response.css('div.accordion.product-detail '
                                                    'p::text').extract_first().strip(),
        item['designer_style_id'] = response.css('script::text').re(r'designerStyleId":(.*?)\"'),
        item['ffetch_id'] = response.css('div.accordion.product-detail '
                                         'p.item-id '
                                         'span::text').extract(),
        item['product_type'] = response.css('script::text').re(r'gender":(.*?)\,"designer')[0].replace("\"", ""),
        item['product_stock_volume'] = int(response.css('script::text').re(r'totalStock":(.*?)\,"stock')[0].replace("\"", "")),
        item['product_colour'] = response.css('script::text').re(r'color":.(.*?)\,"depart')[0].replace("\"", ""),
        item['product_category'] = response.css('script::text').re(r'category":(.*?)\,"sub')[0].replace("\"", "")

        yield item


