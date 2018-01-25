import datetime
import re

import scrapy

from tutorial.items import ECommerceProductItem


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
        item = ECommerceProductItem()
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
                    yield scrapy.Request(next_page_url, self.parse_prd_pages)
                except (RuntimeError, TypeError, NameError):
                    pass

    def parse_prd_pages(self, response):
        page_num = int(response.css('span.js-lp-pagination-all::text').extract_first())
        i = 1
        next_page_url = []
        while i <= page_num:
            page = "?page=" + str(i)
            url = response.urljoin(page)
            path = url.decode('utf-8')
            next_page_url.append(path)
            i += 1
        for links in next_page_url:
            if links is not None:
                try:
                    yield scrapy.Request(links, self.parse_products)
                except (RuntimeError, TypeError, NameError):
                    pass

# Get link for each product and call prd_detail func to scrape
    def parse_products(self, response):
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
        item = ECommerceProductItem()
        time = datetime.datetime.today()
        name = response.css('h1.detail-brand '
                            'a::text').extract_first().strip()

        item['date'] = time,
        item['designer_original_name'] = name,
        item['designer_uni_name'] = re.sub(r'[^\w]', '', name).lower(),
        item['product_name'] = response.css('h1.detail-brand '
                                            'span.heading-regular::text').extract_first().strip(),
        item['product_price'] = float(response.css('script::text').re(r'unitSalePrice":(.*?)\,"unit')[0]),
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


