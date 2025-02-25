import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

# 定数の定義
PRICE_SUFFIX = '円'


# 価格をパースするユーティリティ関数
def parse_price(price):
    """価格から通貨記号とカンマを除去し、整数型に変換する"""
    return int(price.replace(PRICE_SUFFIX, '').replace(',', ''))


# モデル情報をパースするユーティリティ関数
def parse_model(model):
    """モデル名から 'モデル: ' プレフィックスを除去する"""
    return model.replace('モデル: ', '')


class LaptopItem(scrapy.Item):
    """ノートパソコン情報を表すアイテムクラス"""
    order_code = scrapy.Field(
        output_processor=TakeFirst()  # 最初の値を取得
    )
    name = scrapy.Field(
        output_processor=TakeFirst()  # 最初の値を取得
    )
    model = scrapy.Field(
        input_processor=MapCompose(parse_model),  # モデル名をクリーンアップ
        output_processor=TakeFirst()
    )
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(
        input_processor=MapCompose(parse_price),  # 価格をパース
        output_processor=TakeFirst()
    )
    discount = scrapy.Field(
        input_processor=MapCompose(parse_price),  # 割引額をパース
        output_processor=TakeFirst()
    )
    scraped_at = scrapy.Field(
        output_processor=TakeFirst()
    )
