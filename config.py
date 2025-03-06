import os

class Config:
    """Base configuration (共通設定)"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # アプリケーションのセッションやCSRF対策向け
    DEBUG = False  # デフォルトではデバッグモード無効
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # SQLAlchemyのトラッキングを無効化 (警告を回避)
    SCHEDULER_API_ENABLED = True  # 必要に応じてAPI有効
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')  # APIリクエスト制限 (例)

class DevelopmentConfig(Config):
    """開発環境用設定"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL',
                                             f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'dell_laptop.db')}")
    ENV = 'development'

class TestingConfig(Config):
    """テスト環境用設定"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL',
                                             f"sqlite:///{os.path.join(os.path.dirname(os.getcwd()), 'instance', 'dell_laptop_test.db')}")
    API_RATE_LIMIT = '1000/hour'  # テストでは制限緩和
    ENV = 'testing'

class ProductionConfig(Config):
    """本番環境用設定"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCT_DATABASE_URL',
                                             "postgresql://postgres:Ji0101Rh@localhost:5432/dell_laptop") # PostgreSQL例
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')

# 環境ごとに呼び分けるためのマッピング
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
