import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class GmailLogHandler(logging.Handler):
    def __init__(self, sender_email, sender_password, recipient_email):
        super().__init__()
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def emit(self, record):
        if record.levelno >= logging.INFO:  # ERROR以上のログのみ送信
            subject = f"Scrapy エラーログ: {record.levelname}"
            message = self.format(record)

            # メール作成
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            try:
                # Gmail の SMTP サーバーに接続して送信
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()  # TLS を有効化
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
                server.quit()
            except Exception as e:
                print(f"メール送信に失敗: {e}")

# Gmail アカウント情報
SENDER_EMAIL = "junya.ishimoto@gmail.com"
SENDER_PASSWORD = "weaz tcfj rhyt domc"  # アプリパスワードを使用
RECIPIENT_EMAIL = "junya.ishimoto@gmail.com"

# ログハンドラーを追加
gmail_handler = GmailLogHandler(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL)
gmail_handler.setLevel(logging.INFO)  # ERROR以上のログのみ送信

# ScrapyのロガーにGmailハンドラーを追加
logging.getLogger("test").addHandler(gmail_handler)
logger = logging.getLogger("test")
logger.info(f"cwd: {os.getcwd()}, __file__: {os.path.abspath(os.path.dirname(__file__))}")


import os
from datetime import datetime

import pytz
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from scrapers.model import models
from notification.line_notifier import LineNotifier

# 定数
# DATABASE_URL = f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'dell_laptop_test.db')}"
# DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(os.getcwd()), 'instance', 'dell_laptop.db')}"
DATABASE_URL = "postgresql://postgres:Ji0101Rh@localhost:5432/dell_laptop"
DEFAULT_PRICE = 0  # 既存価格がない場合のデフォルト値


class SQLAlchemyPipeline:
    def open_spider(self, spider) -> None:
        """データベース接続を初期化し、テーブルを作成する。"""
        self.engine = create_engine(os.environ.get('PRODUCT_DATABASE_URL'))
        # self.engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
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
            # TODO: 既存の設定を上書きしてFalseにしてしまう。一旦定義なしにするが、既存の設定を保持する仕組みにしたい
            # is_line_notification=False
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
            model=item.get('model'),
            old_price=old_price,
            new_price=new_price,
            url=item.get('url')
        )

    def _get_line_notification_status(self, item: dict) -> bool:
        product = self.session.query(models.Products).filter_by(
            order_code=item.get('order_code')
        ).first()
        return product.is_line_notification if product else False
