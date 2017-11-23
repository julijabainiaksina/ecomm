import scrapy

class QuotesSpider(scrapy.Spider):
    name = "ffetch"

    def start_requests(self):
        # url = 'http://quotes.toscrape.com/'

        url = 'https://www.farfetch.com/uk/designers/women'

        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'ffetch-%s-now.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)

        for ff in response.css("div.designers-list-item"):
            yield {
                'designers': ff.css("ul.list-regular a.open-persistent-tooltip::text").extract(),
            }
        #
        # next_page = response.css('li.next a::attr(href)').extract_first()
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)
        #     yield response.follow(next_page, self.parse)