from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson5.gbparse import settings


if __name__ == '__main__':
    scr_settings = Settings()
    scr_settings.setmodule(settings)
    process = CrawlerProcess(settings=scr_settings)
    process.start()


