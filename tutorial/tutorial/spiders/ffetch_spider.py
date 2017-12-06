import scrapy, pymongo, datetime
from pymongo import MongoClient
from bson import json_util

class QuotesSpider(scrapy.Spider):
    name = "ffetch"

    def start_requests(self):
        url = 'https://www.farfetch.com/uk/designers/women'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse_designers)

    def parse_designers(self, response):
        page = response.url.split("/")[-2]
        filename = 'ffetch-%s-1.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)

        next_page = response.css('ul.list-regular '
                                 'a.open-persistent-tooltip::attr(href)').extract()
        counter = 1
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                counter = counter + 1
                if counter == 4:
                    try:
                        yield scrapy.Request(next_page_url, self.parse_products)

                    except (RuntimeError, TypeError, NameError):
                        pass


    def parse_products(self, response):
        yield {
            'Designer Brand': response.css('h1::text').extract_first(),
            'Number of Prds on sale': response.css('div.listing-bottomBanner '
                                                   'span.underline::text').extract(),
        }
        sales_page = response.css('div.listing-bottomBanner '
                                  'a::attr(href)').extract()

        for links in sales_page:
            if links is not None:
                sales_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(sales_page_url, self.parse_sale_prd_details)
                except (RuntimeError, TypeError, NameError):
                    pass


        next_page = response.css('article.listing-item '
                                 'a.listing-item-content::attr(href)').extract()
        print('LOL')
        print(sales_page)
        # for links in next_page:
        #     if links is not None:
        #         next_page_url = response.urljoin(links)
        #         try:
        #             yield scrapy.Request(next_page_url, self.parse_prd_details)
        #         except (RuntimeError, TypeError, NameError):
        #             pass

    def parse_prd_details(self, response):
        yield {
            'Designer Brand': response.css('h1.detail-brand '
                                           'a::text').extract_first(),
            'Prd Name': response.css('h1.detail-brand '
                                     'span.heading-regular::text').extract(),
            'Prd Price': response.css('div.js-price-without-sale '
                                      'span.listing-price::text').extract_first()[1:],
            'Size': response.css('ul.productDetailModule-selectSize '
                                 'div.dropdown-label-option '
                                 'span.productDetailModule-dropdown-numberItems::text').extract_first(),
        }

    def parse_sale_prd_details(self, response):
        yield {
            'Designer Brand': response.css('h1.detail-brand.detail-name '
                                           'a.generic::text').extract_first(),
            'Prd Name': response.css('h1.detail-brand.detail-name '
                                     'span.heading-regular::text').extract(),
            'Prd sale Price': response.css('div.pdp-price'
                                      'span.listing-sale.js-price::text').extract_first(),
            'Discount': response.css('div.pdp-price '
                                     'div.js-price-on-sale'
                                     'span.discountprice::text').extract_first(),
            'Size': response.css('div.productContainerModule '
                                 'ul.productDetailModule-selectSize '
                                 'li.js-product-selecSize-dropdown '
                                 'span.productDetailModule-dropdown-numberItems::text').extract(),
        }

    # client_connection = MongoClient()
    # data = json_util.loads()