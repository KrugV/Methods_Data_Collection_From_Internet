import requests
import urllib.request

from lxml.html import fromstring

URL = 'https://yandex.ru/search/'
HTML = urllib.request.urlopen(URL)

list_html = HTML.read().decode('utf-8')
parser = fromstring(list_html)

for elem in parser.xpath("//a[contains(@class,'link_cropped_no')]/@href | //a[contains(@class,'organic__url_type_multiline')]/@href"):
    print(elem.text)
    #