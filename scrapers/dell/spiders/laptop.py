import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.keys import Keys
from scrapy.selector import Selector
from ..items import LaptopItem
from time import sleep


class LaptopSpider(scrapy.Spider):
    name = "laptop"
    LAPTOP_LIST = ['14-5440', '14-5445']
    BASE_URL = "https://www.dell.com/ja-jp/shop/dell-laptops/scr/laptops"

    def start_requests(self):
        yield SeleniumRequest(
            url=self.BASE_URL,
            wait_time=3,
            screenshot=False,
            callback=self.parse
        )

    def parse(self, response):
        driver = response.meta['driver']

        for laptop_model in self.LAPTOP_LIST:
            """Extracts and yields laptop details given a model."""
            driver.find_element_by_xpath(f"//h3[@class='ps-title']/a[contains(@href,'{laptop_model}')]").click()
            sleep(3)
            html = driver.page_source
            sel = Selector(text=html)
            loader = ItemLoader(item=LaptopItem(), selector=sel)

            loader.add_xpath('order_code', "//span[@data-bind='text: orderCode']/text()")
            loader.add_xpath('name', "//span[@class='page-title font-weight-md']/text()")
            loader.add_xpath('model', "//div[@class='model-id text-gray-700']/text()")
            loader.add_xpath('price', "//span[@data-bind='html: salePrice']/span[2]/text()")
            loader.add_xpath('discount', "//span[@class='h6 align-middle font-weight-bold savings-price']/text()")

            # URLを追加
            loader.add_value('url', driver.current_url)

            driver.back()
            yield loader.load_item()
