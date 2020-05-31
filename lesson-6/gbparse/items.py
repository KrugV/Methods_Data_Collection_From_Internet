# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


# def cleaner_photo(values):
#     if values[:2] == '//':
#         return f'https:{values}'
#     return values
#
#
# def cleaner_params(item: str):
#     result = item.split('">')[-1].split(':')
#     key = result[0]
#     value = result[-1].split('</span>')[-1].split('</')[0][:-1]
#     try:
#         value = int(value)
#     except ValueError:
#         pass
#
#     return {key: value}


# def dict_params(items):
#     result = {}
#     for item in items:
#         result.update(item)
#     return result

def get_followers_edges(d: dict):
    result = d["data"]["user"]["edge_followed_by"]["edges"]
    list=[]
    for r in result:
        list.append(r["node"])
    return list

def get_following_edges(d: dict):
    result = d["data"]["user"]["edge_follow"]["edges"]
    list=[]
    for r in result:
        list.append(r["node"])
    return list

class InstaItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field(output_processor = TakeFirst())
    user_name = scrapy.Field(output_processor = TakeFirst())
    followers = scrapy.Field(input_processor=MapCompose(get_followers_edges))
    following = scrapy.Field(input_processor=MapCompose(get_following_edges))
    pass

class FollowersItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()
    data = scrapy.Field()

class FollowingItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    following_id = scrapy.Field()
    following_name = scrapy.Field()
    data = scrapy.Field()