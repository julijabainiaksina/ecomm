import scrapy
import re

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

        for brands in response.css('div.designers-list-item'):
            yield {
                'Designer Brands': brands.css('ul.list-regular a.open-persistent-tooltip::text').extract_first(),
            }

        next_page = response.css('ul.list-regular a.open-persistent-tooltip::attr(href)').extract()
        counter = 1
        for links in next_page:
            if links is not None and counter == 1:
                next_page_url = response.urljoin(links)
                counter=counter + 1
                yield scrapy.Request(next_page_url, self.parse_products)

    def parse_products(self, response):
        for prd in response.css('article.listing-item a.listing-item-content'):
            yield {
                'Product Name': prd.css('p.listing-item-content-description::text').extract(),
            }

        next_page = response.css('article.listing-item a.listing-item-content::attr(href)').extract()
        for links in next_page:
            if links is not None:
                next_page_url = response.urljoin(links)
                yield scrapy.Request(next_page_url, self.parse_prd_details)

    def parse_prd_details(self, response):
        yield {
            'Designer Brand': response.css('h1.detail-brand a::text').extract_first(),
            'Prd Name': response.css('h1.detail-brand span.heading-regular::text').extract(),
            'Prd Price': response.css('div.js-price-without-sale span.listing-price::text').extract_first()[1:],
            'Size': response.css('li.js-product-selecSize-dropdown span.productDetailModule-dropdown-numberItems::text')
                .extract(),
        }


