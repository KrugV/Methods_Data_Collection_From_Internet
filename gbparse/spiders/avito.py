# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from gbparse.items import AvitoItem
#


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = [f'https://www.avito.ru/kazan/kvartiry?p={idx}' for idx in range(1, 3)]

    def parse(self, response: HtmlResponse):
        # '/html/body/div[1]/div[2]/div[2]/div[3]/div[4]/div/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[1]/h3/a'
        # urls = response.xpath('//div[contains(@data-marker, "item")]/div[@class="item__line"]//h3/a[@itemprop="url"]')

        for url in response.xpath(
                '//div[contains(@data-marker, "item")]/div[@class="item__line"]//h3/a[@itemprop="url"]'):
            yield response.follow(url, callback=self.avd_parse)

    def avd_parse(self, response: HtmlResponse):
        # item = AvitoItem(
        #     url=response.url,
        #     title=response.xpath('//h1[@class="title-info-title"]/span/text()').extract_first(),
        #     photos=response.xpath('//div[contains(@class, "js-gallery-img-frame")]/@data-url').extract()
        #

        item = ItemLoader(AvitoItem(), response)
        item.add_value('url', response.url)
        item.add_xpath('title', '//h1[@class="title-info-title"]/span/text()')
        item.add_xpath('photos', '//div[contains(@class, "js-gallery-img-frame")]/@data-url')
        item.add_xpath('params', '//div[@class="item-params"]/ul[@class="item-params-list"]/li')
        yield item.load_item()

