from itemadapter import ItemAdapter
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem

from notification import line_notifier
from model import models


# Constants
DATABASE_URL = 'sqlite:///dell_laptop.db'

# SQLAlchemy-based Pipeline
class SQLAlchemyPipeline:
    def open_spider(self, spider) -> None:
        """Initialize and open database connection, and create tables."""
        self.engine = create_engine(DATABASE_URL)
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def process_item(self, item: dict, spider) -> dict:
        """Process and store an item in the database."""
        try:
            old_price = self._get_price_last_scraped(item=item)
            new_price = item.get('price')

            product = self._create_product(item)
            self.session.merge(product)

            price_history = self._create_price_history(item)
            self.session.add(price_history)

            self.session.commit()

            if new_price != old_price:
                # 実行後に通知を送信
                notifier = line_notifier.LineNotifier()
                notifier.send_notifications(name=item.get('name'),
                                            old_price=old_price,
                                            new_price=new_price,
                                            url=item.get('url')
                                            )
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"pipelines: Error processing item: {e}")
            raise DropItem(f"pipelines: Failed to process item: {e}")

        return item

    def close_spider(self, spider) -> None:
        """Close database session and connection."""
        self.session.close()

    def _create_product(self, item: dict) -> models.Product:
        """Create a Products object from the given item."""
        return models.Product(
            order_code=item.get('order_code'),
            name=item.get('name'),
            model=item.get('model'),
            url=item.get('url'),
            price=item.get('price'),
            discount=item.get('discount'),
            scraped_at=datetime.now()
        )

    def _create_price_history(self, item: dict) -> models.PriceHistory:
        """Create a PriceHistory object from the given item."""
        return models.PriceHistory(
            order_code=item.get('order_code'),
            price=item.get('price'),
            discount=item.get('discount'),
            scraped_at=datetime.now()
        )

    def _get_price_last_scraped(self, item: dict) -> int:
        """Get the last scraped price from the given item."""
        existing_product = self.session.query(models.Product).filter_by(
            order_code=item.get('order_code')).first()

        if existing_product:
            return existing_product.price
        else:
            return 0
