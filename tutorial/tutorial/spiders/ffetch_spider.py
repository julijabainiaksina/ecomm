import scrapy, pymongo, datetime
from pymongo import MongoClient
from bson import json_util
from datetime import datetime, date
from json import dumps

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
        page = response.url.split("/")[-2]
        filename = 'ffetch-%s-1.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)

    # print all designer brands
        yield{
            'Designer Brands': response.css('div.designers-list-item '
                                           'a.open-persistent-tooltip::text').extract()
        }

        next_page = response.css('ul.list-regular '
                                 'a.open-persistent-tooltip::attr(href)').extract()
        # counter = 1
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                # counter = counter + 1
                # if counter == 4:
                try:
                    yield scrapy.Request(next_page_url, self.check_sales)

                except (RuntimeError, TypeError, NameError):
                    pass

# Get link for each product and call prd_detail func to scrape
    def parse_prd(self, response):
        next_page = response.css('article.listing-item '
                                 'a.listing-item-content::attr(href)').extract()
        # print (next_page)
        # counter = 1
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                # counter = counter + 1
                try:
                    yield scrapy.Request(next_page_url, self.parse_prd_details)
                except (RuntimeError, TypeError, NameError):
                    pass
# Check if this brand has any products on sale, if so, goes into the sale page and scrape, otherwise scrape
    def check_sales(self, response):
        yield {
            'Designer Brand': response.css('h1::text').extract_first().strip(),
            'Number of Prds on sale': response.css('div.listing-bottomBanner '
                                                   'span.underline::text').extract_first()
        }
        sales_page = response.css('div.listing-bottomBanner '
                                  'a::attr(href)').extract_first()
        # Scrape the sales page if it exist
        if sales_page is not None:
            sales_page_url = response.urljoin(sales_page)
            yield scrapy.Request(sales_page_url, self.parse_prd)

        # self.parse_prd(response)

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
        yield {
            'Designer_name': response.css('h1.detail-brand '
                                          'a::text').extract_first().strip(),
            'Prd_name': response.css('h1.detail-brand '
                                     'span.heading-regular::text').extract_first().strip(),
            'Prd_Price': response.css('script::text').re(r'unitSalePrice":(.*?)\,"unit'),
            'Prd_original_Price': response.css('script::text').re(r'unitPrice":(.*?)\,"unit'),
            'Discount': response.css('div.pdp-price '
                                     'span.discountprice.js-discount-label::text').extract_first()[1:],
            'Availability': response.css('div.js-detail-price '
                                         'span.size-lowStock::text').extract_first(),
            'Description': response.css('div.accordion.product-detail '
                                        'p::text').extract_first().strip(),
            'Colour': response.css('div.accordion.product-detail '
                                   'span::text').extract_first().strip(),
            'Style_id': response.css('script::text').re(r'designerStyleId":(.*?)\"'),
            'Ffetch_id': response.css('div.accordion.product-detail '
                                      'p.item-id '
                                      'span::text').extract(),
            'Prd_type': response.css('script::text').re(r'gender":(.*?)\,"designer'),
            'stock': response.css('script::text').re(r'totalStock":(.*?)\,"stock'),
            'Colour': response.css('script::text').re(r'color":.(.*?)\,"depart'),
            'Category': response.css('script::text').re(r'category":(.*?)\,"sub'),
            # 'Size': response.css('ul.productDetailModule-selectSize '
            #                      'li.js-product-selecSize-dropdown '
            #                      'span.productDetailModule-dropdown-numberItems::text').extract_first(),
        }

    # client_connection = MongoClient()
    # data = json_util.loads()