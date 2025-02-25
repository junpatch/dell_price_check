import requests
import logging
import os

from dotenv import load_dotenv

REQUEST_URL = "https://api.line.me/v2/bot/message/broadcast"

# 環境変数を取得
load_dotenv()

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class LineNotifier:
    def __init__(self):
        self.access_token = os.getenv("LINE_ACCESS_TOKEN")
        self.user_id = os.getenv("LINE_USER_ID")
        self.request_url = REQUEST_URL

        if not self.access_token or not self.user_id:
            raise ValueError("LINE_ACCESS_TOKEN または LINE_USER_ID が設定されていません。")

    def send_notifications(self, old_price, new_price, name, url):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        message = (
            f"🚨価格変動のお知らせ🚨\n"
            f"商品名: {name}\n"
            f"旧価格: ¥{old_price}\n"
            f"新価格: ¥{new_price}\n"
            f"商品リンク: {url}"
        )

        try:
            response=requests.post(
                self.request_url,
                headers=headers,
                json={
                    # "to": self.user_id,  # メッセージを送るユーザーID（またはグループID）
                    "messages": [{"type": "text","text": message}]
                }
            )

            if response.status_code == 200:
                logger.info("通知が正常に送信されました。")
            else:
                logger.error(
                    f"通知の送信中にエラーが発生しました。ステータスコード: {response.status_code}, "
                    f"レスポンス: {response.text}"
                )

        except requests.RequestException as e:
            logger.exception(f"LINE通知の送信中に例外が発生しました: {e}")
