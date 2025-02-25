import os

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from scrapers.dell.spiders.laptop import LaptopSpider

def run_spider():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(this_dir)

    process = CrawlerProcess(get_project_settings())
    process.crawl('laptop')
    # process.crawl(LaptopSpider)
    process.start()