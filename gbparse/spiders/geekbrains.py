# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
#

class GeekbrainsSpider(scrapy.Spider):
    name = 'geekbrains'
    allowed_domains = ['geekbrains.ru']
    start_urls = ['https://geekbrains.ru/posts']

    def parse(self, response: HtmlResponse):
        next_page = response.css('ul.gb__pagination li.page a[rel=next]::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        posts = response.css('div.post-items-wrapper div.post-item a.post-item__title::attr(href)').extract()
        for post in posts:
            yield response.follow(post, callback=self.post_parse)

    def post_parse(self, response: HtmlResponse):
        title = response.css('article h1::text').extract_first()
        date = response.css('article time::attr(datetime)').extract_first()

        yield {
            'title': title,
            'date': date,
        }
