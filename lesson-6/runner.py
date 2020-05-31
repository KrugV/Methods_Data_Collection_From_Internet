from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson5_practice.gbparse import settings
from lesson5_practice.gbparse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    scr_settings = Settings()
    scr_settings.setmodule(settings)
    process = CrawlerProcess(settings=scr_settings)
    process.crawl(InstagramSpider)
    process.start()

#
