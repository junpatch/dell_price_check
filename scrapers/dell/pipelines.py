from itemadapter import ItemAdapter
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem

from notification.line_notifier import LineNotifier

Base = declarative_base()

# Constants
DATABASE_URL = 'sqlite:///dell_laptop.db'


# SQLAlchemy Models
class Products(Base):
    __tablename__ = 'Products'
    order_code = Column(String, primary_key=True, nullable=False)
    name = Column(String)
    model = Column(String)
    url = Column(String)
    price = Column(Integer)
    discount = Column(Integer)
    scraped_at = Column(DateTime)

    def __init__(self, order_code, name, model, url, price, discount, scraped_at):
        self.order_code = order_code
        self.name = name
        self.model = model
        self.url = url
        self.price = price
        self.discount = discount
        self.scraped_at = scraped_at


class PriceHistory(Base):
    __tablename__ = 'PriceHistory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_code = Column(String, ForeignKey("Products.order_code"), nullable=False)
    price = Column(Integer)
    discount = Column(Integer)
    scraped_at = Column(DateTime)

    def __init__(self, order_code, price, discount, scraped_at):
        self.order_code = order_code
        self.price = price
        self.discount = discount
        self.scraped_at = scraped_at


# SQLAlchemy-based Pipeline
class SQLAlchemyPipeline:
    def open_spider(self, spider) -> None:
        """Initialize and open database connection, and create tables."""
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def process_item(self, item: dict, spider) -> dict:
        """Process and store an item in the database."""
        product = self._create_product(item)
        self.session.merge(product)

        price_history = self._create_price_history(item)
        self.session.add(price_history)

        old_price = self._get_price_last_scraped(item=item)
        new_price = item.get('price')

        if not new_price == old_price:
            # 実行後に通知を送信
            notifier = LineNotifier()
            notifier.send_notifications(name=item.get('name'),
                                        old_price=old_price,
                                        new_price=new_price,
                                        url=item.get('url')
                                        )

        self.session.commit()
        return item

    def close_spider(self, spider) -> None:
        """Close database session and connection."""
        self.session.close()

    def _create_product(self, item: dict) -> Products:
        """Create a Products object from the given item."""
        return Products(
            order_code=item.get('order_code'),
            name=item.get('name'),
            model=item.get('model'),
            url=item.get('url'),
            price=item.get('price'),
            discount=item.get('discount'),
            scraped_at=datetime.now()
            # price_last_scraped=self._get_price_last_scraped(item=item)
        )

    def _create_price_history(self, item: dict) -> PriceHistory:
        """Create a PriceHistory object from the given item."""
        return PriceHistory(
            order_code=item.get('order_code'),
            price=item.get('price'),
            discount=item.get('discount'),
            scraped_at=datetime.now()
        )

    def _get_price_last_scraped(self, item: dict) -> int:
        """Get the last scraped price from the given item."""
        existing_product = self.session.query(Products).filter_by(
            order_code=item.get('order_code')).first().price

        if existing_product:
            return existing_product
        else:
            return 0
