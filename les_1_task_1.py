from typing import List
from copy import copy

import requests


class Product:
    name = 'NOT NAME'

    def __init__(self, category, **kwargs):
        self.category = category
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.name


class Category:
    __url = 'https://5ka.ru/api/v2/categories/'
    __name = ''
    __code = ''

    def __init__(self, parent=None, **kwargs):
        self.__parent: Category = parent
        for key, value in kwargs.items():
            if key in ('parent_group_code', 'group_code'):
                self.__code = value
            elif key in ('parent_group_name', 'group_name'):
                self.__name = value
            else:
                setattr(self, f'_{key}', value)

        self.__sub_category = []
        self.__products: List[Product] = []

    @property
    def code(self):
        return self.__code

    @property
    def name(self):
        return self.__name

    @property
    def _sub_categories_urls(self):
        return f'{self.__url}{self.code}' if self.code and not self.__parent else None

    def add_product(self, *product):
        self.__products.extend(product)

    def add_subcategories(self, *sub):
        for itm in sub:
            if isinstance(itm, Category):
                itm.__parent = self
                self.__sub_category.append(itm)

    @classmethod
    def category_url(cls) -> str:
        return cls.__url

    @property
    def products(self):
        result = []
        if self.__sub_category:
            for itm in self.__sub_category:
                result.extend(itm.products)
        result.extend(self.__products)
        return result

    @property
    def sub_category(self):
        return tuple(self.__sub_category)

    def __iter__(self):
        return self.__sub_category.__iter__()

    def __str__(self):
        return f'{self.name} - {self.code}'


class Parser:
    __product_params = {
        'records_per_page': 100,
        'categories': '',
    }
    __product_url = 'https://5ka.ru/api/v2/special_offers/'
    __headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
    }

    def __init__(self):
        self.__categories = self.__get_category(Category.category_url(), True)

        self.__product_parse()

    def __product_parse(self):
        for category in self.__categories:
            for sub in category:
                sub.add_product(*self.get_products(self.__product_url, sub))

    def __get_category(self, url: str, start=False) -> List[Category]:
        categories = []
        response = requests.get(url, headers=self.__headers)
        if response.status_code == 200:
            data = response.json()
            categories.extend([Category(**itm) for itm in data])

        if start:
            for itm in categories:
                itm.add_subcategories(*self.__get_category(itm._sub_categories_urls))

        return categories

    def get_products(self, url: str, category: Category) -> List[Product]:
        result = []
        params = copy(self.__product_params)
        params['categories'] = category.code
        while url:
            response = requests.get(url, headers=self.__headers, params=params)
            data = response.json()
            url = data.get('next')
            params.clear()
            result.extend([Product(category, **itm) for itm in data.get('results')])
        return result

    @property
    def categories(self):
        return tuple(self.__categories)

    @property
    def products(self):
        result = []
        for itm in self.__categories:
            result.extend(itm.products)
        return result


if __name__ == '__main__':
    parser = Parser()
    print(1)
