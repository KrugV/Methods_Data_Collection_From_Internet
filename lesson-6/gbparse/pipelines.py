# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import scrapy
from scrapy.pipelines.images import ImagesPipeline

mongo_client = MongoClient()

class InstaPipeline(object):
    def process_item(self, item, spider):
        database = mongo_client[spider.name]
        #collection = database['instagram_24_01']
        collection = database[type(item).__name__]
        collection.insert_one(item)
        return item

class PhotoDownloadPipeline(ImagesPipeline):
#необходимо описать 2 метода

    def get_media_requests(self, item, info):
        #проверим, прилетели ли фотки
        if item.get('photos'):
            for img in item.get('photos'):
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        #results хранит список кортежей из двух элементов: 1-й это статус Скачано/Нескачано, 2-й это словарь dict
        #в словаре url - откуда, path - относительный путь к указанной директории для images
        if results:
            item['photos'] = [itm[1] for itm in results] #перебираем фотки, которые качаем. Сохраняем всю структуру dict
        return item

# при сохранении фоток в images имена будут меняться. Свзяано это с ем, что с разных url могли быть дубли, а он хочет сохранять всё