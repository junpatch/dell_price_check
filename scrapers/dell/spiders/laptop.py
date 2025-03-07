import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from ..items import LaptopItem
from time import sleep



class LaptopSpider(scrapy.Spider):
    name = "laptop"
    BASE_URL = "https://www.dell.com/ja-jp/shop/dell-laptops/scr/laptops"

    def start_requests(self):
        yield SeleniumRequest(
            url=self.BASE_URL,
            wait_time=5,
            wait_until=EC.element_to_be_clickable(
                (By.XPATH, '//article[@class="variant-stack ps-stack"]/section[@class="ps-show-hide"]/div/h3/a')),
            screenshot=False,
            callback=self.parse
        )

    def parse(self, response):
        driver = response.meta['driver']

        items = self._extract_items_from_articles(driver)
        # parse内からyieldしないと動かない
        for item in items:
            yield item

        total_pages = self._get_total_pages(driver)
        for page_index in range(2, total_pages + 1):
            self._navigate_to_next_page(driver, page_index)
            self._save_screenshot(driver, file_name=f"screenshot_{page_index}.png")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//article[@class="variant-stack ps-stack"]/section[@class="ps-show-hide"]/div/h3/a'))
            )

            items = self._extract_items_from_articles(driver)
            for item in items:
                yield item

    def _extract_items_from_articles(self, driver):
        """現在のページのarticleタグを処理し、アイテムを生成"""
        html = driver.page_source
        sel = Selector(text=html)
        articles = sel.xpath('//article[@class="variant-stack ps-stack"]')
        items = []
        for article in articles:
            try:
                loader = ItemLoader(item=LaptopItem(), selector=article)
                loader.add_xpath('order_code', ".//h3/a/@href")
                loader.add_xpath('name', ".//h3/a/text()")
                loader.add_xpath('model', ".//div[@class='ps-model-number']/span[2]/text()")
                loader.add_xpath('price', ".//span[@class='ps-variant-price-amount']/text()")
                loader.add_xpath('url', ".//h3/a/@href")
                items.append(loader.load_item())
            except Exception as e:
                self.logger.error(f"id={article.attrib.get('id', 'unknown')}読み込み中にエラーが発生しました: {e}")
        return items

    def _navigate_to_next_page(self, driver, page_index):
        try:
            page_input_bar = driver.find_element(By.XPATH, "//input[@id='mypagination-current-page']")
            page_input_bar.send_keys(Keys.BACKSPACE)
            page_input_bar.send_keys(str(page_index))
            page_input_bar.send_keys(Keys.ENTER)

            sleep(3)
        except Exception as e:
            self.logger.error(f"ページ{page_index}に移動中にエラーが発生しました: {e}")

    def _get_total_pages(self, driver):
        """ページ総数を取得"""
        try:
            return int(driver.find_element(By.XPATH, '//span[@class="dds__pagination__page-range-total"]'
                                           ).get_attribute('textContent'))
        except Exception as e:
            self.logger.error(f"総ページ数取得中にエラー: {e}")
            return 1  # エラー時のデフォルト値

    def _save_screenshot(self, driver, file_name="screenshot.png"):
        h = driver.execute_script("return document.body.scrollHeight")
        w = driver.execute_script("return document.body.scrollWidth")
        driver.set_window_size(w, h)
        driver.save_screenshot(file_name)
