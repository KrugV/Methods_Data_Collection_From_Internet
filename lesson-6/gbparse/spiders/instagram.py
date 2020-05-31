# -*- coding: utf-8 -*-
from copy import deepcopy
import re
import json
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
import scrapy
from urllib.parse import urlencode
from lesson5_practice.gbparse.items import InstaItem, FollowersItem, FollowingItem

HASHES = {
    'followers': 'c76146de99bb02f6415203be841dd25a',
    'following': 'd04b0a864b4b54837c0d870b0e77e076',
    'media': '58b6785bea111c67129decbe6a448951',
    'media_comments': '97b41c52301f77ce508f55e66d17620e',
    'likes': 'd5d763b1e2acf209d62d22d184488e57',
    'tags': '174a5243287c5f3a7de741089750ab3b',

}

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'gb_scarto'
    inst_pass = 'scartohorse123'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['vol3397','stasdol','akumich']
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    user_data_hash = 'c9100bf9110dd6361671f113dd02e7d6'
    followers_data_hash = HASHES["followers"]
    following_data_hash = HASHES["following"]
    pass

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'password': self.inst_pass},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            #цикл по пользователям, которых парсим
            for pu in self.parse_user:
                yield response.follow(
                    f'/{pu}',   #self.parse_user
                    callback=self.userdata_parse,
                    cb_kwargs={'username': pu} #self.parse_user
                )

    def userdata_parse(self, response: HtmlResponse, username):
        #нам нужно собрать запрос к API
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            "include_reel": True,
            "include_logged_out_extras": False,
            "first": 50,
        }
        #FOLLOWERS
        url_followers = f'{self.graphql_url}query_hash={self.followers_data_hash}&{urlencode(variables)}' #urlencode кодирует наш словарик для корректной передачи в параметры запроса

        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)
                       }
        )
        pass
        #FOLLOWING
        url_following = f'{self.graphql_url}query_hash={self.following_data_hash}&{urlencode(variables)}'  # urlencode кодирует наш словарик для корректной передачи в параметры запроса

        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)
                       }
        )
        pass

    # #нужен ли?
    # def user_data(self, response: HtmlResponse, username, user_id):
    #     j_user_data = json.loads(response.text)

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = j_data.get('data').get('user').get('edge_followed_by').get('page_info').get('end_cursor')

            url_followers = f'{self.graphql_url}query_hash={self.followers_data_hash}&{urlencode(variables)}'  # urlencode кодирует наш словарик для корректной передачи в параметры запроса
            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)
                           }
            )
        for follower in j_data.get('data').get('user').get('edge_followed_by').get('edges'):
            item = FollowersItem(user_name=username,
                                 user_id=user_id,
                                 follower_id=follower['node']['id'],
                                 follower_name=follower['node']['username'],
                                 data=follower['node']
                                 )
            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = j_data.get('data').get('user').get('edge_follow').get('page_info').get('end_cursor')

            url_following = f'{self.graphql_url}query_hash={self.following_data_hash}&{urlencode(variables)}'  # urlencode кодирует наш словарик для корректной передачи в параметры запроса
            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)
                           }
            )
        for following in j_data.get('data').get('user').get('edge_follow').get('edges'):
            item = FollowingItem(user_name=username,
                                 user_id=user_id,
                                 following_id=following['node']['id'],
                                 following_name=following['node']['username'],
                                 data=following['node']
                                 )
            yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

