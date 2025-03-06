from flask import Flask
# from flask_debugtoolbar import DebugToolbarExtension

from app.model.models import db
from app.routes import main_routes, api_routes
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.debug = True  # デバッグモード有効化
    # 設定を読み込み
    app.config.from_object(config[config_name])

    # toolbar = DebugToolbarExtension(app)

    db.init_app(app)

    # ルーティングの登録（Blueprintを利用）
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(api_routes.bp)

    return app
