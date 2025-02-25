import os

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

DEFAULT_SPIDER_NAME = 'laptop'  # スパイダー名を定数として定義


def run_spider(spider_name=DEFAULT_SPIDER_NAME):  # スパイダー名を引数で渡せるように変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 変数をインライン化
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_name)
    process.start()