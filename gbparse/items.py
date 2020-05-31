# -*- coding: utf-8 -*-

# Define here the models for your scraped items

# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def cleaner_photo(values):
    if values[:2] == '//':
        return f'https:{values}'
    return values


def cleaner_params(item: str):
    result = item.split('">')[-1].split(':')
    key = result[0]
    value = result[-1].split('</span>')[-1].split('</')[0][:-1]
    try:
        value = int(value)
    except ValueError:
        pass

    return {key: value}


def dict_params(items):
    result = {}
    for item in items:
        result.update(item)
    return result


class GbparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AvitoItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    title = scrapy.Field(output_processor=TakeFirst())
    params = scrapy.Field(input_processor=MapCompose(cleaner_params), output_processor=dict_params)
