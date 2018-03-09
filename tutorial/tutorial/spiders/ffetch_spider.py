import datetime
import re
import scrapy
from scrapy_splash import SplashRequest
from tutorial.items import ECommerceProductItem


class FarfetchSpider(scrapy.Spider):
    name = "ffetch"
    other_urls= ['https://www.farfetch.com/uk/shopping/women/shoes-1/items.aspx',
                 'https://www.farfetch.com/uk/shopping/women/accessories-all-1/items.aspx',
                 'https://www.farfetch.com/uk/shopping/women/clothing-1/items.aspx'
                 'https://www.farfetch.com/uk/shopping/women/bags-purses-1/items.aspx',
                 'https://www.farfetch.com/uk/shopping/women/vintage-archive-1/items.aspx',
                 'https://www.farfetch.com/uk/shopping/women/jewellery-1/items.aspx',
                 'https://www.farfetch.com/uk/shopping/women/sale/all/items.aspx']

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

        if self.other_urls:
            for links in self.other_urls:
                yield scrapy.Request(url=links, callback=self.parse_pages, dont_filter=True)

    def parse_pages(self, response):
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
                    yield SplashRequest(links, self.parse_products, dont_filter=True)
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
                        yield scrapy.Request(next_page_url, self.parse_prd_details, dont_filter=True)
                    except (RuntimeError, TypeError, NameError):
                        pass

    def parse_prd_details(self, response):
        # page = response.url.split("/")[-2]
        # filename = 'details-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        item = ECommerceProductItem()
        time = datetime.datetime.today()
        name = str(response.css('h1 '
                                'a::text').extract())

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


