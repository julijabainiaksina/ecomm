import scrapy, pymongo, datetime
from pymongo import MongoClient
from bson import json_util
from tutorial import db_connection


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
    #     yield{
    #         'designer_name': response.css('div.designers-list-item '
    #                                        'a.open-persistent-tooltip::text').extract()
    #     }

        next_page = response.css('ul.list-regular '
                                 'a.open-persistent-tooltip::attr(href)').extract()
        counter = 1
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                counter = counter + 1
                if counter == 4:
                    try:
                        yield scrapy.Request(next_page_url, self.check_sales)

                    except (RuntimeError, TypeError, NameError):
                        pass


# Get link for each product and call prd_detail func to scrape
    def parse_prd(self, response):
        next_page = response.css('article.listing-item '
                                 'a.listing-item-content::attr(href)').extract()
        # counter = 1
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                # counter = counter + 1
                # if counter == 4:
                try:
                    yield scrapy.Request(next_page_url, self.parse_prd_details)
                except (RuntimeError, TypeError, NameError):
                    pass


# Check if this brand has any products on sale, if so, goes into the sale page and scrape, otherwise scrape
    def check_sales(self, response):
        yield {
            'designer_name': response.css('h1::text').extract_first().strip(),
            'no_product_on_sale': response.css('div.listing-bottomBanner '
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
        time = datetime.datetime.now()
        yield {
            'date': time,
            'designer_name': response.css('h1.detail-brand '
                                          'a::text').extract_first().strip(),
            'product_name': response.css('h1.detail-brand '
                                         'span.heading-regular::text').extract_first().strip(),
            'product_Price': float(response.css('script::text').re(r'unitSalePrice":(.*?)\,"unit')[0]),
            'product_original_price': float(response.css('script::text').re(r'unitPrice":(.*?)\,"unit')[0]),
            'discount': response.css('div.pdp-price '
                                     'span.discountprice.js-discount-label::text').extract_first()[1:],
            'product_availability': response.css('div.js-detail-price '
                                                 'span.size-lowStock::text').extract_first(),
            'product_description': response.css('div.accordion.product-detail '
                                                'p::text').extract_first().strip(),
            'designer_style_id': response.css('script::text').re(r'designerStyleId":(.*?)\"'),
            'ffetch_id': response.css('div.accordion.product-detail '
                                      'p.item-id '
                                      'span::text').extract(),
            'product_type': response.css('script::text').re(r'gender":(.*?)\,"designer')[0].replace("\"", ""),
            'product_stock_volume': int(response.css('script::text').re(r'totalStock":(.*?)\,"stock')[0].replace("\"", "")),
            'product_colour': response.css('script::text').re(r'color":.(.*?)\,"depart')[0].replace("\"", ""),
            'product_category': response.css('script::text').re(r'category":(.*?)\,"sub')[0].replace("\"", "")
        }


