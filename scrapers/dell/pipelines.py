import os
from datetime import datetime

import pytz
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import models
from notification.line_notifier import LineNotifier

# 定数
# DATABASE_URL = f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'dell_laptop_test.db')}"
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(os.getcwd()), 'instance', 'dell_laptop.db')}"
DEFAULT_PRICE = 0  # 既存価格がない場合のデフォルト値


class SQLAlchemyPipeline:
    def open_spider(self, spider) -> None:
        """データベース接続を初期化し、テーブルを作成する。"""
        self.engine = create_engine(DATABASE_URL)
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def process_item(self, item: dict, spider) -> dict:
        """アイテムを処理してデータベースに保存する。"""
        try:
            current_time = datetime.now(pytz.timezone('Asia/Tokyo'))
            old_price = self._get_price_last_scraped(item)
            new_price = item.get('price')

            # データベースに商品と価格履歴を保存
            self._save_product_and_history(item, current_time)

            # 価格が変更された場合、かつ通知設定ONの場合、LINE通知を送信
            if new_price != old_price and self._get_line_notification_status(item):
                self._send_notification(item, old_price, new_price)

        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"エラー発生 (Order Code: {item.get('order_code')}): {e}")
            raise DropItem(f"アイテム処理失敗: {e}")
        return item

    def close_spider(self, spider) -> None:
        """データベースセッションと接続を終了する。"""
        self.session.close()

    def _save_product_and_history(self, item: dict, current_time: datetime) -> None:
        """
        データベースに商品データと価格履歴を保存する。
        """
        product = self._create_product(item, current_time)
        self.session.merge(product)

        price_history = self._create_price_history(item, current_time)
        self.session.add(price_history)
        self.session.commit()

    def _create_product(self, item: dict, current_time: datetime) -> models.Products:
        """アイテムから Product オブジェクトを作成する。"""
        return models.Products(
            order_code=item.get('order_code'),
            name=item.get('name'),
            model=item.get('model'),
            url=item.get('url'),
            price=item.get('price'),
            scraped_at=current_time,
            is_line_notification=False
        )

    def _create_price_history(self, item: dict, current_time: datetime) -> models.PriceHistory:
        """アイテムから PriceHistory オブジェクトを作成する。"""
        return models.PriceHistory(
            order_code=item.get('order_code'),
            price=item.get('price'),
            scraped_at=current_time
        )

    def _get_price_last_scraped(self, item: dict) -> int:
        """指定されたアイテムの以前の価格を取得する。"""
        existing_product = self.session.query(models.Products).filter_by(
            order_code=item.get('order_code')
        ).first()
        return existing_product.price if existing_product else DEFAULT_PRICE

    def _send_notification(self, item: dict, old_price: int, new_price: int) -> None:
        """価格変更に関する通知を送信する。"""
        line_notifier_instance = LineNotifier()
        line_notifier_instance.send_notifications(
            name=item.get('name'),
            old_price=old_price,
            new_price=new_price,
            url=item.get('url')
        )

    def _get_line_notification_status(self, item: dict) -> bool:
        product = self.session.query(models.Products).filter_by(
            order_code=item.get('order_code')
        ).first()
        return product.is_line_notification if product else False
