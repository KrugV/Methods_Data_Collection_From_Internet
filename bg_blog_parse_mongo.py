from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


class BlogParse:
    __base_url = 'https://geekbrains.ru'
    __url = 'https://geekbrains.ru/posts'

    def __init__(self):
        self.posts = []
        self.parse(self.__url)
        client = MongoClient('mongodb://localhost:27017/')
        db = client['new_parse']
        self.collection = db['blog']
        self.save_to_mongo()

    def save_to_mongo(self):
        self.collection.insert_many(self.posts)

    def get_page(self, url: str) -> BeautifulSoup:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        return soup

    def parse(self, url):
        while  url:
            soup = self.get_page(url)
            url = self.get_next_page(soup)
            self.posts.extend(self.get_posts(soup))

    def get_next_page(self, soup: BeautifulSoup) -> str:
        a_tag = soup.find('ul', attrs={'class':'gb__pagination'}).find('a', text='›')
        result = f"{self.__base_url}{a_tag.attrs.get('href')}" if a_tag else None
        return result

    def get_posts(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        result = [{'url':f"{self.__base_url}{itm.attrs.get('href')}", 'title':itm.text} for itm in soup.find_all('a', attrs={'class':'post-item__title'})]
        return result

if __name__ == '__main__':
    parser = BlogParse()
    print(1)

    # client = MongoClient('mongodb://localhost:27017/')
    # print(1)
