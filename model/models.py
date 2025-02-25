from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# テーブル名を定数化
PRODUCTS_TABLE = 'Products'
PRICE_HISTORY_TABLE = 'PriceHistory'


# SQLAlchemy Models
class Product(Base):
    __tablename__ = PRODUCTS_TABLE
    order_code = Column(String, primary_key=True, nullable=False)
    name = Column(String)
    model = Column(String)
    url = Column(String)
    price = Column(Integer)
    discount = Column(Integer)
    scraped_at = Column(DateTime)


class PriceHistory(Base):
    __tablename__ = PRICE_HISTORY_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_code = Column(String, ForeignKey(f"{PRODUCTS_TABLE}.order_code"), nullable=False)
    price = Column(Integer)
    discount = Column(Integer)
    scraped_at = Column(DateTime)