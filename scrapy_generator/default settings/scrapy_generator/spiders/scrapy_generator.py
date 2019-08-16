import scrapy
from scrapy_generator.items import Scrapy_generatorItem


class Scrapy_generatorSpider(scrapy.Spider):
    name = 'scrapy_generator'
    allowed_domains = ['scrapy.generator']
    start_urls = ['https://scrapy-generator']

    def parse(self, response):
        item = Scrapy_generatorItem()
        pass
        yield item
