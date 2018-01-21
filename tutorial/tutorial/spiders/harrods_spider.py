import re
import scrapy, datetime
from scrapy import log
from tutorial.items import ECommerceProductItem


class HarrodsSpider(scrapy.Spider):
    name = "harrods"

    # Define starting urls
    def start_requests(self):
        log.msg('Starting Crawl!', level=log.INFO)
        url = 'https://www.harrods.com/en-gb/designers/online?icid=megamenu_designers'

        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse_designers)

    # Begin with designers and fetch url navigating to each designer
    def parse_designers(self, response):
        log.msg('Begin Parsing Designer Brands!', level=log.INFO)

        # All designer brands
        item = ECommerceProductItem()
        time = datetime.datetime.today()

        item['designer_brands'] = response.css('li.brand-az_list-group '
                                               'ul.brand-az_brands '
                                               'a.brand-az_brand-link::text').extract()
        item['date'] = time

        yield item

        next_page = response.css('li.brand-az_list-group '
                                 'ul.brand-az_brands '
                                 'a.brand-az_brand-link::attr(href)').extract()

        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.parse_category)
                except (RuntimeError, TypeError, NameError):
                    pass

    def parse_category(self, response):
        pages = response.css('li.hrd-link-list_item '
                             'a::attr(href)').extract()
        next_page = set([x for x in pages if "all-" in x])
        if next_page or next_page is None:
            for links in next_page:
                if links is not None:
                    next_page_url = response.urljoin(links)
                    try:
                        yield scrapy.Request(next_page_url, self.parse_prd_pages)
                    except (RuntimeError, TypeError, NameError):
                        pass

    def parse_prd_pages(self, response):
        next_page = set(response.css('div.control_paging-list '
                                     'a.control_paging-item::attr(href)').extract())

        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.parse_products)
                except (RuntimeError, TypeError, NameError):
                    pass


# Check if this brand has any products on sale, if so, goes into the sale page and scrape, otherwise scrape
    def parse_products(self, response):
        # Scrape original product page
        next_page = response.css('div.product-card_info '
                                 'a.product-card_link::attr(href)').extract()
        print next_page
        for links in next_page:
            if links is not None:
                try:
                    yield scrapy.Request(links, self.parse_prd_details)
                except (RuntimeError, TypeError, NameError):
                    pass

    def parse_prd_details(self, response):
        item = ECommerceProductItem()
        time = datetime.datetime.today()
        name = response.css('h1.buying-controls_title '
                            'a '
                            'span::text').extract_first().strip()

        item['date'] = time,
        item['designer_original_name'] = name,
        item['designer_uni_name'] = re.sub(r'[^\w]', '', name).lower(),
        item['product_name'] = response.css('h1.buying-controls_title '
                                            'span.buying-controls_name::text').extract_first().strip(),
        item['product_Price'] = response.css('div.price '
                                             'span.price_amount::text').extract_first(default='Null'),
        item['product_description'] = response.css('div.product-info_content '
                                                   'p::text').extract_first(),
        item['harrods_id'] = response.css('div.buying-controls_prodID::text').extract_first(default='Null'),
        item['product_category'] = response.css('div.product-info_content '
                                                'ul.product-info_list '
                                                'a.product-info_item-link::text').extract()[1]

        yield item


