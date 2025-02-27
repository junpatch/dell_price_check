import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from ..items import LaptopItem
from time import sleep
from urllib.parse import unquote


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
            try:
                # リンクがクリック可能になるまで待機してクリック
                clickable_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//h3[@class='ps-title']/a[contains(@href,'{laptop_model}')]"))
                )
                link_url = clickable_link.get_attribute("href")
                driver.get(link_url)

                # ターゲットデータが表示されるまで待機
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@data-bind='html: salePrice']/span[2]"))
                )
                sleep(1)

                html = driver.page_source
                sel = Selector(text=html)
                loader = ItemLoader(item=LaptopItem(), selector=sel)

                loader.add_xpath('order_code', "//span[@data-bind='text: orderCode']/text()")
                loader.add_xpath('name', "//span[@class='page-title font-weight-md']/text()")
                loader.add_xpath('model', "//div[@class='model-id text-gray-700']/text()")
                loader.add_xpath('price', "//span[@data-bind='html: salePrice']/span[2]/text()")
                loader.add_xpath('discount', "//span[@class='h6 align-middle font-weight-bold savings-price']/text()")
                loader.add_value('url', unquote(driver.current_url))

                yield loader.load_item()

            except Exception as e:
                self.logger.error(f"Error extracting data for model {laptop_model}: {e}")

            finally:
                # 元のページに戻る
                driver.get(self.BASE_URL)
