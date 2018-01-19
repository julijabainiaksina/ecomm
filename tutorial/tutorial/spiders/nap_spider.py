import re
import scrapy, datetime
from scrapy import log
from tutorial.items import ECommerceProductItem


class NetAPorterSpider(scrapy.Spider):
    name = "nap"
    other_urls = 'https://www.net-a-porter.com/Shop/Sale/AZDesigners'

    # Define starting urls
    def start_requests(self):
        log.msg('Starting Crawl!', level=log.INFO)
        url = 'https://www.net-a-porter.com/gb/en/Shop/AZDesigners?cm_sp=topnav-_-designers-_-topbar'

        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse_designers)

    # Begin with designers and fetch url navigating to each designer
    def parse_designers(self, response):
        log.msg('Begin Parsing Designer Brands!', level=log.INFO)
        log.msg('Response from: %s!' % response.url, level=log.INFO)

        # All designer brands
        item = ECommerceProductItem()
        time = datetime.datetime.today()

        brands = response.css('div.designer_list_col '
                              'li '
                              'a::text').extract()
        brands = [x.strip() for x in brands]

        item['date'] = time
        item['designer_brands'] = brands

        yield item

        next_page = response.css('div.designer_list_col '
                                 'li '
                                 'a::attr(href)').extract()
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.parse_products)
                except (RuntimeError, TypeError, NameError):
                    pass

        if self.other_urls:
            yield scrapy.Request(url=self.other_urls, callback=self.parse_designers)

        # Check if this brand has any products on sale, if so, goes into the sale page and scrape, otherwise scrape
    def parse_products(self, response):
        # Scrape original product page
        next_page = response.css('div.product-image '
                                 'a::attr(href)').extract()
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
        name = response.css('h1 '
                            'span::text').extract_first().strip()

        item['date'] = time,
        item['designer_original_name'] = name,
        item['designer_uni_name'] = re.sub(r'[^\w]', '', name).lower(),
        item['product_name'] = response.css('h2.product-name::text').extract_first().strip(),
        item['product_Price'] = float(response.xpath('//form[@id=$val]/meta/@data-price-full', val='product-form')
                                .extract_first())/100,
        item['product_original_price'] = float(response.xpath('//form[@id=$val]/meta/@data-price', val='product-form')
                                        .extract_first())/100,
        item['discount'] = response.xpath('//form[@id=$val]/meta/@data-discount-percent', val='product-form')\
                           .extract_first(default='0') + "% OFF",
        item['product_availability'] = response.xpath('//form[@id=$val]/meta/@data-sold-out', val='product-form')\
                           .extract_first(default='Null'),
        item['product_description'] = str(
            response.css('div.show-hide-content '
                         'ul.font-list-copy '
                         'li::text').extract()).replace("\\n", "").replace("\\t", "").replace("\\r", "") \
            + str(response.css('div.show-hide-content '
                               'p::text').extract()).replace("\\n", "").replace("\\t", "").replace("\\r", ""),
        item['nap_id'] = response.xpath('//form[@id=$val]/meta/@data-pid', val='product-form')\
                           .extract_first(default='Null'),
        item['product_category'] = response.xpath('//form[@id=$val]/meta/@data-breadcrumb-names', val='product-form')\
                           .extract_first(default='Null')

        yield item


