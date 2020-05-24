import pandas as pd
import requests
import json
import re
import hashlib
from bs4 import BeautifulSoup as bs
from pprint import pprint


 def get_html(link, headers):
    with requests.session() as s:
        r = s.get(link, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return False


 def get_hh_vacancies(search_queries=[], page_count=1, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}):
    def get_salary_info(link, headers):
        html = get_html(link, headers)
        _min_salary, _max_salary = 0, 0
        if html:
            soup = bs(html, 'html.parser')
            tags = soup.find_all('p', class_='vacancy-salary')
            _salary = re.findall(r'\d+', re.sub(r'\s', '', bs(str(tags[0])).get_text()))
            if len(_salary) == 0:
                pass
            elif len(_salary) == 1:
                _min_salary = _max_salary = _salary[0]
            elif len(_salary) == 2:
                _min_salary, _max_salary = _salary
            else:
                pass
            return _min_salary, _max_salary
        else:
            return _min_salary, _max_salary

    def get_vacancy_info(search_queries, page_count, headers):
        if len(search_queries) > 0:
            _df_list = []
            for search_query in search_queries:
                text = '+'.join(search_query.split(' ')).capitalize()
                for i in range(page_count):
                    link = f'https://hh.ru/search/vacancy?area=1&text={text}&page={i}'
                    html = get_html(link, headers)
                    if html:
                        soup = bs(html, 'html.parser')
                        tags = soup.find_all('a', class_='bloko-link HH-LinkModifier')
                        _vacancies = {
                            'id': [],
                            'name': [],
                            'min_salary': [],
                            'max_salary': [],
                            'link': []
                        }
                        for tag in tags:
                            _id = 'hh' + re.findall(r'(\d+)\??', tag['href'])[0]
                            _name = tag.get_text()
                            _min_salary, _max_salary = get_salary_info(tag['href'], headers)
                            _link = tag['href']
                            _vacancies['id'].append(hashlib.sha256(_id.encode('utf-8')).hexdigest())
                            _vacancies['name'].append(_name)
                            _vacancies['min_salary'].append(_min_salary)
                            _vacancies['max_salary'].append(_max_salary)
                            _vacancies['link'].append(_link)
                        _df_temp = pd.DataFrame(_vacancies)
                    else:
                        return False
                    _df_list.append(_df_temp)
            return pd.concat(_df_list).drop_duplicates(subset='id').reset_index(drop=True)
        else:
            return False

    return get_vacancy_info(search_queries, page_count, headers)


 def get_superjob_vacancies(search_queries=[], page_count=1, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}):

    def get_salary_info(link, headers):
        html = get_html(link, headers)
        _min_salary, _max_salary = 0, 0
        html = get_html(link, headers)
        if html:
            soup = bs(html, 'html.parser')
            tags = soup.find_all('meta', property="og:description")
            _salary = re.findall(r'\d+', re.findall(r'зарплата.+\.', re.sub(r'\s', '', tags[0]['content']))[0])
            if len(_salary) == 0:
                pass
            elif len(_salary) == 1:
                _min_salary = _max_salary = _salary[0]
            elif len(_salary) == 2:
                _min_salary,  _max_salary = _salary
            else:
                pass
            return _min_salary, _max_salary
        else:
            return _min_salary, _max_salary

    def get_vacancy_info(search_queries, page_count, headers):
        if len(search_queries) > 0:
            _df_list = []
            for search_query in search_queries:
                text = '%20'.join(search_query.split(' ')).capitalize()
                for i in range(1, page_count+1):
                    link = f'https://www.superjob.ru/vacancy/search/?geo%5Bt%5D%5B0%5D=4&keywords={text}&page={i}'
                    html = get_html(link, headers)
                    if html:
                        soup = bs(html, 'html.parser')
                        tags = soup.find_all('a', href=True)
                        _vacancies = {
                            'id': [],
                            'name': [],
                            'min_salary': [],
                            'max_salary': [],
                            'link': []
                        }
                        for tag in tags:
                            if len(re.findall(r'<a class="icMQ_ _1QIBo f-test-link-.+', str(tag))) > 0:
                                _id = 'sj' + re.findall(r'(\d+)\.', tag['href'])[0]
                                _name = tag.get_text()
                                _min_salary, _max_salary = get_salary_info('https://www.superjob.ru' + tag['href'], headers)
                                _link = 'https://www.superjob.ru' + tag['href']
                                _vacancies['id'].append(hashlib.sha256(_id.encode('utf-8')).hexdigest())
                                _vacancies['name'].append(_name)
                                _vacancies['min_salary'].append(_min_salary)
                                _vacancies['max_salary'].append(_max_salary)
                                _vacancies['link'].append(_link)
                        _df_temp = pd.DataFrame(_vacancies)
                    else:
                        return False
                    _df_list.append(_df_temp)
            return pd.concat(_df_list).drop_duplicates(subset='id').reset_index(drop=True)
        else:
            return False

    return get_vacancy_info(search_queries, page_count, headers)


 def get_vacancies(search_queries=[], page_count=1, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}):
    try:

        hh = get_hh_vacancies(search_queries, page_count, headers)
        superjob = get_superjob_vacancies(search_queries, page_count, headers)

        if isinstance(hh, pd.DataFrame) and isinstance(superjob, pd.DataFrame):
            hh['min_salary'] = hh['min_salary'].astype(int)
            hh['max_salary'] = hh['max_salary'].astype(int)
            hh['source'] = 'hh'
            superjob['min_salary'] = superjob['min_salary'].astype(int)
            superjob['max_salary'] = superjob['max_salary'].astype(int)
            superjob['source'] = 'superjob'
            return pd.concat([hh, superjob])
        else:
            return 'Something go wrong..'

    except:

        return 'Something go wrong..'

search_queries = ['программист', 'разработчик']
df = get_vacancies(search_queries, page_count=1)