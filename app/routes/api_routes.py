from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request, render_template, Response
from app.model.models import Products, PriceHistory, db

from app.services.price_checker import check_price

bp = Blueprint("api", __name__, url_prefix="/api")

# 定数定義
NOTIFICATION_UPDATED_MSG = "通知設定を更新しました order_code: {}"
PRODUCT_NOT_FOUND_MSG = "商品が見つかりません order_code: {}"


# ヘルパー関数
def fetch_product_by_order_code(order_code: str) -> Products | None:
    """order_code で該当する商品を取得"""
    return db.session.query(Products).filter_by(order_code=order_code).first()


def fetch_price_trends(order_code: str) -> list[dict]:
    """order_code に対応する価格推移を取得"""
    trends = PriceHistory.query.filter_by(order_code=order_code).all()
    return [
        {"date": trend.scraped_at.isoformat() if isinstance(trend.scraped_at, datetime) else trend.scraped_at,
         "price": trend.price}
        for trend in trends
    ]


def fetch_order_code(name: str, model: str) -> str | None:
    """商品の name と model を用いて order_code を取得"""
    product = db.session.query(Products.order_code).filter_by(name=name, model=model).first()
    return product[0] if product else None


# ルート定義
@bp.route("/")
def index():
    """ホーム画面表示"""
    products = Products.query.all()
    return render_template("api.html", products=products, filtered_products=products)


@bp.route("/line_notification_setting")
def line_notification_setting():
    """Line通知設定画面表示"""
    products = Products.query.all()
    return render_template("line_notification_setting.html", products=products)


@bp.route("/check_price", methods=["GET"])
def price_check() -> Response:
    """現在の価格を取得"""
    result = check_price()
    return jsonify(result)


@bp.route("/get_price_trend", methods=["GET", "POST"])
def price_trends() -> Response:
    """価格推移データを取得"""
    data = request.get_json()
    name = data.get("name")
    model = data.get("model")

    order_code = fetch_order_code(name, model)
    if not order_code:
        return jsonify({"error": "商品の注文コードが見つかりません"}), 404

    price_data = fetch_price_trends(order_code)


    return jsonify({"prices": price_data})


@bp.route("/get_notification_setting", methods=["POST"])
def notification_setting() -> Response:
    """通知設定を取得"""
    data = request.get_json()
    order_code = data.get("order_code")
    product = fetch_product_by_order_code(order_code)
    if product:
        return jsonify({"success": True, "toggleValue": product.is_line_notification})
    return jsonify({"success": False, "toggleValue": None})


@bp.route("/update_notification_setting", methods=["POST"])
def update_notification_setting() -> Response:
    """通知設定を更新"""
    data = request.get_json()
    order_code = data.get("order_code")
    is_checked = data.get("is_checked")
    product = fetch_product_by_order_code(order_code)
    if product:
        product.is_line_notification = is_checked
        db.session.commit()
        return jsonify({"message": NOTIFICATION_UPDATED_MSG.format(order_code)}), 200
    return jsonify({"error": PRODUCT_NOT_FOUND_MSG.format(order_code)}), 404