# ниже рабочий вариант реализации коллекции из пользователей, которых обходим
# followers и following сохраняются у них как отдельные списки наряду с именем пользователя и id
# class InstagramSpider(scrapy.Spider):
#     name = 'instagram'
#     allowed_domains = ['instagram.com']
#     start_urls = ['https://instagram.com/']
#     insta_login = 'gb_scarto'
#     inst_pass = 'scartohorse123'
#     inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
#     parse_user = ['vol3397','maximmingalov','dorogakatya']
#     graphql_url = 'https://www.instagram.com/graphql/query/?'
#
#     user_data_hash = 'c9100bf9110dd6361671f113dd02e7d6'
#     followers_data_hash = HASHES["followers"]
#     following_data_hash = HASHES["following"]
#     pass
#
#     def parse(self, response: HtmlResponse):
#         csrf_token = self.fetch_csrf_token(response.text)
#         yield scrapy.FormRequest(
#             self.inst_login_link,
#             method='POST',
#             callback=self.user_parse,
#             formdata={'username': self.insta_login, 'password': self.inst_pass},
#             headers={'X-CSRFToken': csrf_token}
#         )
#
#     def user_parse(self, response: HtmlResponse):
#         j_body = json.loads(response.text)
#         if j_body['authenticated']:
#             #цикл по пользователям, которых парсим
#             for pu in self.parse_user:
#                 yield response.follow(
#                     f'/{pu}',   #self.parse_user
#                     callback=self.userdata_parse,
#                     cb_kwargs={'username': pu} #self.parse_user
#                 )
#
#     def userdata_parse(self, response: HtmlResponse, username):
#         #нам нужно собрать запрос к API
#         user_id = self.fetch_user_id(response.text, username)
#         varibles = {
#             'user_id': user_id,
#             "include_chaining": True,
#             "include_reel": True,
#             "include_logged_out_extras": False,
#         }
#
#         url = f'{self.graphql_url}query_hash={self.user_data_hash}&{urlencode(varibles)}' #urlencode кодирует наш словарик для корректной передачи в параметры запроса
#
#         pass
#         #получили ссылку для запроса к API
#
#         #далее к подписчикам
#         yield response.follow(
#             url,
#             callback=self.user_followers,
#             cb_kwargs={'username': username,
#                        'user_id': user_id}
#         )
#         pass
#
#         # # далее к тем, на кого подписчикам
#         # yield response.follow(
#         #     url,
#         #     callback=self.user_following,
#         #     cb_kwargs={'username': username,
#         #                'user_id': user_id}
#         # )
#         # pass
#
#
#     def user_followers(self, response: HtmlResponse, username, user_id):
#         j_user_data = json.loads(response.text)
#         variables_followers = {
#             'id': user_id,
#             'include_reel': True,
#             # 'fetch_mutual': False,
#             'first': 50,
#             'after': ''
#         }
#         url1 = f'{self.graphql_url}query_hash={self.followers_data_hash}&{urlencode(variables_followers)}'  # urlencode кодирует наш словарик для корректной передачи в параметры запроса
#
#         pass
#         yield response.follow(
#             url1,
#             callback=self.user_following,
#             cb_kwargs={'username': username,
#                        'user_id': user_id,
#                        'j_user_data': j_user_data
#                        }
#         )
#
#     def user_following(self, response: HtmlResponse, username, user_id, j_user_data):
#         j_followers_data = json.loads(response.text)
#         #1
#         page_info = j_followers_data.get('data').get('user').get('edge_followed_by').get('page_info')
#         if page_info.get('has_next_page'):
#             after = j_followers_data.get('data').get('user').get('edge_followed_by').get('page_info').get('end_cursor')
#
#         #2
#         variables_following = {
#             'id': user_id,
#             'include_reel': True,
#             # 'fetch_mutual': False,
#             'first': 50,
#             'after': ''
#         }
#         url2 = f'{self.graphql_url}query_hash={self.following_data_hash}&{urlencode(variables_following)}'  # urlencode кодирует наш словарик для корректной передачи в параметры запроса
#         pass
#         yield response.follow(
#             url2,
#             callback=self.process_Item,
#             cb_kwargs={'username': username,
#                        'user_id': user_id,
#                        'j_user_data': j_user_data,
#                        'j_followers_data': j_followers_data
#                        }
#         )
#
#     def process_Item(self, response: HtmlResponse, j_user_data, username,user_id, j_followers_data):
#         j_following_data = json.loads(response.text)
#         item = ItemLoader(InstaItem(), response)
#
#         item.add_value('user_id', user_id)
#         item.add_value('user_name', username)
#         item.add_value('followers', j_followers_data)
#         item.add_value('following', j_following_data)
#
#         yield item.load_item()
#
#         print(1)
#
#     def fetch_csrf_token(self, text):
#         matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
#         return matched.split(':').pop().replace(r'"', '')
#
#     def fetch_user_id(self, text, username):
#         matched = re.search(
#             '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
#         ).group()
#         return json.loads(matched).get('id')
#