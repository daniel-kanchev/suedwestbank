import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from suedwestbank.items import Article


class SuedwestbankSpider(scrapy.Spider):
    name = 'suedwestbank'
    start_urls = ['https://www.suedwestbank.de/ueber-uns/pressemitteilungen.php']

    def parse(self, response):
        links = response.xpath('//div[@class="mehr"]/a[@class="intern"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//title/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="datum"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="pm_einleitungstext"]//text()').getall() + \
                  response.xpath('//div[@class="pm_text"]//text()').getall()

        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
