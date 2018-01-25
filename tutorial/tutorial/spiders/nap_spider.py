import datetime, json, scrapy, re
from scrapy import log

from tutorial.items import ECommerceProductItem


class NetAPorterSpider(scrapy.Spider):
    name = "nap"
    other_urls = ['https://www.net-a-porter.com/gb/en/d/Shop/Sale/Sport/All_Sportswear?cm_sp=topnav-_-sale-_-sport&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Sale/Lingerie/All?cm_sp=topnav-_-sale-_-lingerie&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Sale/Jewelry_and_Watches/All?cm_sp=topnav-_-sale-_-jewelry&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Sale/Accessories/All?cm_sp=topnav-_-sale-_-accessories&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Sale/Bags/All?cm_sp=topnav-_-sale-_-bags&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Sale/Shoes/All?cm_sp=topnav-_-sale-_-shoes&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Sale/Clothing/All?cm_sp=topnav-_-sale-_-clothing&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Clothing/All?cm_sp=topnav-_-clothing-_-allclothing&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Lingerie/All?cm_sp=topnav-_-lingerie-_-alllingerie&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Jewelry_and_Watches/All?cm_sp=topnav-_-jewelry-_-alljewelry&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Accessories/All?cm_sp=topnav-_-accessories-_-allaccessories&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Bags/All?cm_sp=topnav-_-bags-_-allbags&pn=1&npp=60&image_view=product&dScroll=0',
                  'https://www.net-a-porter.com/gb/en/d/Shop/Shoes/All?cm_sp=topnav-_-shoes-_-allshoes&pn=1&npp=60&image_view=product&dScroll=0']

    # Define starting urls
    def start_requests(self):
        log.msg('Starting Crawl!', level=log.INFO)
        url = 'https://www.net-a-porter.com/gb/en/Shop/AZDesigners?cm_sp=topnav-_-designers-_-seeall...'
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

        if self.other_urls:
            for links in self.other_urls:
                yield scrapy.Request(url=links, callback=self.parse_pages)

    def parse_pages(self, response):
        page_list = response.css('div.pagination-links '
                                 'a::text').extract()
        page_url = response.css('div.pagination-links '
                                'a::attr(href)').extract()
        page_nums = []
        # Convert unicode into num
        for num in page_list:
            page_nums.append(int(num))
        page_num = (max(page_nums))

        s = page_url[0]

        i = 1
        next_page_url = []
        while i <= page_num:
            page_link = s.replace(s[len(s) - 1], str(i))
            url = response.urljoin(page_link)
            path = url.decode('utf-8')
            next_page_url.append(path)
            i += 1

        for links in next_page_url:
            if links is not None:
                try:
                    yield scrapy.Request(links, self.parse_products, dont_filter=True)
                except (RuntimeError, TypeError, NameError):
                    pass


# Check if this brand has any products on sale, if so, goes into the sale page and scrape, otherwise scrape
    def parse_products(self, response):
        # Scrape original product page
        next_page = response.css('div.product-image '
                                 'a::attr(href)').extract()
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                try:
                    yield scrapy.Request(next_page_url, self.parse_prd_details, dont_filter=True)
                except (RuntimeError, TypeError, NameError):
                    pass

    def parse_prd_details(self, response):
        item = ECommerceProductItem()
        time = datetime.datetime.today()
        name = response.css('h1 '
                            'span::text').extract_first().strip()
        # Get price
        checkPrice = response.css('div.total-price nap-price::attr(price)').extract_first()
        if checkPrice:
            a = json.loads(checkPrice)
        else:
            a = json.loads(response.css('nap-price::attr(price)').extract_first())

        # Get product name
        checkName = response.css('h2.product-name::text').extract_first()
        if checkName:
            b = checkName
        else:
            b = response.css('div.details-container '
                             'h2::text').extract_first()

        # get all items
        item['date'] = time,
        item['designer_original_name'] = name,
        item['designer_uni_name'] = re.sub(r'[^\w]', '', name).lower(),
        item['product_name'] = b
        item['product_price'] = a["amount"]/a["divisor"],
        item['product_original_price'] = a["originalAmount"]/a["divisor"],
        item['discount'] = str(a["discountPercent"]) + "% OFF",
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
