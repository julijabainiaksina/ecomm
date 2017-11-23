import scrapy

class FarfetchSpider(scrapy.Spider):
    name = "farfetch"
    start_url = 'https://www.farfetch.com/uk/shopping/women/clothing-1/items.aspx/'
    # start_url = 'https://www.douban.com'

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'farfetch-%s.html' % page
        with open(filename, 'wb') as f:
             f.write(response.body)

        for product in response.css('div.listing-flexbox'):
            yield {
                'Designer': product.css('h5.brand::text').extract_first(),
                'Desc': product.css('p.listing-item-content-description::text').extract_first(),
                'Price': product.css('span.price::text').extract_first()
            }

        # next_page = response.css('li.next a::attr(href)').extract_first()
        # if next_page is not None:
        #     # next_page = response.urljoin(next_page)
        #     # yield scrapy.Request(next_page, callback=self.parse)
        #     yield response.follow(next_page, self.parse)
